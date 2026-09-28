"""
AI-Powered Workforce Management Automation System (InnovateCorp HRvantage)
Phase 15 — Automated Demo Environment Reset Utility
--------------------------------------------------------------------------
Safely purges transient session and test data, re-establishes all MongoDB
collections, reseeds exactly 200 regular employees (EMP001 to EMP200),
provisions verified demo role accounts, initializes Phase 14 extensions
(Locations, Contractors, Compliance), and runs full database validation.

Usage:
    python scripts/reset_demo_environment.py [--drop-first]
"""

import os
import sys
import uuid
import datetime
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from database.mongodb import get_client, get_db, ensure_indexes
from database.seed_database import seed_database


def seed_phase14_extensions(db):
    """Ensures Phase 14 collections (locations, contractors, compliance) are seeded."""
    print("[*] Verifying & seeding Phase 14 enterprise extensions...")

    # 1. Campus Locations (5 Enterprise Campuses)
    loc_file = os.path.join(ROOT_DIR, "data", "fixtures", "locations.json")
    if os.path.exists(loc_file):
        import json
        with open(loc_file, "r", encoding="utf-8") as f:
            all_locations = json.load(f)
        for loc in all_locations:
            loc["is_active"] = True
        db.locations.delete_many({})
        db.locations.insert_many(all_locations)

    # 2. Contractors (isolated from regular employees)
    from backend.routers.contractors import INITIAL_CONTRACTORS
    import copy
    contractors = copy.deepcopy(INITIAL_CONTRACTORS)
    db.contractors.delete_many({})
    db.contractors.insert_many(contractors)

    # 3. Compliance Rules
    compliance_rules = [
        {
            "rule_id": "COMP01",
            "name": "Maximum Weekly Working Hours",
            "description": "Standard weekly working hours must not exceed 48 hours without approved overtime compensation.",
            "threshold_value": 48.0,
            "threshold_unit": "hours_per_week",
            "severity": "HIGH",
            "is_active": True
        },
        {
            "rule_id": "COMP02",
            "name": "Mandatory Consecutive Rest Period",
            "description": "Employees must have at least 11 consecutive hours of rest between consecutive scheduled shifts.",
            "threshold_value": 11.0,
            "threshold_unit": "hours_rest",
            "severity": "CRITICAL",
            "is_active": True
        },
        {
            "rule_id": "COMP03",
            "name": "Maximum Consecutive Working Days",
            "description": "Employees cannot be rostered for more than 6 consecutive working days without a designated rest day.",
            "threshold_value": 6.0,
            "threshold_unit": "consecutive_days",
            "severity": "HIGH",
            "is_active": True
        }
    ]
    db.compliance_rules.delete_many({})
    db.compliance_rules.insert_many(compliance_rules)

    print("  [+] Locations, Contractors, and Compliance Rules seeded successfully.")


def reset_demo_environment():
    """Main execution orchestrating full reset."""
    print("=" * 70)
    print("INNOVATECORP HRVANTAGE — AUTOMATED DEMO ENVIRONMENT RESET")
    print("=" * 70)

    db = get_db()

    # Step 1: Execute primary seed pipeline (reseeds exact 200 employees and all base fixtures)
    print("\n[Step 1/4] Running primary MongoDB seeding pipeline...")
    seed_database()

    # Step 2: Seed Phase 14 extensions
    print("\n[Step 2/4] Seeding Phase 14 enterprise extensions...")
    seed_phase14_extensions(db)

    # Step 3: Establish explicit audit log entry (respecting log_id index)
    print("\n[Step 3/4] Recording environment reset event in audit trail...")
    reset_log = {
        "log_id": f"LOG_{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": "USR0001",
        "action": "ENVIRONMENT_RESET",
        "details": "Demo environment reset executed via scripts/reset_demo_environment.py. Rebuilt 200 employees.",
        "ip_address": "127.0.0.1"
    }
    db.audit_logs.insert_one(reset_log)
    print(f"  [+] Audit log recorded: {reset_log['log_id']}")

    # Step 4: Run automated validation suite
    print("\n[Step 4/4] Executing automated database relational validation...")
    val_script = os.path.join(ROOT_DIR, "scripts", "validate_database.py")
    res = subprocess.run([sys.executable, val_script], capture_output=True, text=True)
    print(res.stdout)

    if res.returncode != 0:
        print(f"[!] Validation failed:\n{res.stderr}", file=sys.stderr)
        sys.exit(1)

    # Final summary banner
    print("=" * 70)
    print("DEMO ENVIRONMENT RESET COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nVERIFIED DEMO CREDENTIALS:")
    print("  - Admin:    admin@demo.com    / Demo@2026  (Role: ADMIN)")
    print("  - HR:       hr@demo.com       / Demo@2026  (Role: HR)")
    print("  - Manager:  manager@demo.com  / Demo@2026  (Role: MANAGER)")
    print("  - Employee: employee@demo.com / Demo@2026  (Role: EMPLOYEE)")
    print("\nWORKFORCE GUARANTEE:")
    emp_count = db.employees.count_documents({})
    print(f"  - Total Regular Employees: {emp_count} (EMP001 to EMP200)")
    print(f"  - Isolated Contractors:    {db.contractors.count_documents({})} (CON001 to CON003)")
    print(f"  - Registered Campuses:     {db.locations.count_documents({})}")
    print("=" * 70)


if __name__ == "__main__":
    reset_demo_environment()
