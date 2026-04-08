import time
import json
import logging
import os
import secrets
from datetime import datetime
import pytz

logger = logging.getLogger("PAN_ReputationEngine")

# PROXY AGENT NETWORK - REPUTATION ENGINE (v2026.1.8)
# "Deterministic Trust & SB 1417 Compliance Math"
# 
# ARCHITECTURAL NOTES:
# 1. Lazy Materialization: The `rep:buyer_score` and `rep:seller_score` keys 
#    are intentionally lagging. They are only updated when `calculate_vts()` 
#    is explicitly invoked. API endpoints and dashboards MUST call `calculate_vts()` 
#    to trigger recalculation rather than reading the materialized keys directly.
# 2. Rater Reliability Recovery: This engine only applies the event-driven downward 
#    friction to `rater_reliability`. The upward recovery path (rewarding honest, 
#    high-volume raters) MUST be handled by a background worker (e.g., reputation_yield_cron) 
#    evaluating the `outbound_downvotes` vs `total_ratings` ratio.
# ----------------------------------------------------

class ReputationEngine:
    
    # Atomic Read-Modify-Write for Rater Reliability (Targets standalone string keys)
    LUA_UPDATE_RATER_REL = """
    local current = tonumber(redis.call('GET', KEYS[1]))
    if current == nil then current = 1.0 end
    local penalty = tonumber(ARGV[1])
    local is_bar_rush = tonumber(ARGV[2])
    if is_bar_rush == 1 then 
        penalty = penalty * 0.5 
    end
    local new_val = math.max(0.1, current - penalty)
    redis.call('SET', KEYS[1], tostring(new_val))
    return tostring(new_val)
    """

    def __init__(self, redis_client, taxonomy_path="apps/backend/src/reputation/schemas/feedback_taxonomy.json"):
        """
        Expects an async Redis client (e.g., from redis.asyncio)
        Dynamically loads weights from the taxonomy Source of Truth.
        """
        self.redis = redis_client
        self.ROLLING_WINDOW_DAYS = 90
        self.BASE_VTS = 100.0
        
        # Load taxonomy from Source of Truth
        self.taxonomy_data = self._load_taxonomy(taxonomy_path)
        self.CATEGORIES = self.taxonomy_data.get("categories", {})
        
        # Flatten override lookups for fast O(1) retrieval, namespaced by direction
        self.OVERRIDES = {"BUYER": {}, "SELLER": {}}
        
        for item in self.taxonomy_data.get("agent_rating_fleet", []):
            if item.get("score_weight_override") is not None:
                self.OVERRIDES["BUYER"][item["label"]] = item["score_weight_override"]
                
        for item in self.taxonomy_data.get("fleet_rating_agent", []):
            if item.get("score_weight_override") is not None:
                self.OVERRIDES["SELLER"][item["label"]] = item["score_weight_override"]

    def _load_taxonomy(self, path: str) -> dict:
        """Loads the taxonomy JSON file safely."""
        try:
            if os.path.exists(path):
                with open(path, "r") as f:
                    return json.load(f)
            else:
                logger.error(f"Taxonomy file not found at {path}. Engine will fail secure.")
                return {}
        except Exception as e:
            logger.error(f"Error loading taxonomy: {e}")
            return {}

    async def submit_feedback(self, task_id: str, submitter_entity_id: str, target_entity_id: str, is_positive: bool, feedback_direction: str, category: str = "", label: str = "", vent_text: str = "") -> dict:
        """
        Ingests feedback, checks idempotency per submitter, atomically updates rater reliability, 
        and logs to the rolling window with directional metadata.
        
        SECURITY NOTE: Task existence, COMPLETED status, and submitter assignment
        (IDOR protection) MUST be validated at the API layer before this method is called.
        Do not call submit_feedback directly without upstream authorization checks.
        """
        # 1. Boundary Validation: Hard reject invalid feedback directions and malformed negative ratings
        feedback_direction = feedback_direction.upper()
        if feedback_direction not in {"BUYER", "SELLER"}:
            logger.error(f"Invalid feedback_direction '{feedback_direction}' for task {task_id} from {submitter_entity_id}")
            return {"status": "error", "reason": "invalid_feedback_direction"}

        if not is_positive and not category:
            logger.error(f"Negative feedback for task {task_id} missing required category.")
            return {"status": "error", "reason": "category_required_for_negative_feedback"}

        # 2. Idempotency Lock
        lock_key = f"pan:feedback:{task_id}:{submitter_entity_id}"
        acquired = await self.redis.set(lock_key, "locked", nx=True, ex=86400)
        
        if not acquired:
            logger.warning(f"Idempotency blocked duplicate feedback for task: {task_id} from {submitter_entity_id}")
            return {"status": "ignored", "reason": "duplicate_submission"}

        # 3. Fetch Submitter's current Rater Reliability Index from standalone namespace key
        rater_rel_key = f"pan:entity:{submitter_entity_id}:rep:rater_reliability"
        rater_rel_raw = await self.redis.get(rater_rel_key)
        rater_reliability = float(rater_rel_raw) if rater_rel_raw else 1.0

        # 4. Fetch True Incident Timestamp for Bar Rush Logic
        current_ts = int(time.time())
        raw_task = await self.redis.hgetall(f"pan:task:{task_id}")
        task_data = {k.decode('utf-8') if isinstance(k, bytes) else k: v.decode('utf-8') if isinstance(v, bytes) else v for k, v in raw_task.items()}
        
        incident_ts_raw = task_data.get("incident_timestamp")
        if incident_ts_raw:
            incident_ts = int(incident_ts_raw)
        else:
            logger.warning(f"⚠️ Task {task_id} missing 'incident_timestamp'. Falling back to submission time. Bar Rush logic may be inaccurate.")
            incident_ts = current_ts

        # 5. Prepare the Feedback Entity (with Cryptographic Entropy)
        feedback_id = f"fb_{current_ts}_{task_id[-6:]}_{secrets.token_hex(4)}"
        safe_vent_text = str(vent_text)[:280] if vent_text else ""

        feedback_data = {
            "id": feedback_id,
            "task_id": task_id,
            "submitter_id": submitter_entity_id,
            "target_id": target_entity_id,
            "is_positive": str(is_positive),
            "direction": feedback_direction,
            "category": category.upper(),
            "label": label,
            "vent_text": safe_vent_text,
            "timestamp": current_ts,
            "incident_timestamp": incident_ts,
            "rater_reliability_weight": rater_reliability
        }

        # 6. Apply Atomic Schema Updates & Sentiment Math (Fully Pipelined)
        async with self.redis.pipeline(transaction=True) as pipe:
            # A. Save feedback hash with extended TTL
            pipe.hset(f"pan:feedback:{feedback_id}", mapping=feedback_data)
            pipe.expire(f"pan:feedback:{feedback_id}", self.ROLLING_WINDOW_DAYS * 86400 * 2)
            
            # B. Add to the Target Entity's 90-day ZSET & Increment Lifetime Counter
            pipe.zadd(f"pan:entity:{target_entity_id}:feedback_history", {feedback_id: current_ts})
            pipe.incr(f"pan:entity:{target_entity_id}:rep:lifetime_ratings")

            # C. Conditional Routing & Math
            if not is_positive:
                cat_data = self.CATEGORIES.get(category.upper(), {})
                if cat_data.get("triggers_ops_review", False):
                    pipe.rpush("pan:ops_review_queue", feedback_id)
                    logger.info(f"🚨 Feedback {feedback_id} flagged for Ops Review (Category: {category.upper()})")

                # Atomically apply Bar Rush protected penalty to Submitter's Rater Reliability
                is_rush = 1 if self._is_bar_rush(incident_ts) else 0
                if is_rush:
                    logger.debug(f"Bar Rush active at incident time {incident_ts}: Atomic rater reliability penalty reduced for {submitter_entity_id}")
                
                # Execute Lua script directly against the standalone namespace key
                pipe.eval(self.LUA_UPDATE_RATER_REL, 1, rater_rel_key, 0.05, is_rush)
                pipe.incr(f"pan:entity:{submitter_entity_id}:rep:outbound_downvotes")
            else:
                # Positive rating simply records the metric without penalty
                pipe.incr(f"pan:entity:{submitter_entity_id}:rep:outbound_upvotes")

            await pipe.execute()

        logger.info(f"✅ Feedback {feedback_id} logged. Target: {target_entity_id} | Positive: {is_positive} | Pool: {feedback_direction}")
        return {"status": "success", "feedback_id": feedback_id}

    def _is_bar_rush(self, timestamp: int) -> bool:
        """
        Checks if the incident occurred between 01:00 and 03:00 in Mesa, AZ (MST)
        on a Friday or Saturday night. (Calendarally Saturday/Sunday mornings).
        """
        az_tz = pytz.timezone('America/Phoenix')
        dt = datetime.fromtimestamp(timestamp, az_tz)
        
        # weekday(): Saturday=5, Sunday=6
        # 1 AM to 3 AM on Saturday/Sunday mornings correspond to the Friday/Saturday night rush
        is_weekend_morning = dt.weekday() in (5, 6)
        is_rush_hour = 1 <= dt.hour < 3
        
        return is_weekend_morning and is_rush_hour

    async def calculate_vts(self, entity_id: str) -> dict:
        """
        Calculates the Vanguard Trust Score (VTS) dynamically based on the 90-day window,
        splitting directional scores (Buyer vs Seller).
        """
        zset_key = f"pan:entity:{entity_id}:feedback_history"
        current_ts = int(time.time())
        cutoff_ts = current_ts - (self.ROLLING_WINDOW_DAYS * 86400)

        # 1. Prune & Archive stale data
        stale_feedback_ids = await self.redis.zrange(zset_key, "-inf", cutoff_ts, byscore=True)
        if stale_feedback_ids:
            async with self.redis.pipeline(transaction=True) as pipe:
                for f_id in stale_feedback_ids:
                    f_id_str = f_id.decode('utf-8') if isinstance(f_id, bytes) else f_id
                    pipe.persist(f"pan:feedback:{f_id_str}")
                    pipe.rpush("pan:archive:feedback_cold_storage", f_id_str)
                pipe.zremrangebyscore(zset_key, "-inf", cutoff_ts)
                await pipe.execute()

        # 2. Fetch the active feedback IDs within the window
        active_feedback_ids = await self.redis.zrange(zset_key, 0, -1)
        active_window_ratings = len(active_feedback_ids)

        if active_feedback_ids:
            async with self.redis.pipeline() as pipe:
                for f_id in active_feedback_ids:
                    f_id_str = f_id.decode('utf-8') if isinstance(f_id, bytes) else f_id
                    pipe.hgetall(f"pan:feedback:{f_id_str}")
                all_raw_data = await pipe.execute()
        else:
            all_raw_data = []

        buyer_penalty = 0.0
        seller_penalty = 0.0

        # 3. Apply the Math, Overrides, Directional Splitting, & Rater Reliability Multipliers
        for raw_data in all_raw_data:
            if not raw_data:
                continue
            
            direction = raw_data.get(b'direction', b'SELLER').decode('utf-8')
            is_positive = (raw_data.get(b'is_positive', b'False').decode('utf-8') == 'True')
            category = raw_data.get(b'category', b'').decode('utf-8')
            label = raw_data.get(b'label', b'').decode('utf-8')
            
            try:
                rater_weight = float(raw_data.get(b'rater_reliability_weight', b'1.0').decode('utf-8'))
            except ValueError:
                rater_weight = 1.0

            penalty_delta = 0.0

            if is_positive:
                # Upward trajectory offset weighted by rater reliability
                penalty_delta = -1.0 * rater_weight
            else:
                cat_data = self.CATEGORIES.get(category, {})
                base_penalty = cat_data.get("score_weight", 10.0) 
                
                # Apply item-level override if it exists within the specific directional pool
                if label in self.OVERRIDES.get(direction, {}):
                    base_penalty = self.OVERRIDES[direction][label]

                penalty_delta = base_penalty * rater_weight

            # Route to respective pool
            if direction == "BUYER":
                buyer_penalty += penalty_delta
            else:
                seller_penalty += penalty_delta

        # 4. Calculate Final Scores (Floor 0, Ceiling 100)
        buyer_vts = max(0.0, min(self.BASE_VTS, self.BASE_VTS - buyer_penalty))
        seller_vts = max(0.0, min(self.BASE_VTS, self.BASE_VTS - seller_penalty))
        
        # 5. Fetch Lifetime Ratings & Check Public Visibility Threshold
        lifetime_raw = await self.redis.get(f"pan:entity:{entity_id}:rep:lifetime_ratings")
        lifetime_ratings = int(lifetime_raw) if lifetime_raw else active_window_ratings
        is_public = lifetime_ratings >= 10
        schema_version = self.taxonomy_data.get("schema_version", "1.0")
        
        # 6. Materialize calculations to Schema
        async with self.redis.pipeline() as pipe:
            pipe.set(f"pan:entity:{entity_id}:rep:seller_score", seller_vts)
            pipe.set(f"pan:entity:{entity_id}:rep:buyer_score", buyer_vts)
            pipe.set(f"pan:entity:{entity_id}:rep:total_ratings", active_window_ratings) # Keep active count for dashboard
            pipe.set(f"pan:entity:{entity_id}:rep:score_version", schema_version)
            await pipe.execute()
        
        logger.info(f"📊 Entity {entity_id} Calculated | Seller VTS: {seller_vts:.2f} | Buyer VTS: {buyer_vts:.2f} | Active Ratings: {active_window_ratings} | Lifetime: {lifetime_ratings}")
        
        return {
            "entity_id": entity_id,
            "seller_vts": seller_vts,
            "buyer_vts": buyer_vts,
            "total_ratings": active_window_ratings,
            "lifetime_ratings": lifetime_ratings,
            "is_public_eligible": is_public
        }