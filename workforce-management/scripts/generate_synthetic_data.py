"""
AI-Powered Workforce Management Automation System
Reproducible Synthetic Data Generator
--------------------------------------------------
Generates EXACTLY 200 employees (EMP001 to EMP200) and all interrelated
synthetic HR data across 16+ relational entities.

Features:
- Deterministic random seed (SEED = 42)
- Zero external package dependencies (standard library only)
- Relational integrity: strict hierarchical manager tree, valid foreign keys,
  accurate mathematical payroll formulas, realistic 6-month attendance logs.
- Direct output to SQLite (data/hr_automation.db) and JSON fixtures (data/fixtures/).
"""

import os
import sys
import json
import math
import random
import sqlite3
import hashlib
from datetime import datetime, date, timedelta

SEED = 42
random.seed(SEED)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT_DIR, "data")
FIXTURES_DIR = os.path.join(DATA_DIR, "fixtures")
DB_PATH = os.path.join(DATA_DIR, "hr_automation.db")
SCHEMA_PATH = os.path.join(ROOT_DIR, "database", "schema.sql")

os.makedirs(FIXTURES_DIR, exist_ok=True)

# ---------------------------------------------------------
# Reference Dictionaries & Name Pools
# ---------------------------------------------------------

FIRST_NAMES_MALE = [
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
    "Shaurya", "Atharv", "Advik", "Pranav", "Advaith", "Aaryan", "Dhruv", "Kabir", "Rishi", "Darsh",
    "Karthik", "Rohan", "Siddharth", "Vikram", "Rahul", "Naveen", "Anand", "Suresh", "Manoj", "Deepak",
    "Ravi", "Amit", "Rajesh", "Praveen", "Gautam", "Harish", "Alok", "Varun", "Abhishek", "Kunal",
    "Sanjay", "Mahesh", "Nikhil", "Vishal", "Akash", "Ashok", "Vinay", "Hemant", "Rohit", "Tarun"
]

FIRST_NAMES_FEMALE = [
    "Saanvi", "Aanya", "Aadhya", "Aaradhya", "Ananya", "Pari", "Anika", "Navya", "Angel", "Diya",
    "Myra", "Sara", "Ira", "Kavya", "Avani", "Riya", "Prisha", "Isha", "Anvi", "Sneha",
    "Pooja", "Neha", "Divya", "Priya", "Anjali", "Swati", "Meera", "Shruti", "Shreya", "Deepika",
    "Pallavi", "Nandini", "Tanvi", "Sunita", "Rashmi", "Rupal", "Komal", "Shalini", "Aditi", "Bhavna",
    "Preeti", "Radhika", "Monika", "Gayatri", "Suman", "Vandana", "Archana", "Kalyani", "Jyoti", "Aparna"
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Reddy", "Rao", "Nair", "Iyer", "Mukherjee", "Chatterjee", "Banerjee",
    "Kulkarni", "Deshmukh", "Joshi", "Bhat", "Hegde", "Menon", "Pillai", "Gupta", "Agarwal", "Mishra",
    "Pandey", "Trivedi", "Shukla", "Chopra", "Malhotra", "Kapoor", "Bhatia", "Saxena", "Sinha", "Choudhury",
    "Mehta", "Shah", "Gala", "Parikh", "Dalal", "Das", "Ghosh", "Bose", "Dutta", "Sen",
    "Naidu", "Chowdary", "Goud", "Shetty", "Kamath", "Prabhu", "Pawar", "Shinde", "Jadhav", "Bhosale"
]

LOCATIONS = [
    {
        "location_id": "LOC01",
        "name": "Hyderabad Tech Park Campus",
        "city": "Hyderabad",
        "state": "Telangana",
        "country": "India",
        "latitude": 17.4435,
        "longitude": 78.3772,
        "geofence_radius_meters": 500.0,
        "timezone": "Asia/Kolkata"
    },
    {
        "location_id": "LOC02",
        "name": "Bengaluru Innovation Hub",
        "city": "Bengaluru",
        "state": "Karnataka",
        "country": "India",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "geofence_radius_meters": 500.0,
        "timezone": "Asia/Kolkata"
    },
    {
        "location_id": "LOC03",
        "name": "Chennai Cyber City",
        "city": "Chennai",
        "state": "Tamil Nadu",
        "country": "India",
        "latitude": 13.0827,
        "longitude": 80.2707,
        "geofence_radius_meters": 500.0,
        "timezone": "Asia/Kolkata"
    },
    {
        "location_id": "LOC04",
        "name": "Pune Silicon Towers",
        "city": "Pune",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "geofence_radius_meters": 500.0,
        "timezone": "Asia/Kolkata"
    },
    {
        "location_id": "LOC05",
        "name": "Mumbai Financial District Hub",
        "city": "Mumbai",
        "state": "Maharashtra",
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777,
        "geofence_radius_meters": 500.0,
        "timezone": "Asia/Kolkata"
    }
]

DEPARTMENTS = [
    {"department_id": "DEP01", "name": "Engineering", "code": "ENG", "description": "Software architecture, core platform, cloud and application development.", "budget": 120000000.0},
    {"department_id": "DEP02", "name": "Data Science", "code": "DS", "description": "Machine learning, AI research, statistical modeling and business intelligence.", "budget": 65000000.0},
    {"department_id": "DEP03", "name": "Human Resources", "code": "HR", "description": "Talent acquisition, employee engagement, workplace culture and benefits.", "budget": 28000000.0},
    {"department_id": "DEP04", "name": "Finance", "code": "FIN", "description": "Financial planning, accounting, payroll compliance, tax and audits.", "budget": 35000000.0},
    {"department_id": "DEP05", "name": "Marketing", "code": "MKT", "description": "Brand strategy, demand generation, product marketing and PR.", "budget": 42000000.0},
    {"department_id": "DEP06", "name": "Sales", "code": "SLS", "description": "Enterprise sales, client acquisition, renewals and revenue operations.", "budget": 58000000.0},
    {"department_id": "DEP07", "name": "Operations", "code": "OPS", "description": "Facilities, workplace operations, vendor relations and logistics.", "budget": 30000000.0},
    {"department_id": "DEP08", "name": "IT", "code": "IT", "description": "Enterprise infrastructure, cybersecurity, helpdesk and IT assets.", "budget": 45000000.0},
    {"department_id": "DEP09", "name": "Customer Support", "code": "CS", "description": "24/7 technical customer support, client onboarding and satisfaction.", "budget": 32000000.0},
]

SHIFTS = [
    {"shift_id": "SH01", "shift_name": "General Shift", "start_time": "09:00", "end_time": "18:00", "grace_period_mins": 15, "is_rotational": 0},
    {"shift_id": "SH02", "shift_name": "Morning Shift", "start_time": "06:00", "end_time": "15:00", "grace_period_mins": 15, "is_rotational": 1},
    {"shift_id": "SH03", "shift_name": "Evening Shift", "start_time": "13:00", "end_time": "21:30", "grace_period_mins": 15, "is_rotational": 1},
    {"shift_id": "SH04", "shift_name": "Night Shift", "start_time": "22:00", "end_time": "07:00", "grace_period_mins": 15, "is_rotational": 1},
]

SKILLS_CATALOG = [
    {"skill_id": "SK01", "skill_name": "Python", "category": "Technical"},
    {"skill_id": "SK02", "skill_name": "Java", "category": "Technical"},
    {"skill_id": "SK03", "skill_name": "SQL", "category": "Technical"},
    {"skill_id": "SK04", "skill_name": "JavaScript", "category": "Technical"},
    {"skill_id": "SK05", "skill_name": "Cloud Computing", "category": "Technical"},
    {"skill_id": "SK06", "skill_name": "Data Science", "category": "Data & AI"},
    {"skill_id": "SK07", "skill_name": "Machine Learning", "category": "Data & AI"},
    {"skill_id": "SK08", "skill_name": "Communication", "category": "Soft Skills"},
    {"skill_id": "SK09", "skill_name": "Project Management", "category": "Management"},
    {"skill_id": "SK10", "skill_name": "Excel", "category": "Analytics"},
    {"skill_id": "SK11", "skill_name": "Power BI", "category": "Analytics"},
    {"skill_id": "SK12", "skill_name": "AWS", "category": "Technical"},
    {"skill_id": "SK13", "skill_name": "Azure", "category": "Technical"},
    {"skill_id": "SK14", "skill_name": "React", "category": "Technical"},
    {"skill_id": "SK15", "skill_name": "DevOps", "category": "Technical"},
    {"skill_id": "SK16", "skill_name": "Cybersecurity", "category": "Technical"},
    {"skill_id": "SK17", "skill_name": "Financial Modeling", "category": "Analytics"},
    {"skill_id": "SK18", "skill_name": "Negotiation", "category": "Soft Skills"},
]

PROJECTS_DATA = [
    {"project_id": "PRJ01", "project_name": "Project Alpha", "client_name": "Apex Global Financials", "department_id": "DEP01", "start_date": "2025-06-01", "end_date": "2026-08-31", "status": "Active", "budget": 18500000.0},
    {"project_id": "PRJ02", "project_name": "Project Beta", "client_name": "Nexis Health Systems", "department_id": "DEP02", "start_date": "2025-08-15", "end_date": "2026-05-30", "status": "Active", "budget": 14200000.0},
    {"project_id": "PRJ03", "project_name": "Project Gamma", "client_name": "Titan Retail Cloud", "department_id": "DEP01", "start_date": "2025-04-01", "end_date": "2026-03-31", "status": "Active", "budget": 21000000.0},
    {"project_id": "PRJ04", "project_name": "Project Delta", "client_name": "Vanguard Telecom", "department_id": "DEP08", "start_date": "2025-09-01", "end_date": "2026-11-15", "status": "Active", "budget": 12000000.0},
    {"project_id": "PRJ05", "project_name": "Project Omega", "client_name": "OmniCorp Logistics", "department_id": "DEP07", "start_date": "2025-07-01", "end_date": "2026-06-30", "status": "Active", "budget": 16000000.0},
    {"project_id": "PRJ06", "project_name": "Project Horizon", "client_name": "Starlight Media", "department_id": "DEP05", "start_date": "2025-10-01", "end_date": "2026-09-30", "status": "Active", "budget": 9500000.0},
    {"project_id": "PRJ07", "project_name": "Project Pulse", "client_name": "Quantum Automations", "department_id": "DEP02", "start_date": "2025-11-01", "end_date": "2026-10-31", "status": "Active", "budget": 13800000.0},
    {"project_id": "PRJ08", "project_name": "Internal Platform v3", "client_name": "Internal Corp", "department_id": "DEP01", "start_date": "2025-01-01", "end_date": "2026-12-31", "status": "Active", "budget": 25000000.0},
]

HOLIDAYS = [
    {"holiday_id": "HOL01", "holiday_name": "Gandhi Jayanti", "date": "2025-10-02", "location_id": "ALL"},
    {"holiday_id": "HOL02", "holiday_name": "Dussehra (Vijayadashami)", "date": "2025-10-12", "location_id": "ALL"},
    {"holiday_id": "HOL03", "holiday_name": "Diwali Deepavali", "date": "2025-10-20", "location_id": "ALL"},
    {"holiday_id": "HOL04", "holiday_name": "Guru Nanak Jayanti", "date": "2025-11-05", "location_id": "ALL"},
    {"holiday_id": "HOL05", "holiday_name": "Christmas Day", "date": "2025-12-25", "location_id": "ALL"},
    {"holiday_id": "HOL06", "holiday_name": "New Year's Day", "date": "2026-01-01", "location_id": "ALL"},
    {"holiday_id": "HOL07", "holiday_name": "Makar Sankranti / Pongal", "date": "2026-01-14", "location_id": "ALL"},
    {"holiday_id": "HOL08", "holiday_name": "Republic Day", "date": "2026-01-26", "location_id": "ALL"},
    {"holiday_id": "HOL09", "holiday_name": "Maha Shivaratri", "date": "2026-02-15", "location_id": "ALL"},
    {"holiday_id": "HOL10", "holiday_name": "Holi Festival", "date": "2026-03-03", "location_id": "ALL"},
]

TRAINING_COURSES = [
    {"name": "Advanced Python & Microservices", "skill": "Python", "duration": 40},
    {"name": "Applied Machine Learning at Scale", "skill": "Machine Learning", "duration": 50},
    {"name": "Modern Cloud Architecture with AWS", "skill": "AWS", "duration": 45},
    {"name": "Data Analytics with Power BI & SQL", "skill": "Power BI", "duration": 35},
    {"name": "Full Stack React & Modern UI", "skill": "React", "duration": 40},
    {"name": "Kubernetes & DevOps Pipelines", "skill": "DevOps", "duration": 40},
    {"name": "Strategic Leadership & Communication", "skill": "Communication", "duration": 25},
    {"name": "Enterprise Cybersecurity Fundamentals", "skill": "Cybersecurity", "duration": 30},
    {"name": "Financial Analysis & Forecasting", "skill": "Financial Modeling", "duration": 30},
    {"name": "Agile Project Delivery Masterclass", "skill": "Project Management", "duration": 25},
]

# ---------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------

def hash_password(password: str) -> str:
    """Deterministic hash for demo accounts"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def random_date(start: date, end: date) -> date:
    days_range = (end - start).days
    return start + timedelta(days=random.randint(0, days_range))

# ---------------------------------------------------------
# Generation Logic
# ---------------------------------------------------------

def generate_employees():
    """
    Generates EXACTLY 200 employees (EMP001 to EMP200).
    Organized hierarchically:
    EMP001: Chief Executive Officer (Top of tree, manager_id = None)
    EMP002 to EMP010: 9 Department Heads (report to EMP001)
    EMP011 to EMP035: 25 Functional Managers / Team Leads (report to respective Dept Heads)
    EMP036 to EMP200: 165 Individual Contributors (report to functional managers)
    """
    employees = []
    used_emails = set()

    dept_distribution = {
        "DEP01": 55, # Engineering (large)
        "DEP02": 25, # Data Science
        "DEP03": 12, # HR
        "DEP04": 15, # Finance
        "DEP05": 16, # Marketing
        "DEP06": 22, # Sales
        "DEP07": 15, # Operations
        "DEP08": 18, # IT
        "DEP09": 22, # Customer Support
    }
    assert sum(dept_distribution.values()) == 200, "Distribution sum must equal exactly 200"

    dept_target_counts = dict(dept_distribution)

    # 1. EMP001: CEO
    emp001 = {
        "employee_id": "EMP001",
        "first_name": "Vikramaditya",
        "last_name": "Singhania",
        "gender": "Male",
        "date_of_birth": "1976-08-14",
        "email": "vikramaditya.singhania@innovatecorp.demo",
        "phone": "+91-9876543210",
        "address": "Penthouse 12, Jubilee Hills, Hyderabad",
        "joining_date": "2018-01-10",
        "employment_type": "Full-Time",
        "designation": "Chief Executive Officer",
        "department_id": "DEP07", # Operations/Executive
        "manager_id": None,
        "location_id": "LOC01",
        "salary": 5800000.0,
        "experience": 24.0,
        "employment_status": "Active",
        "role": "ADMIN"
    }
    employees.append(emp001)
    used_emails.add(emp001["email"])
    dept_target_counts["DEP07"] -= 1

    # 2. EMP002 to EMP010: 9 Department Heads
    dept_heads_info = [
        ("DEP01", "Vice President of Engineering", "Engineering Lead", 4200000.0, 18.0),
        ("DEP02", "Head of AI & Data Science", "Data Science Lead", 4000000.0, 17.0),
        ("DEP03", "Chief Human Resources Officer", "HR Director", 3500000.0, 16.0),
        ("DEP04", "Chief Financial Officer", "Finance Director", 3900000.0, 17.0),
        ("DEP05", "Chief Marketing Officer", "Marketing Director", 3600000.0, 16.0),
        ("DEP06", "Head of Global Sales", "Sales VP", 3800000.0, 17.0),
        ("DEP07", "Chief Operating Officer", "VP Operations", 3700000.0, 18.0),
        ("DEP08", "Head of Enterprise IT & Security", "IT Director", 3500000.0, 16.0),
        ("DEP09", "Director of Customer Success", "Support Director", 3200000.0, 15.0),
    ]

    dept_head_ids = {}

    for idx, (dept_id, title, _, salary, exp) in enumerate(dept_heads_info, start=2):
        emp_id = f"EMP{idx:03d}"
        gender = "Female" if idx % 2 == 0 else "Male"
        first = FIRST_NAMES_FEMALE[idx % len(FIRST_NAMES_FEMALE)] if gender == "Female" else FIRST_NAMES_MALE[idx % len(FIRST_NAMES_MALE)]
        last = LAST_NAMES[idx % len(LAST_NAMES)]
        email = f"{first.lower()}.{last.lower()}@innovatecorp.demo"
        if email in used_emails:
            email = f"{first.lower()}.{last.lower()}{idx}@innovatecorp.demo"
        used_emails.add(email)

        loc = LOCATIONS[idx % len(LOCATIONS)]["location_id"]
        birth_year = 2026 - int(exp + 23)
        dob = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        join_date = f"{2019 + (idx % 3)}-{random.randint(1,12):02d}-15"

        role = "HR" if dept_id == "DEP03" else "MANAGER"

        emp = {
            "employee_id": emp_id,
            "first_name": first,
            "last_name": last,
            "gender": gender,
            "date_of_birth": dob,
            "email": email,
            "phone": f"+91-98{random.randint(10000000, 99999999)}",
            "address": f"Plot {10 + idx}, Sector {idx}, {LOCATIONS[idx % len(LOCATIONS)]['city']}",
            "joining_date": join_date,
            "employment_type": "Full-Time",
            "designation": title,
            "department_id": dept_id,
            "manager_id": "EMP001", # All report to CEO
            "location_id": loc,
            "salary": salary,
            "experience": exp,
            "employment_status": "Active",
            "role": role
        }
        employees.append(emp)
        dept_target_counts[dept_id] -= 1
        dept_head_ids[dept_id] = emp_id

    # 3. EMP011 to EMP035: 25 Functional Managers / Team Leads
    manager_assignments = [
        # (emp_id, dept_id, designation, manager_id)
        ("DEP01", "Engineering Manager - Backend", dept_head_ids["DEP01"]),
        ("DEP01", "Engineering Manager - Frontend", dept_head_ids["DEP01"]),
        ("DEP01", "Engineering Manager - Cloud DevOps", dept_head_ids["DEP01"]),
        ("DEP01", "QA & Test Automation Manager", dept_head_ids["DEP01"]),
        ("DEP01", "Staff Architect Lead", dept_head_ids["DEP01"]),
        ("DEP01", "Mobile Development Lead", dept_head_ids["DEP01"]),
        ("DEP02", "Lead Machine Learning Scientist", dept_head_ids["DEP02"]),
        ("DEP02", "Data Engineering Lead", dept_head_ids["DEP02"]),
        ("DEP02", "BI & Analytics Manager", dept_head_ids["DEP02"]),
        ("DEP03", "Talent Acquisition Manager", dept_head_ids["DEP03"]),
        ("DEP03", "HR Operations & Payroll Lead", dept_head_ids["DEP03"]),
        ("DEP04", "Financial Controller", dept_head_ids["DEP04"]),
        ("DEP04", "Corporate Tax & Audit Manager", dept_head_ids["DEP04"]),
        ("DEP05", "Digital Marketing Lead", dept_head_ids["DEP05"]),
        ("DEP05", "Product Marketing Manager", dept_head_ids["DEP05"]),
        ("DEP06", "Enterprise Sales Lead - North & West", dept_head_ids["DEP06"]),
        ("DEP06", "Enterprise Sales Lead - South", dept_head_ids["DEP06"]),
        ("DEP06", "Inside Sales & Business Dev Manager", dept_head_ids["DEP06"]),
        ("DEP07", "Workplace Operations Manager", dept_head_ids["DEP07"]),
        ("DEP07", "Procurement & Vendor Manager", dept_head_ids["DEP07"]),
        ("DEP08", "IT Infrastructure Lead", dept_head_ids["DEP08"]),
        ("DEP08", "Information Security Officer", dept_head_ids["DEP08"]),
        ("DEP09", "Technical Support Team Lead - Tier 1", dept_head_ids["DEP09"]),
        ("DEP09", "Technical Support Team Lead - Tier 2", dept_head_ids["DEP09"]),
        ("DEP09", "Customer Onboarding Lead", dept_head_ids["DEP09"]),
    ]

    dept_managers_pool = {dept["department_id"]: [] for dept in DEPARTMENTS}
    # Also include dept heads in manager pool
    for dept_id, head_id in dept_head_ids.items():
        dept_managers_pool[dept_id].append(head_id)

    for idx, (dept_id, title, mgr_id) in enumerate(manager_assignments, start=11):
        emp_id = f"EMP{idx:03d}"
        gender = "Female" if idx % 2 == 0 else "Male"
        first = FIRST_NAMES_FEMALE[idx % len(FIRST_NAMES_FEMALE)] if gender == "Female" else FIRST_NAMES_MALE[idx % len(FIRST_NAMES_MALE)]
        last = LAST_NAMES[(idx * 3) % len(LAST_NAMES)]
        email = f"{first.lower()}.{last.lower()}@innovatecorp.demo"
        if email in used_emails:
            email = f"{first.lower()}.{last.lower()}{idx}@innovatecorp.demo"
        used_emails.add(email)

        loc = LOCATIONS[idx % len(LOCATIONS)]["location_id"]
        exp = round(10.0 + (idx % 5) * 1.2, 1)
        birth_year = 2026 - int(exp + 22)
        dob = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        join_date = f"{2020 + (idx % 3)}-{random.randint(1,12):02d}-10"
        salary = round(2200000.0 + (idx % 6) * 150000.0, 2)

        role = "HR" if dept_id == "DEP03" else "MANAGER"

        emp = {
            "employee_id": emp_id,
            "first_name": first,
            "last_name": last,
            "gender": gender,
            "date_of_birth": dob,
            "email": email,
            "phone": f"+91-97{random.randint(10000000, 99999999)}",
            "address": f"Flat {101 + idx}, Harmony Heights, {LOCATIONS[idx % len(LOCATIONS)]['city']}",
            "joining_date": join_date,
            "employment_type": "Full-Time",
            "designation": title,
            "department_id": dept_id,
            "manager_id": mgr_id,
            "location_id": loc,
            "salary": salary,
            "experience": exp,
            "employment_status": "Active",
            "role": role
        }
        employees.append(emp)
        dept_target_counts[dept_id] -= 1
        dept_managers_pool[dept_id].append(emp_id)

    # 4. EMP036 to EMP200: 165 Individual Contributors
    designation_map = {
        "DEP01": ["Senior Software Engineer", "Software Engineer", "Frontend Developer", "Backend Developer", "DevOps Engineer", "QA Engineer", "Cloud Engineer"],
        "DEP02": ["Data Scientist", "Machine Learning Engineer", "Data Analyst", "Data Engineer", "AI Research Associate"],
        "DEP03": ["HR Business Partner", "Talent Acquisition Specialist", "HR Generalist", "Payroll Specialist", "Employee Experience Associate"],
        "DEP04": ["Financial Analyst", "Accountant", "Senior Financial Analyst", "Payroll Accountant", "Billing Specialist"],
        "DEP05": ["Marketing Specialist", "Content Strategist", "SEO Analyst", "Growth Marketing Associate", "Graphic Designer"],
        "DEP06": ["Account Executive", "Business Development Representative", "Sales Operations Analyst", "Client Relationship Manager"],
        "DEP07": ["Workplace Coordinator", "Operations Analyst", "Facilities Specialist", "Procurement Associate"],
        "DEP08": ["Systems Administrator", "Network Engineer", "Cybersecurity Analyst", "IT Support Specialist", "Cloud Ops Associate"],
        "DEP09": ["Customer Support Representative", "Technical Support Engineer", "Client Success Associate", "Support Specialist"],
    }

    # Build sequence of departments matching remaining target counts
    remaining_dept_list = []
    for dept_id, remaining in dept_target_counts.items():
        remaining_dept_list.extend([dept_id] * remaining)
    
    # Shuffle deterministically with current seed
    random.shuffle(remaining_dept_list)
    assert len(remaining_dept_list) == 200 - 35, f"Expected 165 remaining, got {len(remaining_dept_list)}"

    for idx, dept_id in enumerate(remaining_dept_list, start=36):
        emp_id = f"EMP{idx:03d}"
        gender = "Female" if (idx * 7) % 2 == 0 else "Male"
        first = FIRST_NAMES_FEMALE[idx % len(FIRST_NAMES_FEMALE)] if gender == "Female" else FIRST_NAMES_MALE[idx % len(FIRST_NAMES_MALE)]
        last = LAST_NAMES[(idx * 7) % len(LAST_NAMES)]
        email = f"{first.lower()}.{last.lower()}@innovatecorp.demo"
        if email in used_emails:
            email = f"{first.lower()}.{last.lower()}{idx}@innovatecorp.demo"
        used_emails.add(email)

        # Experience & age
        exp = round(random.uniform(0.5, 9.0), 1)
        birth_year = 2026 - int(exp + 22 + random.randint(0, 3))
        dob = f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}"
        
        # Joining date between 2021 and 2025
        join_year = random.randint(2021, 2025)
        join_month = random.randint(1, 12)
        join_day = random.randint(1, 28)
        join_date = f"{join_year}-{join_month:02d}-{join_day:02d}"

        # Designation
        designations = designation_map[dept_id]
        designation = designations[idx % len(designations)]

        # Salary based on exp & dept
        base_rate = 600000.0 if dept_id in ["DEP01", "DEP02"] else 450000.0
        salary = round(base_rate + (exp * 125000.0) + (random.randint(-20, 30) * 10000.0), 2)
        salary = max(380000.0, salary)

        # Manager: picked from dept_managers_pool
        possible_managers = dept_managers_pool[dept_id]
        mgr_id = random.choice(possible_managers)

        # Location
        loc = LOCATIONS[idx % len(LOCATIONS)]["location_id"]

        # Employment status (few on notice / leave)
        if idx in [45, 92, 134]:
            status = "On Notice"
        elif idx in [78, 160]:
            status = "On Leave"
        else:
            status = "Active"

        # Employment type
        emp_type = "Intern" if exp < 1.0 and idx % 15 == 0 else ("Contract" if idx % 20 == 0 else "Full-Time")

        role = "HR" if dept_id == "DEP03" else "EMPLOYEE"

        emp = {
            "employee_id": emp_id,
            "first_name": first,
            "last_name": last,
            "gender": gender,
            "date_of_birth": dob,
            "email": email,
            "phone": f"+91-9{random.randint(10, 99)}{random.randint(1000000, 9999999)}",
            "address": f"Door {random.randint(1, 500)}, Colony {random.randint(1, 25)}, {LOCATIONS[idx % len(LOCATIONS)]['city']}",
            "joining_date": join_date,
            "employment_type": emp_type,
            "designation": designation,
            "department_id": dept_id,
            "manager_id": mgr_id,
            "location_id": loc,
            "salary": salary,
            "experience": exp,
            "employment_status": status,
            "role": role
        }
        employees.append(emp)

    assert len(employees) == 200, f"Expected exactly 200 employees, got {len(employees)}"
    return employees, dept_head_ids

def generate_employee_skills(employees):
    """Assign 2-5 skills per employee based on their department and designation."""
    emp_skills = []
    
    dept_skill_prefs = {
        "DEP01": ["SK01", "SK02", "SK03", "SK04", "SK05", "SK12", "SK13", "SK14", "SK15"], # Tech
        "DEP02": ["SK01", "SK03", "SK06", "SK07", "SK10", "SK11", "SK12"], # Data & AI
        "DEP03": ["SK08", "SK09", "SK10"], # HR
        "DEP04": ["SK03", "SK10", "SK11", "SK17"], # Finance
        "DEP05": ["SK08", "SK10", "SK18", "SK04"], # Mkt
        "DEP06": ["SK08", "SK09", "SK18", "SK10"], # Sales
        "DEP07": ["SK08", "SK09", "SK10", "SK15"], # Ops
        "DEP08": ["SK03", "SK05", "SK12", "SK13", "SK15", "SK16"], # IT
        "DEP09": ["SK08", "SK10", "SK18", "SK03"], # Support
    }

    proficiency_levels = ["Beginner", "Intermediate", "Advanced", "Expert"]

    for emp in employees:
        dept_id = emp["department_id"]
        pref_skills = dept_skill_prefs.get(dept_id, ["SK08", "SK09", "SK10"])
        num_skills = random.randint(3, 5)
        chosen_skills = set(random.sample(pref_skills, min(num_skills, len(pref_skills))))
        
        # Add general skills
        if len(chosen_skills) < 4:
            chosen_skills.add(random.choice(["SK08", "SK09", "SK10"]))

        for s_id in chosen_skills:
            if emp["experience"] > 12:
                prof = random.choice(["Advanced", "Expert"])
            elif emp["experience"] > 5:
                prof = random.choice(["Intermediate", "Advanced"])
            elif emp["experience"] > 2:
                prof = random.choice(["Beginner", "Intermediate"])
            else:
                prof = "Beginner"

            years_exp = round(min(emp["experience"], random.uniform(1.0, max(1.5, emp["experience"]))), 1)

            emp_skills.append({
                "employee_id": emp["employee_id"],
                "skill_id": s_id,
                "proficiency_level": prof,
                "years_experience": years_exp
            })

    return emp_skills

def generate_shift_assignments(employees):
    """Assign shifts to employees. Customer Support, IT, Ops get rotational/evening/night shifts."""
    shift_assignments = []
    for idx, emp in enumerate(employees):
        dept_id = emp["department_id"]
        if dept_id in ["DEP09", "DEP08", "DEP07"]:
            # Rotational / varying shifts
            shift_id = random.choice(["SH01", "SH02", "SH03", "SH04"])
        else:
            shift_id = "SH01" # General shift for most

        shift_assignments.append({
            "schedule_id": f"SCH{idx+1:04d}",
            "employee_id": emp["employee_id"],
            "shift_id": shift_id,
            "effective_from": "2025-09-01",
            "effective_to": "2026-12-31"
        })
    return shift_assignments

def generate_project_assignments(employees):
    """Assign employees to projects."""
    assignments = []
    assign_counter = 1

    # Assign technical employees (DEP01, DEP02, DEP08) to projects
    for emp in employees:
        dept = emp["department_id"]
        matching_projects = [p for p in PROJECTS_DATA if p["department_id"] == dept]
        if not matching_projects:
            # Maybe assign to general or internal platform
            matching_projects = [PROJECTS_DATA[7]] # Internal Platform

        num_proj = 1 if random.random() > 0.25 else 2
        assigned = random.sample(matching_projects, min(num_proj, len(matching_projects)))

        alloc = 100.0 if len(assigned) == 1 else 50.0
        for p in assigned:
            role = emp["designation"]
            assignments.append({
                "assignment_id": f"ASG{assign_counter:04d}",
                "employee_id": emp["employee_id"],
                "project_id": p["project_id"],
                "role": role,
                "allocation_percentage": alloc,
                "start_date": "2025-10-01",
                "end_date": "2026-06-30"
            })
            assign_counter += 1

    return assignments

def generate_attendance_data(employees, shift_map):
    """
    Generates approximately 6 months of realistic synthetic attendance records
    (October 1, 2025 to March 20, 2026) for all 200 employees.
    Strictly adheres to working days (Mon-Fri) excluding holidays.
    Includes realistic variations: Present, Absent, Late, Half Day, WFH, Holiday, Leave.
    Realistic check-in, check-out, overtime, and simulated AI anomalies (~1.5%).
    """
    attendance_records = []
    holiday_dates = {h["date"] for h in HOLIDAYS}

    start_date = date(2025, 10, 1)
    end_date = date(2026, 3, 20)

    # Precalculate calendar days
    calendar_days = []
    curr = start_date
    while curr <= end_date:
        calendar_days.append(curr)
        curr += timedelta(days=1)

    record_counter = 1

    attendance_methods = ["Biometric", "Face Recognition", "GPS", "QR Code"]

    # Shift timing details
    shift_info = {
        "SH01": (9, 0, 18, 0),
        "SH02": (6, 0, 15, 0),
        "SH03": (13, 0, 21, 30),
        "SH04": (22, 0, 7, 0),
    }

    # Profile behavioral tendencies for employees (some are always on time, some prone to late/absent)
    employee_profiles = {}
    for emp in employees:
        eid = emp["employee_id"]
        # Punctuality bias: 0 (chronic late) to 1 (extremely punctual)
        punctuality = random.uniform(0.75, 0.98)
        wfh_preference = random.uniform(0.02, 0.15) if emp["department_id"] in ["DEP01", "DEP02"] else 0.02
        employee_profiles[eid] = {
            "punctuality": punctuality,
            "wfh_preference": wfh_preference
        }

    for current_day in calendar_days:
        day_str = current_day.strftime("%Y-%m-%d")
        weekday = current_day.weekday() # 0 = Monday, 6 = Sunday
        is_weekend = weekday >= 5
        is_holiday = day_str in holiday_dates

        if is_weekend:
            continue # Standard weekend off

        for emp in employees:
            eid = emp["employee_id"]
            assigned_shift_id = shift_map[eid]
            s_start_h, s_start_m, s_end_h, s_end_m = shift_info[assigned_shift_id]
            profile = employee_profiles[eid]

            if is_holiday:
                attendance_records.append({
                    "attendance_id": f"ATT{record_counter:07d}",
                    "employee_id": eid,
                    "date": day_str,
                    "check_in": None,
                    "check_out": None,
                    "attendance_status": "Holiday",
                    "attendance_method": None,
                    "location_id": emp["location_id"],
                    "late_minutes": 0,
                    "overtime_hours": 0.0,
                    "shift_id": assigned_shift_id,
                    "anomaly_flag": 0,
                    "anomaly_reason": None
                })
                record_counter += 1
                continue

            # Working day: determine status
            rand_roll = random.random()

            # 1. Leave (~3%)
            if rand_roll < 0.03:
                attendance_records.append({
                    "attendance_id": f"ATT{record_counter:07d}",
                    "employee_id": eid,
                    "date": day_str,
                    "check_in": None,
                    "check_out": None,
                    "attendance_status": "Leave",
                    "attendance_method": None,
                    "location_id": emp["location_id"],
                    "late_minutes": 0,
                    "overtime_hours": 0.0,
                    "shift_id": assigned_shift_id,
                    "anomaly_flag": 0,
                    "anomaly_reason": None
                })
                record_counter += 1
                continue

            # 2. Absent (~2%)
            elif rand_roll < 0.05:
                attendance_records.append({
                    "attendance_id": f"ATT{record_counter:07d}",
                    "employee_id": eid,
                    "date": day_str,
                    "check_in": None,
                    "check_out": None,
                    "attendance_status": "Absent",
                    "attendance_method": None,
                    "location_id": emp["location_id"],
                    "late_minutes": 0,
                    "overtime_hours": 0.0,
                    "shift_id": assigned_shift_id,
                    "anomaly_flag": 0,
                    "anomaly_reason": None
                })
                record_counter += 1
                continue

            # 3. Work From Home (~5-10%)
            elif rand_roll < (0.05 + profile["wfh_preference"]):
                check_in_time = f"{s_start_h:02d}:{random.randint(0, 15):02d}:00"
                check_out_time = f"{s_end_h:02d}:{random.randint(0, 30):02d}:00"
                attendance_records.append({
                    "attendance_id": f"ATT{record_counter:07d}",
                    "employee_id": eid,
                    "date": day_str,
                    "check_in": check_in_time,
                    "check_out": check_out_time,
                    "attendance_status": "Work From Home",
                    "attendance_method": "GPS",
                    "location_id": emp["location_id"],
                    "late_minutes": 0,
                    "overtime_hours": 0.0,
                    "shift_id": assigned_shift_id,
                    "anomaly_flag": 0,
                    "anomaly_reason": None
                })
                record_counter += 1
                continue

            # 4. Half Day (~1.5%)
            elif rand_roll < (0.065 + profile["wfh_preference"]):
                check_in_time = f"{s_start_h:02d}:{random.randint(0, 10):02d}:00"
                check_out_time = f"{(s_start_h + 4):02d}:{random.randint(0, 15):02d}:00"
                attendance_records.append({
                    "attendance_id": f"ATT{record_counter:07d}",
                    "employee_id": eid,
                    "date": day_str,
                    "check_in": check_in_time,
                    "check_out": check_out_time,
                    "attendance_status": "Half Day",
                    "attendance_method": random.choice(attendance_methods),
                    "location_id": emp["location_id"],
                    "late_minutes": 0,
                    "overtime_hours": 0.0,
                    "shift_id": assigned_shift_id,
                    "anomaly_flag": 0,
                    "anomaly_reason": None
                })
                record_counter += 1
                continue

            # 5. Present or Late
            method = random.choice(attendance_methods)
            is_punctual = random.random() < profile["punctuality"]
            
            anomaly_flag = 0
            anomaly_reason = None

            if is_punctual:
                status = "Present"
                late_mins = 0
                # Arrive between 20 mins early to 5 mins past
                in_min_delta = random.randint(-20, 5)
            else:
                status = "Late"
                # Arrive 16 to 75 mins late
                late_mins = random.randint(16, 75)
                in_min_delta = late_mins

            # Occasional AI Anomaly Injection (~1.5% chance)
            anomaly_roll = random.random()
            if anomaly_roll < 0.015:
                anomaly_type = random.choice(["extreme_overtime", "unusual_checkin", "missing_checkout", "late_arrival_spike"])
                if anomaly_type == "missing_checkout":
                    anomaly_flag = 1
                    anomaly_reason = "Missing check-out timestamp recorded by access control"
                elif anomaly_type == "extreme_overtime":
                    anomaly_flag = 1
                    anomaly_reason = "Abnormal overtime exceeding 4.0 hours in single shift"
                elif anomaly_type == "unusual_checkin":
                    anomaly_flag = 1
                    anomaly_reason = "Unusual check-in time significantly deviated from assigned shift schedule"
                elif anomaly_type == "late_arrival_spike":
                    late_mins = random.randint(120, 240)
                    in_min_delta = late_mins
                    status = "Late"
                    anomaly_flag = 1
                    anomaly_reason = f"Severe late arrival ({late_mins} mins past grace period)"

            # Compute actual check-in timestamp
            in_total_mins = s_start_h * 60 + s_start_m + in_min_delta
            in_h = (in_total_mins // 60) % 24
            in_m = in_total_mins % 60
            in_s = random.randint(0, 59)
            check_in_time = f"{in_h:02d}:{in_m:02d}:{in_s:02d}"

            # Compute check-out timestamp
            if anomaly_flag == 1 and anomaly_reason.startswith("Missing check-out"):
                check_out_time = None
                ot_hours = 0.0
            else:
                ot_hours = 0.0
                if anomaly_flag == 1 and "overtime" in anomaly_reason:
                    ot_hours = round(random.uniform(4.0, 4.8), 1)
                    out_min_delta = int(ot_hours * 60)
                else:
                    # Normal working day: 0 to 2.0 hrs overtime occasionally
                    if random.random() < 0.15:
                        ot_hours = round(random.uniform(0.5, 2.0), 1)
                        out_min_delta = int(ot_hours * 60) + random.randint(0, 15)
                    else:
                        out_min_delta = random.randint(-5, 20)

                out_total_mins = s_end_h * 60 + s_end_m + out_min_delta

                # For non-night shifts (SH01, SH02, SH03), ensure checkout stays on same day strictly after checkin
                if assigned_shift_id != "SH04":
                    out_total_mins = max(in_total_mins + 180, min(23 * 60 + 55, out_total_mins))
                    out_h = out_total_mins // 60
                    out_m = out_total_mins % 60
                else:
                    # Night shift wraps past midnight
                    out_h = (out_total_mins // 60) % 24
                    out_m = out_total_mins % 60

                out_s = random.randint(0, 59)
                check_out_time = f"{out_h:02d}:{out_m:02d}:{out_s:02d}"

            attendance_records.append({
                "attendance_id": f"ATT{record_counter:07d}",
                "employee_id": eid,
                "date": day_str,
                "check_in": check_in_time,
                "check_out": check_out_time,
                "attendance_status": status,
                "attendance_method": method,
                "location_id": emp["location_id"],
                "late_minutes": late_mins,
                "overtime_hours": ot_hours,
                "shift_id": assigned_shift_id,
                "anomaly_flag": anomaly_flag,
                "anomaly_reason": anomaly_reason
            })
            record_counter += 1

    return attendance_records

def generate_leave_data(employees):
    """
    Generates leave balances and realistic leave requests for all 200 employees.
    Maintains exact balance equation: allocated_days == used_days + remaining_days.
    """
    leave_types = ["Annual Leave", "Sick Leave", "Casual Leave", "Emergency Leave", "Maternity/Paternity Leave"]
    
    balances = []
    requests = []
    
    req_counter = 1
    bal_counter = 1

    reasons_pool = [
        "Family vacation and personal travel",
        "Viral fever and medical rest advised by physician",
        "Attending family wedding ceremony",
        "Personal legal and banking appointments",
        "Home renovation and relocation",
        "Child school admission procedures",
        "Routine health checkup and diagnostic tests",
        "Sudden domestic emergency"
    ]

    for emp in employees:
        eid = emp["employee_id"]
        mgr_id = emp["manager_id"] or "EMP001"

        # Allocations
        alloc_map = {
            "Annual Leave": 18.0,
            "Sick Leave": 12.0,
            "Casual Leave": 10.0,
            "Emergency Leave": 5.0,
            "Maternity/Paternity Leave": 90.0 if emp["gender"] == "Female" and random.random() < 0.1 else (15.0 if emp["gender"] == "Male" and random.random() < 0.1 else 0.0)
        }

        for l_type, allocated in alloc_map.items():
            if allocated == 0.0:
                continue

            used = 0.0
            
            # Generate 0-2 requests per leave type
            num_req = random.choices([0, 1, 2], weights=[0.4, 0.45, 0.15])[0]
            
            for _ in range(num_req):
                days = float(random.choice([1, 2, 3, 4, 5]))
                if used + days > allocated:
                    continue

                # Date in past 6 months
                start = random_date(date(2025, 10, 5), date(2026, 3, 10))
                end = start + timedelta(days=int(days)-1)
                
                # Status
                roll = random.random()
                if roll < 0.75:
                    status = "Approved"
                    used += days
                elif roll < 0.90:
                    status = "Pending"
                else:
                    status = "Rejected"

                requests.append({
                    "leave_id": f"LV{req_counter:05d}",
                    "employee_id": eid,
                    "leave_type": l_type,
                    "start_date": start.strftime("%Y-%m-%d"),
                    "end_date": end.strftime("%Y-%m-%d"),
                    "days_count": days,
                    "reason": random.choice(reasons_pool),
                    "status": status,
                    "approved_by": mgr_id,
                    "created_at": (start - timedelta(days=random.randint(2, 7))).strftime("%Y-%m-%d %H:%M:%S")
                })
                req_counter += 1

            remaining = round(allocated - used, 1)

            balances.append({
                "balance_id": f"BAL{bal_counter:05d}",
                "employee_id": eid,
                "leave_type": l_type,
                "allocated_days": allocated,
                "used_days": used,
                "remaining_days": remaining,
                "year": 2026
            })
            bal_counter += 1

    return balances, requests

def generate_timesheet_data(employees, project_assignments):
    """
    Generates synthetic daily timesheets for the past 4 weeks (recent active period)
    matching assignments.
    hours_worked = billable_hours + non_billable_hours
    """
    timesheets = []
    ts_counter = 1

    # Map employee to project ids
    emp_proj_map = {}
    for asg in project_assignments:
        emp_proj_map.setdefault(asg["employee_id"], []).append(asg["project_id"])

    # Past 20 working days
    cur = date(2026, 2, 23)
    end = date(2026, 3, 20)
    days = []
    while cur <= end:
        if cur.weekday() < 5:
            days.append(cur.strftime("%Y-%m-%d"))
        cur += timedelta(days=1)

    for day in days:
        for emp in employees:
            eid = emp["employee_id"]
            projs = emp_proj_map.get(eid, ["PRJ08"])
            chosen_proj = random.choice(projs)

            # Working hours: standard 8.0, occasionally overtime
            ot = 0.0
            if random.random() < 0.15:
                ot = round(random.uniform(1.0, 2.5), 1)

            total_h = 8.0 + ot
            billable = round(total_h * random.uniform(0.75, 1.0), 1)
            non_billable = round(total_h - billable, 1)

            status = "Approved" if day < "2026-03-15" else random.choice(["Submitted", "Approved"])

            timesheets.append({
                "timesheet_id": f"TS{ts_counter:07d}",
                "employee_id": eid,
                "date": day,
                "project_id": chosen_proj,
                "hours_worked": total_h,
                "billable_hours": billable,
                "non_billable_hours": non_billable,
                "overtime_hours": ot,
                "status": status
            })
            ts_counter += 1

    return timesheets

def generate_payroll_data(employees):
    """
    Generates 6 months of mathematically exact payroll records (2025-10 through 2026-03).
    Strict formulas:
    - gross_salary = base_salary + overtime_pay + incentives + bonuses
    - deductions = tax_deduction + pf_deduction + leave_deduction
    - net_salary = gross_salary - deductions
    - net_salary >= 0
    """
    payroll_records = []
    pay_counter = 1

    months = ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03"]

    for month_str in months:
        y, m = map(int, month_str.split("-"))
        # Pay date is last day of the month
        if m in [1, 3, 5, 7, 8, 10, 12]:
            pay_day = 31
        elif m in [4, 6, 9, 11]:
            pay_day = 30
        else:
            pay_day = 28
        pay_date = f"{month_str}-{pay_day:02d}"

        for emp in employees:
            eid = emp["employee_id"]
            monthly_base = round(emp["salary"] / 12.0, 2)

            # Overtime pay based on role
            hourly_rate = round(monthly_base / 160.0, 2)
            ot_hours = random.choice([0.0, 0.0, 4.0, 8.0, 12.0]) if emp["role"] == "EMPLOYEE" else 0.0
            overtime_pay = round(ot_hours * hourly_rate * 1.5, 2)

            # Bonuses & Incentives (festival bonus in Oct/Nov, performance incentive in Mar)
            bonuses = 0.0
            incentives = 0.0
            if month_str == "2025-10": # Diwali festival bonus
                bonuses = round(monthly_base * 0.10, 2)
            elif month_str == "2026-03": # Annual performance incentive
                incentives = round(monthly_base * random.uniform(0.05, 0.20), 2)

            gross_salary = round(monthly_base + overtime_pay + incentives + bonuses, 2)

            # Deductions
            # Provident Fund: 12% of base capped realistically
            pf = round(min(monthly_base * 0.12, 15000.0), 2)
            
            # Income Tax (TDS estimated ~10-20% based on slab)
            annual_salary = emp["salary"]
            if annual_salary > 2000000.0:
                tds_rate = 0.20
            elif annual_salary > 1000000.0:
                tds_rate = 0.15
            elif annual_salary > 500000.0:
                tds_rate = 0.08
            else:
                tds_rate = 0.02
            tax = round(gross_salary * tds_rate, 2)

            # Unpaid leave deduction (occasional)
            unpaid_leave_days = 1.0 if random.random() < 0.04 else 0.0
            leave_deduction = round((monthly_base / 22.0) * unpaid_leave_days, 2)

            deductions = round(pf + tax + leave_deduction, 2)
            net_salary = round(gross_salary - deductions, 2)

            assert net_salary > 0, f"Net salary cannot be negative for {eid}"

            payroll_records.append({
                "payroll_id": f"PAY{pay_counter:06d}",
                "employee_id": eid,
                "month": month_str,
                "base_salary": monthly_base,
                "overtime_pay": overtime_pay,
                "leave_deduction": leave_deduction,
                "incentives": incentives,
                "bonuses": bonuses,
                "gross_salary": gross_salary,
                "deductions": deductions,
                "net_salary": net_salary,
                "payment_status": "Paid" if month_str < "2026-03" else "Processed",
                "payment_date": pay_date
            })
            pay_counter += 1

    return payroll_records

def generate_performance_reviews(employees):
    """
    Generates realistic performance appraisal records for employees.
    Realistic normal distribution of KPI and productivity scores.
    """
    reviews = []
    rev_counter = 1

    ratings = [
        (90, 100, "Outstanding", "Consistently exceeds goals, exhibits exceptional technical leadership, and drives positive team impact."),
        (80, 89, "Exceeds Expectations", "Delivers high quality output ahead of schedule, proactive problem solver and reliable collaborator."),
        (68, 79, "Meets Expectations", "Consistently accomplishes assigned objectives in alignment with sprint requirements and standard benchmarks."),
        (55, 67, "Needs Improvement", "Output is acceptable but requires frequent supervisor guidance and attention to deadlines."),
        (35, 54, "Unsatisfactory", "Fails to meet core deliverables; placed on targeted performance improvement plan.")
    ]

    for emp in employees:
        eid = emp["employee_id"]
        mgr_id = emp["manager_id"] or "EMP001"

        # Gaussian score around 78
        score = int(random.gauss(78, 12))
        score = max(40, min(98, score))

        goal_comp = round(min(100.0, score + random.uniform(-5.0, 5.0)), 1)
        prod_score = round(min(100.0, score + random.uniform(-4.0, 4.0)), 1)

        for low, high, rating, feedback in ratings:
            if low <= score <= high:
                selected_rating = rating
                selected_feedback = feedback
                break
        else:
            selected_rating = "Meets Expectations"
            selected_feedback = "Steady performer meeting expectations."

        reviews.append({
            "review_id": f"REV{rev_counter:05d}",
            "employee_id": eid,
            "kpi_score": float(score),
            "goal_completion": goal_comp,
            "productivity_score": prod_score,
            "manager_feedback": selected_feedback,
            "performance_rating": selected_rating,
            "review_date": "2025-12-15",
            "reviewer_id": mgr_id
        })
        rev_counter += 1

    return reviews

def generate_training_data(employees):
    """Generates training completions and recommendations."""
    trainings = []
    recommendations = []
    tr_counter = 1
    rec_counter = 1

    for emp in employees:
        eid = emp["employee_id"]
        
        # 1-2 completed trainings
        num_tr = random.randint(1, 2)
        chosen_courses = random.sample(TRAINING_COURSES, num_tr)
        for c in chosen_courses:
            score = round(random.uniform(70.0, 98.0), 1)
            trainings.append({
                "training_id": f"TRN{tr_counter:05d}",
                "employee_id": eid,
                "training_name": c["name"],
                "skill": c["skill"],
                "completion_status": "Completed",
                "start_date": "2025-11-01",
                "completion_date": "2025-11-30",
                "score": score
            })
            tr_counter += 1

        # 1 AI recommendation based on skill gap
        rec_course = random.choice(TRAINING_COURSES)
        recommendations.append({
            "recommendation_id": f"REC{rec_counter:05d}",
            "employee_id": eid,
            "recommended_course": rec_course["name"],
            "target_skill": rec_course["skill"],
            "reason": "AI Skill Gap Analysis: Recommended for career progression and upcoming project requirements.",
            "created_at": "2026-01-10 10:00:00"
        })
        rec_counter += 1

    return trainings, recommendations

def generate_notifications(employees):
    """Generates notifications for employees across all categories."""
    notifications = []
    notif_counter = 1

    categories = [
        ("Shift reminder", "Upcoming Shift Schedule", "Your General Shift schedule is confirmed for tomorrow 09:00 AM."),
        ("Leave approval", "Leave Request Approved", "Your leave application has been approved by your reporting manager."),
        ("Attendance alert", "Attendance Verification", "Your biometric clock-in was recorded at 08:55 AM."),
        ("Timesheet reminder", "Weekly Timesheet Submission Due", "Please complete and submit your weekly project timesheet before Friday 6 PM."),
        ("Birthday", "Happy Birthday!", "The team wishes you a wonderful birthday and a great year ahead!"),
        ("Work anniversary", "Happy Work Anniversary!", "Congratulations on completing another successful year with InnovateCorp!"),
        ("Payroll notification", "Salary Credited", "Your monthly salary for February 2026 has been processed and credited to your registered bank account.")
    ]

    for emp in employees:
        eid = emp["employee_id"]
        # Generate 2-3 notifications per employee
        for cat, title, msg in random.sample(categories, 3):
            notifications.append({
                "notification_id": f"NOT{notif_counter:06d}",
                "employee_id": eid,
                "category": cat,
                "title": title,
                "message": msg,
                "is_read": 1 if random.random() < 0.65 else 0,
                "created_at": "2026-03-18 09:30:00"
            })
            notif_counter += 1

    return notifications

def generate_user_accounts(employees):
    """
    Creates authentication user accounts for all employees, plus explicit DEMO accounts:
    - hr@demo.com -> HR role (EMP003)
    - manager@demo.com -> MANAGER role (EMP002)
    - employee@demo.com -> EMPLOYEE role (EMP050)
    - admin@demo.com -> ADMIN role (EMP001)
    All demo passwords hashed: Demo@2026
    """
    accounts = []
    demo_password_hash = hash_password("Demo@2026")

    # Fixed demo mappings
    demo_mappings = [
        {"email": "admin@demo.com", "employee_id": "EMP001", "role": "ADMIN"},
        {"email": "manager@demo.com", "employee_id": "EMP002", "role": "MANAGER"},
        {"email": "hr@demo.com", "employee_id": "EMP003", "role": "HR"},
        {"email": "employee@demo.com", "employee_id": "EMP050", "role": "EMPLOYEE"},
    ]

    acc_id = 1
    # 1. Create the 4 dedicated demo accounts first
    for demo in demo_mappings:
        accounts.append({
            "user_id": f"USR{acc_id:04d}",
            "employee_id": demo["employee_id"],
            "email": demo["email"],
            "password_hash": demo_password_hash,
            "role": demo["role"],
            "is_active": 1,
            "created_at": "2025-01-01 00:00:00"
        })
        acc_id += 1

    # 2. Create standard user accounts for all 200 employees using their employee email
    for emp in employees:
        accounts.append({
            "user_id": f"USR{acc_id:04d}",
            "employee_id": emp["employee_id"],
            "email": emp["email"],
            "password_hash": demo_password_hash,
            "role": emp["role"],
            "is_active": 1,
            "created_at": "2025-01-01 00:00:00"
        })
        acc_id += 1

    return accounts

# ---------------------------------------------------------
# Database Loading & Export
# ---------------------------------------------------------

def load_data_to_sqlite(all_data):
    """Executes schema.sql and loads all generated dataset records into SQLite."""
    print(f"Connecting to database: {DB_PATH}")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    cursor.executescript(schema_sql)

    # 1. Locations
    cursor.executemany("""
        INSERT INTO locations (location_id, name, city, state, country, latitude, longitude, geofence_radius_meters, timezone)
        VALUES (:location_id, :name, :city, :state, :country, :latitude, :longitude, :geofence_radius_meters, :timezone)
    """, all_data["locations"])

    # 2. Departments
    cursor.executemany("""
        INSERT INTO departments (department_id, name, code, description, head_employee_id, budget)
        VALUES (:department_id, :name, :code, :description, :head_employee_id, :budget)
    """, all_data["departments"])

    # 3. Shifts
    cursor.executemany("""
        INSERT INTO shifts (shift_id, shift_name, start_time, end_time, grace_period_mins, is_rotational)
        VALUES (:shift_id, :shift_name, :start_time, :end_time, :grace_period_mins, :is_rotational)
    """, all_data["shifts"])

    # 4. Employees
    cursor.executemany("""
        INSERT INTO employees (
            employee_id, first_name, last_name, gender, date_of_birth, email, phone, address,
            joining_date, employment_type, designation, department_id, manager_id, location_id,
            salary, experience, employment_status, role
        ) VALUES (
            :employee_id, :first_name, :last_name, :gender, :date_of_birth, :email, :phone, :address,
            :joining_date, :employment_type, :designation, :department_id, :manager_id, :location_id,
            :salary, :experience, :employment_status, :role
        )
    """, all_data["employees"])

    # 5. Skills
    cursor.executemany("""
        INSERT INTO skills (skill_id, skill_name, category)
        VALUES (:skill_id, :skill_name, :category)
    """, all_data["skills"])

    # 6. Employee Skills
    cursor.executemany("""
        INSERT INTO employee_skills (employee_id, skill_id, proficiency_level, years_experience)
        VALUES (:employee_id, :skill_id, :proficiency_level, :years_experience)
    """, all_data["employee_skills"])

    # 7. Projects
    cursor.executemany("""
        INSERT INTO projects (project_id, project_name, client_name, department_id, start_date, end_date, status, budget)
        VALUES (:project_id, :project_name, :client_name, :department_id, :start_date, :end_date, :status, :budget)
    """, all_data["projects"])

    # 8. Employee Projects
    cursor.executemany("""
        INSERT INTO employee_projects (assignment_id, employee_id, project_id, role, allocation_percentage, start_date, end_date)
        VALUES (:assignment_id, :employee_id, :project_id, :role, :allocation_percentage, :start_date, :end_date)
    """, all_data["employee_projects"])

    # 9. Employee Shifts
    cursor.executemany("""
        INSERT INTO employee_shifts (schedule_id, employee_id, shift_id, effective_from, effective_to)
        VALUES (:schedule_id, :employee_id, :shift_id, :effective_from, :effective_to)
    """, all_data["employee_shifts"])

    # 10. Attendance
    cursor.executemany("""
        INSERT INTO attendance (
            attendance_id, employee_id, date, check_in, check_out, attendance_status,
            attendance_method, location_id, late_minutes, overtime_hours, shift_id,
            anomaly_flag, anomaly_reason
        ) VALUES (
            :attendance_id, :employee_id, :date, :check_in, :check_out, :attendance_status,
            :attendance_method, :location_id, :late_minutes, :overtime_hours, :shift_id,
            :anomaly_flag, :anomaly_reason
        )
    """, all_data["attendance"])

    # 11. Leave Balances
    cursor.executemany("""
        INSERT INTO leave_balances (balance_id, employee_id, leave_type, allocated_days, used_days, remaining_days, year)
        VALUES (:balance_id, :employee_id, :leave_type, :allocated_days, :used_days, :remaining_days, :year)
    """, all_data["leave_balances"])

    # 12. Leave Requests
    cursor.executemany("""
        INSERT INTO leave_requests (leave_id, employee_id, leave_type, start_date, end_date, days_count, reason, status, approved_by, created_at)
        VALUES (:leave_id, :employee_id, :leave_type, :start_date, :end_date, :days_count, :reason, :status, :approved_by, :created_at)
    """, all_data["leave_requests"])

    # 13. Timesheets
    cursor.executemany("""
        INSERT INTO timesheets (timesheet_id, employee_id, date, project_id, hours_worked, billable_hours, non_billable_hours, overtime_hours, status)
        VALUES (:timesheet_id, :employee_id, :date, :project_id, :hours_worked, :billable_hours, :non_billable_hours, :overtime_hours, :status)
    """, all_data["timesheets"])

    # 14. Payroll
    cursor.executemany("""
        INSERT INTO payroll (
            payroll_id, employee_id, month, base_salary, overtime_pay, leave_deduction,
            incentives, bonuses, gross_salary, deductions, net_salary, payment_status, payment_date
        ) VALUES (
            :payroll_id, :employee_id, :month, :base_salary, :overtime_pay, :leave_deduction,
            :incentives, :bonuses, :gross_salary, :deductions, :net_salary, :payment_status, :payment_date
        )
    """, all_data["payroll"])

    # 15. Performance Reviews
    cursor.executemany("""
        INSERT INTO performance_reviews (review_id, employee_id, kpi_score, goal_completion, productivity_score, manager_feedback, performance_rating, review_date, reviewer_id)
        VALUES (:review_id, :employee_id, :kpi_score, :goal_completion, :productivity_score, :manager_feedback, :performance_rating, :review_date, :reviewer_id)
    """, all_data["performance_reviews"])

    # 16. Training Records
    cursor.executemany("""
        INSERT INTO training_records (training_id, employee_id, training_name, skill, completion_status, start_date, completion_date, score)
        VALUES (:training_id, :employee_id, :training_name, :skill, :completion_status, :start_date, :completion_date, :score)
    """, all_data["training_records"])

    # 17. Training Recommendations
    cursor.executemany("""
        INSERT INTO training_recommendations (recommendation_id, employee_id, recommended_course, target_skill, reason, created_at)
        VALUES (:recommendation_id, :employee_id, :recommended_course, :target_skill, :reason, :created_at)
    """, all_data["training_recommendations"])

    # 18. Company Holidays
    cursor.executemany("""
        INSERT INTO company_holidays (holiday_id, holiday_name, date, location_id)
        VALUES (:holiday_id, :holiday_name, :date, :location_id)
    """, all_data["company_holidays"])

    # 19. Notifications
    cursor.executemany("""
        INSERT INTO notifications (notification_id, employee_id, category, title, message, is_read, created_at)
        VALUES (:notification_id, :employee_id, :category, :title, :message, :is_read, :created_at)
    """, all_data["notifications"])

    # 20. User Accounts
    cursor.executemany("""
        INSERT INTO user_accounts (user_id, employee_id, email, password_hash, role, is_active, created_at)
        VALUES (:user_id, :employee_id, :email, :password_hash, :role, :is_active, :created_at)
    """, all_data["user_accounts"])

    conn.commit()
    conn.close()
    print("Database populated successfully.")

def save_json_fixtures(all_data):
    """Saves generated entities to JSON fixture files."""
    print("Saving JSON fixtures...")
    for entity_name, records in all_data.items():
        file_path = os.path.join(FIXTURES_DIR, f"{entity_name}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
    
    # Save combined snapshot
    combined_path = os.path.join(DATA_DIR, "all_synthetic_data.json")
    with open(combined_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)
    print("All fixtures written to data/fixtures/.")

# ---------------------------------------------------------
# Main Execution
# ---------------------------------------------------------

def main():
    print("=" * 60)
    print("AI WORKFORCE MANAGEMENT SYSTEM - SYNTHETIC DATA GENERATOR")
    print(f"Random Seed: {SEED}")
    print("=" * 60)

    # 1. Employees & Departments
    print("1. Generating 200 Employees & Department Hierarchy...")
    employees, dept_head_ids = generate_employees()
    print(f"   Generated {len(employees)} employees (EMP001 - EMP200)")

    # Update department head_employee_ids
    departments = []
    for dept in DEPARTMENTS:
        d = dict(dept)
        d["head_employee_id"] = dept_head_ids.get(d["department_id"])
        departments.append(d)

    # 2. Employee Skills
    print("2. Generating Skills & Employee Skills Mapping...")
    emp_skills = generate_employee_skills(employees)

    # 3. Shifts & Schedules
    print("3. Generating Shifts & Schedules...")
    shift_assignments = generate_shift_assignments(employees)
    shift_map = {sa["employee_id"]: sa["shift_id"] for sa in shift_assignments}

    # 4. Project Assignments
    print("4. Generating Projects & Team Staffing...")
    project_assignments = generate_project_assignments(employees)

    # 5. Attendance (~6 months)
    print("5. Generating 6-month Attendance Log (~24,000+ records)...")
    attendance = generate_attendance_data(employees, shift_map)
    print(f"   Generated {len(attendance)} attendance entries")

    # 6. Leave Balances & Requests
    print("6. Generating Leave Balances & Requests...")
    leave_balances, leave_requests = generate_leave_data(employees)

    # 7. Timesheets
    print("7. Generating Timesheets...")
    timesheets = generate_timesheet_data(employees, project_assignments)

    # 8. Payroll Inputs (6 months)
    print("8. Generating Payroll Inputs (Oct 2025 - Mar 2026)...")
    payroll = generate_payroll_data(employees)
    print(f"   Generated {len(payroll)} payroll records (200 employees x 6 months)")

    # 9. Performance Reviews
    print("9. Generating Performance Appraisals...")
    performance_reviews = generate_performance_reviews(employees)

    # 10. Training Records
    print("10. Generating Training Records & Skill Gap Recommendations...")
    trainings, recommendations = generate_training_data(employees)

    # 11. Notifications
    print("11. Generating System Notifications...")
    notifications = generate_notifications(employees)

    # 12. User Accounts
    print("12. Generating Authentication User Accounts (inc. demo users)...")
    user_accounts = generate_user_accounts(employees)

    all_data = {
        "locations": LOCATIONS,
        "departments": departments,
        "shifts": SHIFTS,
        "employees": employees,
        "skills": SKILLS_CATALOG,
        "employee_skills": emp_skills,
        "projects": PROJECTS_DATA,
        "employee_projects": project_assignments,
        "employee_shifts": shift_assignments,
        "attendance": attendance,
        "leave_balances": leave_balances,
        "leave_requests": leave_requests,
        "timesheets": timesheets,
        "payroll": payroll,
        "performance_reviews": performance_reviews,
        "training_records": trainings,
        "training_recommendations": recommendations,
        "company_holidays": HOLIDAYS,
        "notifications": notifications,
        "user_accounts": user_accounts
    }

    # Export to JSON
    save_json_fixtures(all_data)

    # Populate SQLite Database
    load_data_to_sqlite(all_data)

    print("=" * 60)
    print("SYNTHETIC DATA GENERATION COMPLETE!")
    print(f"Total Employees: {len(employees)}")
    print(f"Total Attendance Records: {len(attendance)}")
    print(f"Total Payroll Records: {len(payroll)}")
    print(f"Database File: {DB_PATH}")
    print("=" * 60)

if __name__ == "__main__":
    main()
