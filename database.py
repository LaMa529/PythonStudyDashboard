import sqlite3
from datetime import date
from models import Module, Settings
from enums import ExamType, StatusType, StudyModel


class DatabaseManager:
    """
    Handles all SQLite database interactions.
    This class abstracts the SQL queries away from the main application logic.
    """

    def __init__(self, db_name="study_database.db"):
        self.db_name = db_name
        self.create_tables()

    def connect(self):
        """Establishes and returns a connection to the SQLite database."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Initializes the database schema if it doesn't exist yet."""
        conn = self.connect()
        cursor = conn.cursor()

        # Create modules table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                semester TEXT NOT NULL,
                exam_type TEXT NOT NULL,
                status TEXT NOT NULL,
                ects INTEGER NOT NULL,
                grade REAL,
                website_url TEXT,
                pdf_url TEXT,
                attempt INTEGER DEFAULT 1,
                exam_date TEXT
            )
        ''')

        # Create settings table (restricted to a single row using id=1)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                first_name TEXT, last_name TEXT, study_program TEXT,
                total_ects INTEGER, study_start TEXT, study_model TEXT,
                target_grade REAL, theme TEXT
            )
        ''')

        # Insert default user data if the settings table is completely empty
        cursor.execute('''
            INSERT OR IGNORE INTO settings 
            (id, first_name, last_name, study_program, total_ects, study_start, study_model, target_grade, theme)
            VALUES (1, 'User', '', 'Cyber Security', 180, '2025-04', 'Fulltime', 2.0, 'System')
        ''')

        conn.commit()
        conn.close()

    def add_module(self, module: Module):
        """Inserts a new module record into the database."""
        conn = self.connect()
        cursor = conn.cursor()
        date_str = module.exam_date.isoformat() if module.exam_date else None

        cursor.execute('''
            INSERT INTO modules (name, semester, exam_type, status, ects, grade, website_url, pdf_url, attempt, exam_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (module.name, module.semester, module.exam_type.value, module.status.value,
              module.ects, module.grade, module.website_url, module.pdf_url, module.attempt, date_str))
        conn.commit()
        conn.close()

    def get_modules(self):
        """Fetches all modules from the database and maps them to Module objects."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM modules')
        rows = cursor.fetchall()
        conn.close()

        modules = []
        for row in rows:
            # Parse ISO date string back to date object if available
            d_obj = date.fromisoformat(row[10]) if row[10] else None

            modules.append(Module(
                id=row[0], name=row[1], semester=row[2],
                exam_type=ExamType.from_value(row[3]), status=StatusType.from_value(row[4]),
                ects=row[5], grade=row[6], website_url=row[7], pdf_url=row[8],
                attempt=row[9], exam_date=d_obj
            ))
        return modules

    def update_module(self, module: Module):
        """Updates an existing module record matching the given module ID."""
        conn = self.connect()
        cursor = conn.cursor()
        date_str = module.exam_date.isoformat() if module.exam_date else None

        cursor.execute('''
            UPDATE modules 
            SET name=?, semester=?, exam_type=?, status=?, ects=?, grade=?, website_url=?, pdf_url=?, attempt=?, exam_date=?
            WHERE id=?
        ''', (module.name, module.semester, module.exam_type.value, module.status.value,
              module.ects, module.grade, module.website_url, module.pdf_url,
              module.attempt, date_str, module.id))
        conn.commit()
        conn.close()

    def delete_module(self, module_id: int):
        """Deletes a module record by its ID."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM modules WHERE id=?', (module_id,))
        conn.commit()
        conn.close()

    def get_settings(self):
        """Retrieves the single settings record from the database."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE id=1')
        row = cursor.fetchone()
        conn.close()

        if row:
            return Settings(
                first_name=row[1], last_name=row[2], study_program=row[3],
                total_ects=row[4], study_start=row[5], study_model=StudyModel.from_value(row[6]),
                target_grade=row[7], theme=row[8]
            )
        return None

    def save_settings(self, s: Settings):
        """Overwrites the existing settings record with new values."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE settings 
            SET first_name=?, last_name=?, study_program=?, total_ects=?, study_start=?, study_model=?, target_grade=?, theme=?
            WHERE id=1
        ''', (s.first_name, s.last_name, s.study_program, s.total_ects,
              s.study_start, s.study_model.value, s.target_grade, s.theme))
        conn.commit()
        conn.close()