"""
AI-Powered Workforce Management Automation System
Database Backup Utility
--------------------------------------------------
Performs a portable, consistent logical backup of the MongoDB database.
Exports all collections into a compressed archive with metadata manifests
and SHA-256 integrity checksums.
"""

import os
import sys
import json
import gzip
import tarfile
import hashlib
from datetime import datetime, timezone
from bson import json_util

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_db, get_database_name

def backup_database(output_dir: str = "backups", target_db_name: str = None) -> dict:
    """
    Exports all collections in target_db_name to a compressed backup archive.
    """
    db_name = target_db_name or get_database_name()
    db = get_db(db_name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_id = f"backup_{db_name}_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    temp_dir = os.path.join(output_dir, backup_id)
    os.makedirs(temp_dir, exist_ok=True)

    manifest = {
        "backup_id": backup_id,
        "database": db_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "collections": {},
        "total_documents": 0
    }

    collection_names = db.list_collection_names()
    print(f"[*] Starting backup of database '{db_name}' ({len(collection_names)} collections)...")

    for col_name in collection_names:
        col = db[col_name]
        docs = list(col.find({}))
        doc_count = len(docs)
        manifest["collections"][col_name] = doc_count
        manifest["total_documents"] += doc_count

        col_file = os.path.join(temp_dir, f"{col_name}.json.gz")
        with gzip.open(col_file, "wt", encoding="utf-8") as f:
            f.write(json_util.dumps(docs))
        print(f"  [+] Exported {col_name}: {doc_count} documents")

    # Write manifest
    manifest_file = os.path.join(temp_dir, "manifest.json")
    with open(manifest_file, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    # Create tar.gz archive
    archive_path = os.path.join(output_dir, f"{backup_id}.tar.gz")
    with tarfile.open(archive_path, "w:gz") as tar:
        tar.add(temp_dir, arcname=backup_id)

    # Calculate SHA-256
    sha256 = hashlib.sha256()
    with open(archive_path, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    checksum = sha256.hexdigest()
    manifest["sha256_checksum"] = checksum
    manifest["archive_path"] = archive_path
    manifest["archive_size_bytes"] = os.path.getsize(archive_path)

    # Clean up temporary unpacked directory
    for root, dirs, files in os.walk(temp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(temp_dir)

    print(f"[SUCCESS] Backup completed successfully: {archive_path}")
    print(f"  Total Collections: {len(collection_names)}")
    print(f"  Total Documents:   {manifest['total_documents']}")
    print(f"  Archive Size:      {manifest['archive_size_bytes']} bytes")
    print(f"  SHA-256 Checksum:  {checksum}")

    return manifest

if __name__ == "__main__":
    backup_database()
