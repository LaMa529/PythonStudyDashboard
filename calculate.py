from datetime import datetime
from models import Settings
from enums import StatusType

"""
Utility module containing all business logic for calculating grades, progress, and forecasts.
Extracting these functions from the GUI classes keeps the architecture clean and testable.
"""


def calculate_average_grade(modules):
    """Calculates the GPA based only on passed modules that have a grade assigned."""
    completed = [m for m in modules if m.status == StatusType.PASSED and m.grade is not None]
    return sum(m.grade for m in completed) / len(completed) if completed else 0.0


def calculate_completed_ects(modules):
    """Sums up the ECTS points of all successfully passed modules."""
    return sum(m.ects for m in modules if m.status == StatusType.PASSED)


def calculate_progress_percentage(modules, settings: Settings):
    """Returns the study progress as a float between 0.0 and 1.0."""
    if settings.total_ects == 0: return 0.0
    return calculate_completed_ects(modules) / settings.total_ects


def calculate_end_date(modules, settings: Settings):
    """
    Predicts the graduation date based on the user's start date and their current pace
    (completed ECTS per month).
    """
    completed_ects = calculate_completed_ects(modules)
    if completed_ects == 0: return "Not enough data"

    try:
        year, month = map(int, settings.study_start.split('-'))
        start_date = datetime(year, month, 1)
    except ValueError:
        return "Invalid Start Date"

    now = datetime.now()
    months_passed = (now.year - start_date.year) * 12 + (now.month - start_date.month)

    if months_passed <= 0: return "Just started"

    ects_per_month = completed_ects / months_passed
    if ects_per_month == 0: return "Pace too slow"

    remaining_ects = settings.total_ects - completed_ects
    months_remaining = int(remaining_ects / ects_per_month)

    # Calculate target year and month
    end_year = now.year + (now.month + months_remaining) // 12
    end_month = (now.month + months_remaining) % 12
    if end_month == 0:
        end_month = 12
        end_year -= 1

    months = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return f"{months[end_month]} {end_year}"


def calculate_needed_grade(modules, target_avg: float):
    """
    Calculates the exact grade needed in the next exam to reach the user's target GPA.
    Returns None if the target is mathematically impossible.
    """
    completed = [m for m in modules if m.status == StatusType.PASSED and m.grade is not None]
    current_sum = sum(m.grade for m in completed)
    needed = (target_avg * (len(completed) + 1)) - current_sum

    if needed < 1.0: return 1.0
    if needed > 6.0: return None
    return needed