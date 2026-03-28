import asyncio
import time
import logging

logger = logging.getLogger("PAN_SLA_Daemon")

async def run_sla_monitor(redis_client):
    """
    Continuous background daemon that tracks response times for analytics.
    (Punitive 12-minute SLA has been removed for legal/safety compliance).
    """
    logger.info("⏱️ [METRICS_DAEMON] Online. Tracking Vanguard response times...")
    
    while True:
        try:
            now = int(time.time())
            
            # Scan Redis for all currently active missions
            cursor = '0'
            while cursor != 0:
                cursor, keys = await redis_client.scan(cursor=cursor, match="mission:active:*", count=100)
                
                for key in keys:
                    mission = await redis_client.hgetall(key)
                    
                    if not mission or b"dispatched_at" not in mission and "dispatched_at" not in mission:
                        continue
                    
                    # Handle both byte-strings and standard strings depending on Redis config
                    raw_dispatch = mission.get(b"dispatched_at", mission.get("dispatched_at"))
                    dispatched_at = int(raw_dispatch)
                    
                    delta_seconds = now - dispatched_at
                    delta_minutes = delta_seconds / 60.0
                    
                    raw_sla = mission.get(b"sla_status", mission.get("sla_status", b"OK"))
                    current_sla = raw_sla.decode('utf-8') if isinstance(raw_sla, bytes) else raw_sla
                    
                    mission_id = key.decode('utf-8').split(":")[-1] if isinstance(key, bytes) else key.split(":")[-1]
                    
                    # --- 12 MINUTE DELAY ANALYTICS (NON-PUNITIVE) ---
                    if delta_minutes >= 12.0 and current_sla != "DELAYED":
                        logger.info(f"📊 [METRICS] Mission {mission_id} running long ({delta_minutes:.1f}m). Logging for analytics.")
                        await redis_client.hset(key, "sla_status", "DELAYED")
                        
                        # Broadcast delay to the Ops Hub WebSocket purely for visibility
                        await redis_client.publish(
                            "telemetry_updates", 
                            f'{{"type": "MISSION_DELAYED", "mission_id": "{mission_id}", "delta": {delta_minutes:.1f}}}'
                        )
                    
                    # --- 9 MINUTE WARNING ANALYTICS ---
                    elif delta_minutes >= 9.0 and delta_minutes < 12.0 and current_sla == "OK":
                        logger.info(f"📊 [METRICS] Mission {mission_id} past 9 minutes ({delta_minutes:.1f}m).")
                        await redis_client.hset(key, "sla_status", "WARNING")
                        
                        # Broadcast warning to the Ops Hub WebSocket
                        await redis_client.publish(
                            "telemetry_updates", 
                            f'{{"type": "MISSION_WARNING", "mission_id": "{mission_id}", "delta": {delta_minutes:.1f}}}'
                        )

            # Sleep for 5 seconds before sweeping again to save CPU cycles
            await asyncio.sleep(5)
            
        except asyncio.CancelledError:
            logger.info("🛑 [METRICS_DAEMON] Shutting down...")
            break
        except Exception as e:
            logger.error(f"🛑 [METRICS_DAEMON] Unexpected Error: {e}")
            await asyncio.sleep(5)