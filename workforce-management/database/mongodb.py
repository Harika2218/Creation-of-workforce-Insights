"""
AI-Powered Workforce Management Automation System
MongoDB Connection & Client Manager
--------------------------------------------------
Provides centralized, reusable MongoDB connection management using PyMongo.
Reads configuration from environment variables via python-dotenv.
Supports both local MongoDB and MongoDB Atlas deployments.
"""

import os
import sys
from typing import Optional
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

# Load environment variables from .env file
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DEFAULT_MONGODB_URI = "mongodb://localhost:27017/"
DEFAULT_DATABASE_NAME = "hr_automation"

_client: Optional[MongoClient] = None
_db: Optional[Database] = None

def get_mongodb_uri() -> str:
    """Returns the MongoDB URI configured in environment, or default local URI."""
    return os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI)

def get_database_name() -> str:
    """Returns the database name configured in environment, or default."""
    return os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE_NAME)

def mask_mongodb_uri(uri: str) -> str:
    """Masks credentials in MongoDB connection string for safe logging and status reporting."""
    if "@" in uri:
        prefix, rest = uri.split("@", 1)
        scheme = prefix.split("://")[0] + "://" if "://" in prefix else ""
        return f"{scheme}***:***@{rest}"
    return uri

def get_client(uri: Optional[str] = None, timeout_ms: Optional[int] = None) -> MongoClient:
    """
    Returns a singleton MongoClient instance or a new client if uri is provided.
    Configured with production-ready connection pool and timeouts.
    """
    global _client
    target_uri = uri or get_mongodb_uri()
    
    server_timeout = timeout_ms or int(os.getenv("MONGODB_SERVER_SELECTION_TIMEOUT_MS", "5000"))
    connect_timeout = timeout_ms or int(os.getenv("MONGODB_CONNECT_TIMEOUT_MS", "5000"))
    max_pool_size = int(os.getenv("MONGODB_MAX_POOL_SIZE", "50"))
    min_pool_size = int(os.getenv("MONGODB_MIN_POOL_SIZE", "10"))

    if _client is None or uri is not None:
        try:
            client = MongoClient(
                target_uri,
                serverSelectionTimeoutMS=server_timeout,
                connectTimeoutMS=connect_timeout,
                maxPoolSize=max_pool_size,
                minPoolSize=min_pool_size,
                maxIdleTimeMS=60000,
                retryWrites=True
            )
            # Verify connectivity
            client.admin.command('ping')
            if uri is None:
                _client = client
            return client
        except (ConnectionFailure, ServerSelectionTimeoutError) as err:
            masked = mask_mongodb_uri(target_uri)
            print(f"[ERROR] Failed to connect to MongoDB at {masked}: {err}", file=sys.stderr)
            raise

    return _client

def get_db(db_name: Optional[str] = None) -> Database:
    """
    Returns the target Database instance.
    """
    global _db
    target_db_name = db_name or get_database_name()

    if _db is None or db_name is not None:
        client = get_client()
        db = client[target_db_name]
        if db_name is None:
            _db = db
        return db

    return _db

def check_connection() -> dict:
    """
    Performs a ping check on MongoDB and returns connection status details.
    Guarantees credentials in URI are masked for security.
    """
    uri = get_mongodb_uri()
    masked_uri = mask_mongodb_uri(uri)
    db_name = get_database_name()
    try:
        client = get_client(timeout_ms=3000)
        client.admin.command('ping')
        server_info = client.server_info()
        return {
            "status": "connected",
            "uri": masked_uri,
            "database": db_name,
            "version": server_info.get("version", "unknown"),
            "ok": True
        }
    except Exception as err:
        return {
            "status": "disconnected",
            "uri": masked_uri,
            "database": db_name,
            "error": str(err),
            "ok": False
        }

def ensure_indexes(db: Optional[Database] = None) -> dict:
    """
    Idempotently creates necessary production performance indexes across critical collections.
    Safe against existing index names and duplicate creation.
    """
    target_db = db if db is not None else get_db()
    results = {}
    try:
        from pymongo import IndexModel, ASCENDING, DESCENDING
        from database.seed_database import setup_indexes
        
        # 1. Base collections indexes
        setup_indexes(target_db)
        results["base_collections"] = "verified"

        # 2. Integration Sync History (Phase 10)
        try:
            target_db.integration_sync_history.create_indexes([
                IndexModel([("provider", ASCENDING), ("started_at", DESCENDING)], name="idx_sync_history_provider_time")
            ])
            results["integration_sync_history"] = "indexed"
        except Exception:
            results["integration_sync_history"] = "already_indexed"

        return {"ok": True, "details": results}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def close_connection():
    """Closes global MongoDB client connection safely."""
    global _client, _db
    if _client:
        try:
            _client.close()
        except Exception:
            pass
        _client = None
        _db = None

if __name__ == "__main__":
    status = check_connection()
    print("MongoDB Connection Status:")
    for k, v in status.items():
        print(f"  {k}: {v}")
