import firebase_admin
from firebase_admin import credentials, auth
import redis
import secrets
import csv
import os
import time
import logging
import stat
import argparse

# --- CONFIGURATION ---
FIREBASE_CREDENTIALS_PATH = "serviceAccountKey.json"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
OUTPUT_CSV = "vanguard_50_credentials.csv"
VANGUARD_COUNT = 50

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("PAN_Provisioning")

def initialize_systems():
    """Bootstraps the Firebase Admin SDK and Redis connection."""
    if not os.path.exists(FIREBASE_CREDENTIALS_PATH):
        logger.error(f"CRITICAL: Firebase credentials not found at {FIREBASE_CREDENTIALS_PATH}")
        logger.error("Download it from Firebase Console -> Project Settings -> Service Accounts.")
        exit(1)

    try:
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        logger.info("✅ Firebase Admin SDK Initialized.")
    except ValueError:
        # App already initialized
        pass

    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        redis_client.ping()
        logger.info("✅ Redis Cluster Connected.")
        return redis_client
    except redis.ConnectionError:
        logger.error(f"CRITICAL: Could not connect to Redis at {REDIS_HOST}:{REDIS_PORT}")
        exit(1)

def generate_secure_password(length=16):
    """Generates a highly secure, URL-safe password for the initial login."""
    return secrets.token_urlsafe(length)

def reset_vanguard_fleet(redis_client):
    """
    Idempotent recovery path. 
    Resets all existing Vanguard 50 agents back to PENDING_KEY_CEREMONY status.
    """
    logger.info("🔄 Executing manual status reset for Vanguard 50 fleet...")
    reset_count = 0
    
    for i in range(1, VANGUARD_COUNT + 1):
        email = f"vanguard.{i:02d}@pantactical.com"
        uid = redis_client.get(f"agent_email:{email}")
        
        if uid and redis_client.exists(f"agent:{uid}"):
            redis_client.hset(f"agent:{uid}", "status", "PENDING_KEY_CEREMONY")
            # Clear any potentially compromised public keys so the agent can re-bind new hardware
            redis_client.delete(f"pan:agent:{uid}:pubkey")
            logger.info(f"✔️ Reset {email} (UID: {uid}) to PENDING_KEY_CEREMONY.")
            reset_count += 1
        else:
            logger.warning(f"⚠️ Could not locate Redis record for {email}. Skipping.")
            
    logger.info(f"🎯 Reset Complete. {reset_count}/{VANGUARD_COUNT} agents recovered.")
    print("\n[MANUAL OVERRIDE] If an individual agent requires a targeted reset later, use the Redis CLI:")
    print("HSET agent:{uid} status PENDING_KEY_CEREMONY\nDEL pan:agent:{uid}:pubkey\n")

def provision_vanguard_fleet(redis_client):
    """Generates the 50 Firebase accounts and syncs them to Redis."""
    logger.info(f"🚀 Commencing Provisioning for {VANGUARD_COUNT} Vanguard Agents...")
    
    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Callsign", "Email", "Temporary_Password", "Firebase_UID", "Status"])
        
        success_count = 0
        
        for i in range(1, VANGUARD_COUNT + 1):
            callsign = f"Vanguard-{i:02d}"
            email = f"vanguard.{i:02d}@pantactical.com"
            temp_password = generate_secure_password()
            
            try:
                # 1. Create the user in Google Firebase Auth
                user = auth.create_user(
                    email=email,
                    email_verified=True,
                    password=temp_password,
                    display_name=callsign,
                    disabled=False
                )
                
                uid = user.uid
                
                # 2. Inject the approved agent profile directly into Redis
                redis_client.hset(f"agent:{uid}", mapping={
                    "name": f"Operator {i:02d}",
                    "callsign": callsign,
                    "email": email,
                    "phone": "CLASSIFIED",
                    "zip_code": "85201", 
                    "vehicle_class": "STANDARD",
                    "referred_by": "COMMAND",
                    "status": "PENDING_KEY_CEREMONY", 
                    "credential_filename": "COMMAND_PROVISIONED", # 🟢 THE FIX 4: Schema parity
                    "enlisted_at": int(time.time()),
                    "referrals_pending": 0,
                    "referrals_cleared": 0
                })
                
                # Lock the email index to prevent waitlist overlaps
                redis_client.set(f"agent_email:{email}", uid)
                
                # 3. Log to the sealed envelope CSV
                writer.writerow([callsign, email, temp_password, uid, "PROVISIONED"])
                logger.info(f"✔️ Provisioned {callsign} | UID: {uid}")
                
                success_count += 1
                time.sleep(0.1)
                
            except auth.EmailAlreadyExistsError:
                logger.warning(f"⚠️ {email} already exists in Firebase. Skipping.")
                writer.writerow([callsign, email, "[ALREADY EXISTS]", "[FETCH MANUALLY]", "SKIPPED"])
            except Exception as e:
                logger.error(f"❌ Failed to provision {callsign}: {e}")
                writer.writerow([callsign, email, "ERROR", "ERROR", str(e)])

    # 🟢 THE FIX 1: Instantly lock down the file permissions to 600 (owner read/write only)
    try:
        os.chmod(OUTPUT_CSV, stat.S_IRUSR | stat.S_IWUSR)
        logger.info(f"🔒 Applied strict 600 permissions to {OUTPUT_CSV}")
    except Exception as e:
        logger.error(f"⚠️ Failed to lock CSV permissions: {e}")

    logger.info("====================================================")
    logger.info(f"🎯 Provisioning Complete. {success_count}/{VANGUARD_COUNT} Agents Secured.")
    logger.info(f"📄 Credentials written to: {os.path.abspath(OUTPUT_CSV)}")
    logger.info("====================================================")
    
    # 🟢 THE FIX 2: Explicit, unavoidable terminal output for credential destruction
    print("\n" + "!"*60)
    print("CRITICAL SECURITY NOTICE:")
    print(f"Plaintext passwords have been written to {OUTPUT_CSV}.")
    print("You MUST physically destroy or securely delete this CSV file")
    print("immediately after generating the sealed deployment envelopes.")
    print("!"*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vanguard 50 Pilot Fleet Provisioning Tool")
    parser.add_argument("--reset", action="store_true", help="Resets all existing Vanguard 50 accounts to PENDING_KEY_CEREMONY")
    args = parser.parse_args()

    redis_conn = initialize_systems()
    
    if args.reset:
        reset_vanguard_fleet(redis_conn)
    else:
        provision_vanguard_fleet(redis_conn)