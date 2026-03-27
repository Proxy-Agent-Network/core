import asyncio
import time
import logging

logger = logging.getLogger("PAN_SLA_Daemon")

async def run_sla_monitor(redis_client):
    """
    Continuous background daemon that enforces the Vanguard 50 12-minute SLA.
    Sweeps active missions and triggers warnings at 9 mins, and breaches at 12 mins.
    """
    logger.info("⏱️ [SLA_DAEMON] Online. Enforcing 12-Minute Vanguard Protocol...")
    
    while True:
        try:
            now = int(time.time())
            
            # Scan Redis for all currently active missions
            cursor = '0'
            while cursor != 0:
                cursor, keys = await redis_client.scan(cursor=cursor, match="mission:active:*", count=100)
                
                for key in keys:
                    mission = await redis_client.hgetall(key)
                    
                    if not mission or "dispatched_at" not in mission:
                        continue
                        
                    dispatched_at = int(mission["dispatched_at"])
                    delta_seconds = now - dispatched_at
                    delta_minutes = delta_seconds / 60.0
                    
                    current_sla = mission.get("sla_status", "OK")
                    mission_id = key.split(":")[-1]
                    
                    # --- 12 MINUTE BREACH PROTOCOL ---
                    if delta_minutes >= 2.0 and current_sla != "BREACH":
                        logger.critical(f"🚨 [SLA BREACH] Mission {mission_id} at {delta_minutes:.1f}m! Alerting Command.")
                        await redis_client.hset(key, "sla_status", "BREACH")
                        
                        # Broadcast breach to the Ops Hub WebSocket
                        await redis_client.publish(
                            "telemetry_updates", 
                            f'{{"type": "SLA_BREACH", "mission_id": "{mission_id}", "delta": {delta_minutes:.1f}}}'
                        )
                    
                    # --- 9 MINUTE WARNING PROTOCOL ---
                    elif delta_minutes >= 1.0 and delta_minutes < 2.0 and current_sla == "OK":
                        logger.warning(f"⚠️ [SLA WARNING] Mission {mission_id} approaching limit ({delta_minutes:.1f}m).")
                        await redis_client.hset(key, "sla_status", "WARNING")
                        
                        # Broadcast warning to the Ops Hub WebSocket
                        await redis_client.publish(
                            "telemetry_updates", 
                            f'{{"type": "SLA_WARNING", "mission_id": "{mission_id}", "delta": {delta_minutes:.1f}}}'
                        )

            # Sleep for 5 seconds before sweeping again to save CPU cycles
            await asyncio.sleep(5)
            
        except asyncio.CancelledError:
            logger.info("🛑 [SLA_DAEMON] Shutting down...")
            break
        except Exception as e:
            logger.error(f"🛑 [SLA_DAEMON] Unexpected Error: {e}")
            await asyncio.sleep(5)