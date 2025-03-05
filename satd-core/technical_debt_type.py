from enum import Enum


class TechnicalDebtType(Enum):
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
    '1': 'ARCHITECTURE',
    '2': 'BUILD',
    '3': 'CODE',
    '4': 'DEFECT',
    '5': 'DESIGN',
    '6': 'DOCUMENTATION',
    '7': 'INFRASTRUCTURE',
    '8': 'PEOPLE',
    '9': 'PROCESS',
    '10': 'REQUIREMENT',
    '11': 'SERVICE',
    '12': 'AUTOMATION',
    '13': 'TEST',
    '14': 'UNKNOWN',
    'Ar': 'ARCHITECTURE',
    'Bu': 'BUILD',
    'Co': 'CODE',
    'Def': 'DEFECT',
    'Des': 'DESIGN',
    'Do': 'DOCUMENTATION',
    'In': 'INFRASTRUCTURE',
    'Pe': 'PEOPLE',
    'Pr': 'PROCESS',
    'Re': 'REQUIREMENT',
    'Se': 'SERVICE',
    'Au': 'AUTOMATION',
    'Te': 'TEST',
    'Un': 'UNKNOWN'
}


def find_debt_type(key):
    if key in DEBT_MAP:
        return DEBT_MAP[key]
    else:
        return None
