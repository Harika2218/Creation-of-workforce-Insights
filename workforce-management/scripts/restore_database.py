"""
AI-Powered Workforce Management Automation System
Database Restore & Validation Utility
--------------------------------------------------
Restores collections and documents from a backup archive to a designated
target database. Rebuilds indexes and performs post-restore document count
validation against the backup manifest.
"""

import os
import sys
import json
import gzip
import tarfile
import hashlib
from typing import Optional, Dict, Any
from bson import json_util

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_client, get_db, ensure_indexes

def restore_database(archive_path: str, target_db_name: str, drop_first: bool = False) -> Dict[str, Any]:
    """
    Restores database from archive_path into target_db_name.
    """
    if not os.path.exists(archive_path):
        raise FileNotFoundError(f"Backup archive not found: {archive_path}")

    # Validate archive SHA-256 if known or verify tar integrity
    print(f"[*] Validating and unpacking archive: {archive_path}")
    temp_extract_dir = os.path.join(os.path.dirname(archive_path), "temp_restore_unpack")
    os.makedirs(temp_extract_dir, exist_ok=True)

    try:
        with tarfile.open(archive_path, "r:gz") as tar:
            tar.extractall(path=temp_extract_dir)

        # Locate unpacked backup folder
        subdirs = [os.path.join(temp_extract_dir, d) for d in os.listdir(temp_extract_dir) if os.path.isdir(os.path.join(temp_extract_dir, d))]
        if not subdirs:
            raise ValueError("No backup folder structure found inside archive.")
        backup_folder = subdirs[0]

        manifest_file = os.path.join(backup_folder, "manifest.json")
        if not os.path.exists(manifest_file):
            raise FileNotFoundError(f"manifest.json missing inside backup archive: {backup_folder}")

        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        print(f"[*] Restoring backup '{manifest['backup_id']}' to database '{target_db_name}'...")
        db = get_db(target_db_name)

        if drop_first:
            print(f"[!] Dropping existing collections in '{target_db_name}' prior to restore...")
            client = get_client()
            client.drop_database(target_db_name)

        restored_counts = {}
        for col_name, expected_count in manifest.get("collections", {}).items():
            col_file = os.path.join(backup_folder, f"{col_name}.json.gz")
            if not os.path.exists(col_file):
                print(f"[WARN] File for collection {col_name} missing from backup, skipping.")
                continue

            with gzip.open(col_file, "rt", encoding="utf-8") as f:
                docs = json_util.loads(f.read())

            if docs:
                db[col_name].insert_many(docs, ordered=False)
            actual_count = db[col_name].count_documents({})
            restored_counts[col_name] = actual_count
            print(f"  [+] Restored {col_name}: {actual_count} / {expected_count} documents")

        # Re-apply indexes to target database
        print("[*] Rebuilding database indexes on restored collections...")
        idx_res = ensure_indexes(db)
        print(f"  [+] Index rebuild status: {idx_res.get('ok', False)}")

        # Validation check
        all_matched = True
        discrepancies = []
        for col_name, expected_count in manifest.get("collections", {}).items():
            actual = restored_counts.get(col_name, 0)
            if actual != expected_count:
                all_matched = False
                discrepancies.append(f"{col_name}: expected {expected_count}, got {actual}")

        result = {
            "status": "SUCCESS" if all_matched else "PARTIAL_MISMATCH",
            "target_database": target_db_name,
            "backup_id": manifest["backup_id"],
            "restored_collections": len(restored_counts),
            "total_documents_restored": sum(restored_counts.values()),
            "expected_documents": manifest["total_documents"],
            "discrepancies": discrepancies,
            "indexes_applied": idx_res.get("ok", False)
        }

        print(f"[*] Restoration completed with status: {result['status']}")
        return result

    finally:
        # Clean up temporary unpack directory
        for root, dirs, files in os.walk(temp_extract_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.exists(temp_extract_dir):
            os.rmdir(temp_extract_dir)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python restore_database.py <archive_path> <target_db_name> [--drop]")
        sys.exit(1)
    archive = sys.argv[1]
    target = sys.argv[2]
    drop = "--drop" in sys.argv
    restore_database(archive, target, drop_first=drop)
