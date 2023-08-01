import json
from pathlib import Path

mapping_file_path = Path(__file__).parent.parent / 'data' / 'mapping.json'

with open(mapping_file_path, 'r') as fp:
    mapping = json.load(fp)


compulsory_cols_to_be_mapped = mapping.get('required_columns')
extra_cols_to_be_mapped = mapping.get('extra_cols')

std_date_cols = ['PolicyStartDate',
                 'PolicyEndDate',
                 'DateOfAdmission',
                 'DateOfDischarge']
str_cols = ["AilmentICDCode",
            "Insurer",
            "PolicyStartDate",
            "PolicyEndDate",
            "EmployeeCode",
            "Sex",
            "Relation",
            "ClaimType",
            "ClaimStatus",
            "DateOfAdmission",
            "DateOfDischarge",
            "Location"]
