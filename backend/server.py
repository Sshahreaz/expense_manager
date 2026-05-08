from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime, date
import db_helper
from logging_setup import setup_logging

# Initialize logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Expense Manager API",
    description="REST API for tracking expenses by date and category",
    version="1.0"
)

# ============================================================================
# PYDANTIC MODELS (Data Validation) - Pydantic v2 Syntax
# ============================================================================

class Expense(BaseModel):
    """Single expense record"""
    date: str          # Format: YYYY-MM-DD
    category: str
    amount: float
    notes: Optional[str] = ""
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "2025-03-15",
                "category": "Food",
                "amount": 25.50,
                "notes": "Lunch with team"
            }
        }
    )


class ExpenseResponse(BaseModel):
    """Response model when expense is created/updated"""
    id: int
    expense_date: date
    category: str
    amount: float
    notes: Optional[str]


class DateRange(BaseModel):
    """Request model for analytics endpoint"""
    start_date: str    # Format: YYYY-MM-DD
    end_date: str      # Format: YYYY-MM-DD
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "start_date": "2025-03-01",
                "end_date": "2025-03-31"
            }
        }
    )


class AnalyticsSummary(BaseModel):
    """Response model for analytics"""
    total_expense: float
    expense_count: int
    by_category: dict  # {category: total_amount}

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Expense Manager API is running"
    }


@app.get("/expenses/{date}")
def get_expenses(date: str):
    """
    Fetch all expenses for a specific date.
    
    Args:
        date (str): Date in format YYYY-MM-DD
    
    Returns:
        List of expense records
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        expenses = db_helper.get_expenses_by_date(date)
        logger.info(f"GET /expenses/{date} - Retrieved {len(expenses)} expenses")
        return {
            "date": date,
            "expenses": expenses,
            "total": sum(exp['amount'] for exp in expenses)
        }
    except Exception as e:
        logger.error(f"Error fetching expenses for {date}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch expenses")


@app.post("/expenses/{date}")
def add_or_update_expense_endpoint(date: str, expense: Expense):
    """
    Add a new expense or update existing expense for same date+category.
    
    Args:
        date (str): Date in format YYYY-MM-DD
        expense (Expense): Request body with category, amount, notes
    
    Returns:
        The created/updated expense record
    """
    try:
        # Validate date format
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        result = db_helper.add_or_update_expense(
            date_str=date,
            category=expense.category,
            amount=expense.amount,
            notes=expense.notes
        )
        logger.info(f"POST /expenses/{date} - Added/updated {expense.category} for ${expense.amount}")
        return {
            "status": "success",
            "expense": result
        }
    except Exception as e:
        logger.error(f"Error adding/updating expense: {e}")
        raise HTTPException(status_code=500, detail="Failed to add/update expense")


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    """
    Get expense summary for a date range.
    
    Args:
        date_range (DateRange): Request body with start_date and end_date
    
    Returns:
        Total expense, count, and breakdown by category
    """
    try:
        # Validate dates
        datetime.strptime(date_range.start_date, "%Y-%m-%d")
        datetime.strptime(date_range.end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    try:
        expenses = db_helper.get_expenses_by_date_range(
            date_range.start_date,
            date_range.end_date
        )
        
        # Calculate totals
        total_expense = sum(exp['amount'] for exp in expenses)
        
        # Group by category
        by_category = {}
        for exp in expenses:
            cat = exp['category']
            by_category[cat] = by_category.get(cat, 0) + exp['amount']
        
        logger.info(f"Analytics query: {date_range.start_date} to {date_range.end_date} - Total: ${total_expense}")
        
        return {
            "start_date": date_range.start_date,
            "end_date": date_range.end_date,
            "total_expense": round(total_expense, 2),
            "expense_count": len(expenses),
            "by_category": {cat: round(amount, 2) for cat, amount in by_category.items()}
        }
    except Exception as e:
        logger.error(f"Error computing analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to compute analytics")


@app.get("/categories/")
def get_categories():
    """
    Fetch all unique expense categories in the database.
    
    Returns:
        List of category strings
    """
    try:
        categories = db_helper.get_categories()
        logger.info(f"GET /categories/ - Retrieved {len(categories)} categories")
        return {
            "categories": categories
        }
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")