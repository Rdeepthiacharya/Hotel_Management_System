import sqlite3
import time
import threading
from typing import List, Tuple, Any, Dict, Union, Optional

class DBController:
    """
    Controller for managing SQLite database connections and operations.
    Includes robust retry logic for handling 'database is locked' errors during transactions.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        # SQLite allows only one writer at a time; serialize writes to avoid "database is locked".
        self._write_lock = threading.Lock()
        self.initialize_db()

    def connect(self) -> sqlite3.Connection:
        """Establishes a connection to the database."""
        # Give SQLite more time to acquire the lock instead of failing immediately.
        conn = sqlite3.connect(self.db_name, timeout=30.0)
        conn.row_factory = sqlite3.Row 

        # Reduce locking/contention issues:
        # - WAL allows concurrent reads while a write transaction is in progress.
        # - busy_timeout makes SQLite wait briefly for the lock instead of failing immediately.
        cur = conn.cursor()
        # Wait for locks briefly before raising "database is locked".
        cur.execute("PRAGMA busy_timeout=15000")
        # journal_mode=WAL can fail if another connection is currently holding locks.
        # It's beneficial, but we don't want to crash the whole app if it can't be applied immediately.
        try:
            cur.execute("PRAGMA journal_mode=WAL")
        except sqlite3.OperationalError:
            pass
        try:
            cur.execute("PRAGMA synchronous=NORMAL")
        except sqlite3.OperationalError:
            pass
        return conn

    def initialize_db(self):
        """Initializes the required tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                mobileno INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rdetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                desc TEXT,
                price REAL,
                image TEXT,
                total_rooms INTEGER,
                available_rooms INTEGER
            )
        """) 

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factdetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                desc TEXT,
                price REAL,
                image TEXT,
                total_slots INTEGER,
                available_slots INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bdetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                telphone INTEGER,
                address TEXT,
                room_type TEXT,
                number_of_rooms INTEGER,
                other_facilities TEXT,
                arrival_date TEXT,
                departure_date TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        if not self.executeQuery("SELECT 1 FROM rdetails LIMIT 1"):
            print("Seeding initial room data...")
            self.insert("rdetails", {"name": "Standard", "desc": "Cozy single room.", "price": 100.00, "image": "room_standard.jpg", "total_rooms": 10, "available_rooms": 10})
            self.insert("rdetails", {"name": "Deluxe", "desc": "Spacious double room with a view.", "price": 150.00, "image": "room_deluxe.jpg", "total_rooms": 5, "available_rooms": 5})
            self.insert("rdetails", {"name": "Suite", "desc": "Luxury suite with separate living area.", "price": 300.00, "image": "room_suite.jpg", "total_rooms": 2, "available_rooms": 2})

        if not self.executeQuery("SELECT 1 FROM factdetails LIMIT 1"):
            print("Seeding initial facility data...")
            self.insert("factdetails", {"name": "Gym", "desc": "Fully equipped fitness center.", "price": 0.00, "image": "facility_gym.jpg", "total_slots": 10, "available_slots": 10})
            self.insert("factdetails", {"name": "Spa", "desc": "Massage and relaxation services.", "price": 50.00, "image": "facility_spa.jpg", "total_slots": 5, "available_slots": 5})
            self.insert("factdetails", {"name": "Private theater", "desc": "Book for a private movie screening.", "price": 75.00, "image": "facility_theater.jpg", "total_slots": 2, "available_slots": 2})

        if not self.executeQuery("SELECT 1 FROM admins LIMIT 1"):
            print("Seeding initial admin user...")
            self.insert("admins", {"username": "admin", "email": "admin@hotel.com", "password": "admin"})

        conn.commit()
        conn.close()

    def executeQuery(self, sql: str) -> List[sqlite3.Row]:
        """Executes a simple read query and returns results."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql)
        results = cursor.fetchall()
        conn.close()
        return results

    def executeQueryWithParams(self, sql: str, params: Optional[List[Any]] = None) -> List[sqlite3.Row]:
        """Executes a read query with parameters and returns results."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(sql, params or [])
        results = cursor.fetchall()
        conn.close()
        return results

    def insert(self, table: str, data: Dict[str, Any]):
        """Inserts a single row of data into a table."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        with self._write_lock:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(sql, list(data.values()))
            conn.commit()
            conn.close()

    def executeTransaction(self, transaction_list: List[Tuple[str, Union[List[Any], Dict[str, Any]]]], max_retries: int = 15) -> bool:
        """
        Executes a list of SQL operations in a single, atomic transaction with robust retry logic 
        for 'database is locked' errors using exponential backoff.
        
        This method is critical for concurrency control.
        """
        # Serialize write attempts in-process; this prevents most "database is locked" cases
        # caused by overlapping requests in multi-threaded execution.
        with self._write_lock:
            for attempt in range(max_retries):
                conn = None
                try:
                    conn = self.connect()
                    cursor = conn.cursor()

                    for sql, params in transaction_list:
                        if isinstance(params, list):
                            cursor.execute(sql, params)
                        elif isinstance(params, dict):
                            cursor.execute(sql, params)
                        else:
                            raise ValueError("Parameters must be a list (positional) or dictionary (named).")

                    conn.commit()
                    return True
                except sqlite3.OperationalError as e:
                    if "database is locked" in str(e):
                        if conn:
                            conn.rollback()

                        # Exponential backoff; cap to keep the total wait reasonable.
                        wait_time = min(2**attempt * 0.1, 2.0)
                        if attempt < max_retries - 1:
                            print(f"--- DB Locked. Retrying in {wait_time:.2f}s... (Attempt {attempt + 1}/{max_retries})")
                            time.sleep(wait_time)
                        else:
                            raise e
                    else:
                        if conn:
                            conn.rollback()
                        raise e
                except Exception as e:
                    if conn:
                        conn.rollback()
                    raise e
                finally:
                    if conn:
                        conn.close()

        return False
