from enum import Enum

"""
Defines all enumerations used across the application.
Using Enums ensures type safety and prevents typos (e.g., in database queries)
that could occur when using plain strings.
"""

class ExamType(Enum):
    """Represents the different types of examinations available for a module."""
    PRESENTATION = "Presentation"
    WRITTENEXAM = "Written Exam"
    HOMEWORK = "Home Work"
    SEMINARPAPER = "Seminar Paper"
    PORTFOLIO = "Portfolio"
    PROJECT = "Project"
    BACHELORTHESIS = "Bachelor Thesis"
    WORKBOOK = "Workbook"

    @classmethod
    def get_values(cls):
        """Returns all enum values as a list of strings for UI dropdowns."""
        return [e.value for e in cls]

    @classmethod
    def from_value(cls, value: str):
        """Helper to convert a string back to an Enum instance (used when reading from DB)."""
        for e in cls:
            if e.value == value: return e
        return cls.WRITTENEXAM


class StatusType(Enum):
    """Tracks the current progress state of a module."""
    REGISTERED = "Registered"
    IN_PROGRESS = "In Progress"
    PASSED = "Passed"
    NOT_PASSED = "Not Passed"

    @classmethod
    def get_values(cls):
        return [s.value for s in cls]

    @classmethod
    def from_value(cls, value: str):
        for s in cls:
            if s.value == value: return s
        return cls.REGISTERED


class StudyModel(Enum):
    """Defines the time model of the user to calculate realistic graduation forecasts."""
    FULLTIME = "Fulltime"
    PARTTIME_I = "Part Time I"
    PARTTIME_II = "Part Time II"

    @classmethod
    def get_values(cls):
        return [m.value for m in cls]

    @classmethod
    def from_value(cls, value: str):
        for m in cls:
            if m.value == value: return m
        return cls.FULLTIME


class ThemeMode(Enum):
    """Defines the UI appearance mode."""
    LIGHT = "Light"
    DARK = "Dark"