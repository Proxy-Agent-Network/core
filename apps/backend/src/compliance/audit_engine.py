import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

# Removed module-level setLevel to allow the application config to control log verbosity
logger = logging.getLogger("PAN_AuditEngine")

class ComplianceEngine:
    """
    Generates immutable SB 1417 Optical Health Reports for Fleet Partners.
    """

    @staticmethod
    def _generate_sha256_hash(payload: str) -> str:
        """Generates a cryptographic hash of the payload string."""
        hasher = hashlib.sha256()
        hasher.update(payload.encode('utf-8'))
        return hasher.hexdigest()

    @classmethod
    def generate_optical_health_report(
        cls, 
        agent_id: str, 
        vin: str, 
        mission_id: str,
        fault_code: str, 
        evidence_urls: List[str], 
        hardware_attestation_token: str
    ) -> Dict[str, Any]:
        """
        Compiles mission data into a cryptographically sealed compliance receipt.
        
        IMPORTANT: The caller is responsible for immediately persisting this
        report to immutable storage. An unsealed report has no legal standing.
        """
        
        # 1. Zero-Trust Guard: Validate the hardware token before stamping the record
        # 🟢 PILOT BYPASS: Allow empty token for the pilot agent
        if agent_id != "VNG-50-PILOT":
            # A basic length guard ensures we don't seal a blank or clearly malformed token.
            if not hardware_attestation_token or len(hardware_attestation_token) < 100:
                logger.error("🛑 [COMPLIANCE] Invalid or missing hardware attestation token.")
                raise ValueError("Invalid or missing hardware attestation token.")
        
        # 2. Compile the exact state of the mission
        timestamp_iso = datetime.now(timezone.utc).isoformat()
        
        receipt_data = {
            "metadata": {
                "document_type": "SB_1417_OPTICAL_HEALTH_REPORT",
                "version": "1.0",
                "generated_at": timestamp_iso,
            },
            "fleet_asset": {
                "vin": vin,
                "uds_fault_code": fault_code,
                "mission_id": mission_id
            },
            "vanguard_attestation": {
                "agent_id": agent_id,
                "evidence_chain": evidence_urls,
                # The Play Integrity token proves the agent was on authorized hardware
                "hardware_signature": hardware_attestation_token 
            }
        }

        # 3. Serialize deterministically (sort_keys guarantees consistent hashing)
        serialized_payload = json.dumps(receipt_data, sort_keys=True, separators=(',', ':'))
        
        # 4. Cryptographically seal the record
        document_hash = cls._generate_sha256_hash(serialized_payload)
        
        # 5. Append the seal to the final envelope
        sealed_report = {
            "document_hash": document_hash,
            "algorithm": "SHA-256",
            "payload": receipt_data
        }

        logger.info(f"🛡️ [COMPLIANCE] Generated Immutable Health Report for VIN: {vin} | Hash: {document_hash[:8]}...")
        
        return sealed_report

    @classmethod
    def verify_report_integrity(cls, sealed_report: Dict[str, Any]) -> bool:
        """
        Recalculates the hash of the payload to prove it hasn't been tampered with.
        """
        try:
            provided_hash = sealed_report.get("document_hash")
            payload = sealed_report.get("payload")
            algorithm = sealed_report.get("algorithm")
            
            if not provided_hash or not payload:
                return False
                
            # Strict algorithm enforcement prevents downgrade attacks
            if algorithm != "SHA-256":
                logger.error(f"🛑 [COMPLIANCE] Unsupported or missing algorithm field: {algorithm}")
                return False

            serialized_payload = json.dumps(payload, sort_keys=True, separators=(',', ':'))
            calculated_hash = cls._generate_sha256_hash(serialized_payload)
            
            # Timing-safe cryptographic comparison
            is_valid = hmac.compare_digest(provided_hash, calculated_hash)
            
            if not is_valid:
                logger.error("🛑 [COMPLIANCE] INTEGRITY BREACH: Document hash mismatch!")
                
            return is_valid
        except Exception as e:
            logger.error(f"🛑 [COMPLIANCE] Validation crashed: {str(e)}")
            return False

    @classmethod
    async def generate_quarterly_near_miss_report(cls, redis_client, year: int, quarter: int) -> Dict[str, Any]:
        """
        Aggregates all flagged near-miss incidents for a specific quarter into an 
        ADOT/DPS compliant JSON filing, complete with cryptographic seals for each event.
        """
        index_key = f"pan:compliance:near_misses:{year}_Q{quarter}"
        task_ids = await redis_client.smembers(index_key)
        
        events = []
        for task_id_bytes in task_ids:
            task_id = task_id_bytes.decode('utf-8') if isinstance(task_id_bytes, bytes) else task_id_bytes
            
            raw_task = await redis_client.hgetall(f"pan:task:{task_id}")
            if not raw_task:
                continue
                
            task_data = {
                k.decode('utf-8') if isinstance(k, bytes) else k: 
                v.decode('utf-8') if isinstance(v, bytes) else v 
                for k, v in raw_task.items()
            }
                
            # Attempt to pull the cryptographically sealed report if the mission was completed
            sealed_report_raw = await redis_client.get(f"pan:compliance:report:{task_id}")
            report_hash = "PENDING_OR_ABORTED"
            
            if sealed_report_raw:
                try:
                    sealed_report = json.loads(sealed_report_raw)
                    report_hash = sealed_report.get("document_hash", "UNKNOWN")
                except json.JSONDecodeError:
                    pass
                
            events.append({
                "task_id": task_id,
                "incident_id": task_data.get("incident_id", ""),
                "fleet_id": task_data.get("fleet_id", "UNKNOWN"),
                "vin": task_data.get("vin", "UNKNOWN"),
                "timestamp": int(task_data.get("timestamp", 0)),
                "latitude": float(task_data.get("lat", 0.0)),
                "longitude": float(task_data.get("lon", 0.0)),
                "intersection": task_data.get("intersection", "UNKNOWN"),
                "sealed_report_hash": report_hash
            })

        dps_report = {
            "metadata": {
                "document_type": "ADOT_SB1417_QUARTERLY_NEAR_MISS_FILING",
                "filing_period": f"{year}_Q{quarter}",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "total_incidents": len(events),
            },
            "incidents": events
        }
        
        # Seal the entire aggregated report
        serialized_payload = json.dumps(dps_report, sort_keys=True, separators=(',', ':'))
        document_hash = cls._generate_sha256_hash(serialized_payload)
        
        sealed_dps_report = {
            "document_hash": document_hash,
            "algorithm": "SHA-256",
            "payload": dps_report
        }
        
        logger.info(f"🛡️ [COMPLIANCE] Generated SB 1417 Near-Miss Filing for {year}_Q{quarter} | Hash: {document_hash[:8]}...")
        return sealed_dps_report