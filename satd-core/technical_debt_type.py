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


DEBT_MAP = {
    '0': 'Na',
    '1': 'Architecture',
    '2': 'Build',
    '3': 'Code',
    '4': 'Defect',
    '5': 'DESIGN',
    '6': 'Documentation',
    '7': 'Infrastructure',
    '8': 'People',
    '9': 'Process',
    '10': 'Requirement',
    '11': 'Service',
    '12': 'Automation',
    '13': 'Test',
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
