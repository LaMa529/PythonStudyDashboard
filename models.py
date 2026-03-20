from dataclasses import dataclass
from typing import Optional
from datetime import date
from enums import ExamType, StatusType, StudyModel

"""
Contains the data models representing the core business objects.
Python's @dataclass decorator is used here to automatically generate 
boilerplate code like __init__ and __repr__ methods.
"""

@dataclass
class Module:
    """
    Data container for a single university module.
    Maps directly to a row in the 'modules' database table.
    """
    id: int
    name: str
    semester: str
    exam_type: ExamType
    status: StatusType
    ects: int
    grade: Optional[float] = None  # Grade is optional since the exam might not be written yet
    website_url: Optional[str] = None
    pdf_url: Optional[str] = None
    attempt: int = 1
    exam_date: Optional[date] = None

@dataclass
class Settings:
    """
    Data container for the user's global settings and preferences.
    Maps to the single row in the 'settings' database table.
    """
    first_name: str
    last_name: str
    study_program: str
    total_ects: int
    study_start: str
    study_model: StudyModel
    target_grade: float
    theme: str = "System"