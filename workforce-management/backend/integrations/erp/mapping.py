"""
ERP / SAP Data Mapping Schemas
------------------------------
Standardized, decoupled translation between internal MongoDB models and ERP schemas.
"""

from typing import Dict, Any

class ERPDataMapper:
    """Decoupled mapper between InnovateCorp HR domain and ERP structures."""

    @staticmethod
    def employee_to_sap(emp: Dict[str, Any]) -> Dict[str, Any]:
        """Maps internal employee document to SAP Personnel Record (Infotype 0001/0002)."""
        return {
            "PersonnelNumber": emp.get("employee_id"),
            "FirstName": emp.get("first_name", emp.get("name", "").split()[0] if emp.get("name") else ""),
            "LastName": emp.get("last_name", emp.get("name", "").split()[-1] if emp.get("name") else ""),
            "CompanyCode": "1000",
            "CostCenter": f"CC_{emp.get('department_id', 'GEN')}",
            "OrganizationalUnit": emp.get("department_id"),
            "Position": emp.get("designation"),
            "EmploymentStatus": "3" if emp.get("employment_status") == "Active" else "0",
            "EntryDate": emp.get("joining_date", "").replace("-", "")
        }

    @staticmethod
    def department_to_sap(dept: Dict[str, Any]) -> Dict[str, Any]:
        """Maps internal department document to SAP Cost Center object."""
        return {
            "CostCenter": dept.get("code", dept.get("department_id")),
            "CostCenterName": dept.get("name"),
            "CompanyCode": "1000",
            "ControllingArea": "A000"
        }
