import sys
import os
import time
from pathlib import Path

# Add Backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

print("=" * 60)
print("FOCUSFLOW BACKEND CONNECTION TESTS")
print("=" * 60)

# -------------------------------------------------------------
# 1. DATABASE CONNECTION TEST
# -------------------------------------------------------------
print("\n[1/2] Testing PostgreSQL Database Connection...")
try:
    from app.authentication.settings.db import database_connection, DB_HOST, DB_NAME, DB_USER, DB_PORT
    print(f"  Target: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    start_time = time.time()
    conn = database_connection()
    elapsed = time.time() - start_time
    
    if conn is None:
        print("  [FAIL] database_connection() returned None. Could not connect to PostgreSQL.")
    else:
        print(f"  [SUCCESS] Connected to PostgreSQL in {elapsed:.2f}s!")
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            db_version = cur.fetchone()
            print(f"  PostgreSQL Version: {db_version['version']}")
            
            # Check expected tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row['table_name'] for row in cur.fetchall()]
            print(f"  Public Tables Found ({len(tables)}): {', '.join(tables) if tables else 'None'}")
            
            expected_tables = [
                "users",
                "pending_users",
                "otp_table",
                "documents",
                "document_chunks",
            ]
            for table in expected_tables:
                if table in tables:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table};")
                    count = cur.fetchone()['count']
                    print(f"    - Table '{table}': EXISTS ({count} rows)")
                else:
                    print(f"    - Table '{table}': MISSING")
        conn.close()
except Exception as e:
    print(f"  [ERROR] Database test exception: {e}")

# -------------------------------------------------------------
# 2. AI CONNECTION TEST
# -------------------------------------------------------------
print("\n[2/2] Testing AI / OpenRouter Connection...")
try:
    from app.ai.chatbot import chat_service
    from app.ai.chatbot.models import ChatMessage
    
    api_key = os.environ.get("OPENAI_API_KEY", "")
    base_url = os.environ.get("OPENAI_BASE_URL", "")
    model = os.environ.get("OPENAI_MODEL", "")
    
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "(not set or short)"
    print(f"  Base URL: {base_url}")
    print(f"  Model   : {model}")
    print(f"  API Key : {masked_key}")
    
    test_messages = [
        ChatMessage(role="user", content="Respond with the single word 'Connected' if you receive this message.")
    ]
    
    print("  Sending test prompt to AI model...")
    start_time = time.time()
    reply = chat_service.get_reply(test_messages)
    elapsed = time.time() - start_time
    
    print(f"  [SUCCESS] AI response received in {elapsed:.2f}s!")
    print(f"  Reply: {reply.strip()}")
except Exception as e:
    print(f"  [ERROR] AI connection exception: {e}")

print("\n" + "=" * 60)
print("TEST RUN COMPLETE")
print("=" * 60)
