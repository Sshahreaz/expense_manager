import mysql.connector
from mysql.connector import Error
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Ensures connection always closes, even if an error occurs.
    
    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses")
    """
    conn = None
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="expense_manager"
        )
        yield conn
    except Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.debug("Database connection closed")


def get_expenses_by_date(date_str):
    """
    Fetch all expenses for a specific date.
    
    Args:
        date_str (str): Date in format 'YYYY-MM-DD'
    
    Returns:
        list: List of dicts with keys: id, expense_date, category, amount, notes
    
    Raises:
        Exception: If database error occurs
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM expenses WHERE expense_date = %s ORDER BY category"
            cursor.execute(query, (date_str,))
            expenses = cursor.fetchall()
            cursor.close()
            logger.info(f"Retrieved {len(expenses)} expenses for {date_str}")
            return expenses
    except Error as e:
        logger.error(f"Error fetching expenses for {date_str}: {e}")
        raise


def add_or_update_expense(date_str, category, amount, notes=""):
    """
    Add a new expense or update existing one for same date+category.
    
    Args:
        date_str (str): Date in format 'YYYY-MM-DD'
        category (str): Expense category (e.g., 'Food', 'Rent')
        amount (float): Amount in dollars
        notes (str): Optional notes
    
    Returns:
        dict: The inserted/updated row (id, expense_date, category, amount, notes)
    
    Raises:
        Exception: If database error occurs
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Check if expense already exists for this date+category
            check_query = "SELECT id FROM expenses WHERE expense_date = %s AND category = %s"
            cursor.execute(check_query, (date_str, category))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                update_query = "UPDATE expenses SET amount = %s, notes = %s WHERE id = %s"
                cursor.execute(update_query, (amount, notes, existing['id']))
                logger.info(f"Updated expense: {date_str} - {category} - ${amount}")
            else:
                # Insert new
                insert_query = "INSERT INTO expenses (expense_date, category, amount, notes) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (date_str, category, amount, notes))
                logger.info(f"Added expense: {date_str} - {category} - ${amount}")
            
            conn.commit()
            
            # Fetch and return the final row
            fetch_query = "SELECT * FROM expenses WHERE expense_date = %s AND category = %s"
            cursor.execute(fetch_query, (date_str, category))
            result = cursor.fetchone()
            cursor.close()
            
            return result
    except Error as e:
        logger.error(f"Error adding/updating expense: {e}")
        raise


def get_expenses_by_date_range(start_date, end_date):
    """
    Fetch all expenses between two dates (inclusive).
    
    Args:
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
    
    Returns:
        list: List of dicts with expense rows
    
    Raises:
        Exception: If database error occurs
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM expenses WHERE expense_date BETWEEN %s AND %s ORDER BY expense_date, category"
            cursor.execute(query, (start_date, end_date))
            expenses = cursor.fetchall()
            cursor.close()
            logger.info(f"Retrieved {len(expenses)} expenses between {start_date} and {end_date}")
            return expenses
    except Error as e:
        logger.error(f"Error fetching expenses for range {start_date} to {end_date}: {e}")
        raise


def get_categories():
    """
    Fetch all unique expense categories.
    
    Returns:
        list: List of category strings (e.g., ['Food', 'Rent', 'Transport'])
    
    Raises:
        Exception: If database error occurs
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT DISTINCT category FROM expenses ORDER BY category"
            cursor.execute(query)
            categories = [row[0] for row in cursor.fetchall()]
            cursor.close()
            logger.info(f"Retrieved {len(categories)} categories")
            return categories
    except Error as e:
        logger.error(f"Error fetching categories: {e}")
        raise