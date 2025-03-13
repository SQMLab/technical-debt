from enum import Enum


class TechnicalDebtType(Enum):
    NA = 'Na'
    ARCHITECTURE = 'Architecture'
    BUILD = 'Build'
    CODE = 'Code'
    DEFECT = "Defect"
    DESIGN = "Design"
    DOCUMENTATION = "Documentation"
    INFRASTRUCTURE = "Infrastructure"
    PEOPLE = "People"
    PROCESS = "Process"
    REQUIREMENT = "Requirement"
    SERVICE = "Service"
    AUTOMATION = "Automation"
    TEST = "Test"
    UNKNOWN = "Unknown"


print(f"""
            0: Na: Na
            1  Des: Design              8   Pe: People
            2  Def: Defect              9   Pr: Process
            3  Te: Test                 10  Se: Service
            4  Re: Requirement          11  Au: Automation
            5  Ar: Architecture         12  Do: Documentation        
            6  Bu: Build                13  In: Infrastructure               
            7  Co: Code                 14  Un: Unknown                
        """)

DEBT_MAP = {
    '0': 'Na',
    '1': 'Design',
    '2': 'Code',
    '3': 'Test',
    '4': 'Requirement',
    '5': 'Architecture',
    '6': 'Build',
    '7': 'Defect',
    '8': 'People',
    '9': 'Process',
    '10': 'Service',
    '11': 'Automation',
    '12': 'Documentation',
    '13': 'Infrastructure',
    '14': 'Unknown',
    'na': 'Na',
    'ar': 'Architecture',
    'bu': 'Build',
    'co': 'Code',
    'def': 'Defect',
    'des': 'Design',
    'do': 'Documentation',
    'in': 'Infrastructure',
    'pe': 'People',
    'pr': 'Process',
    're': 'Requirement',
    'se': 'Service',
    'au': 'Automation',
    'te': 'Test',
    'un': 'Unknown'
}

def find_debt_type(key):
    key = key.lower()
    return DEBT_MAP.get(key, None)

