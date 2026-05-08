import pytest
import sys
import os
from datetime import datetime, timedelta

# conftest.py already added backend to path
import db_helper

# ============================================================================
# FIXTURES (Test Setup)
# ============================================================================

@pytest.fixture
def test_date():
    """Provides a consistent test date"""
    return "2026-05-08"


@pytest.fixture
def test_expense_data():
    """Provides test expense data"""
    return {
        "date": "2026-05-08",
        "category": "Test_Category",
        "amount": 99.99,
        "notes": "Test expense"
    }


# ============================================================================
# TESTS: get_categories()
# ============================================================================

def test_get_categories_returns_list():
    """ARRANGE-ACT-ASSERT: get_categories() returns a list"""
    # ARRANGE: Already have categories in DB from earlier
    
    # ACT
    result = db_helper.get_categories()
    
    # ASSERT
    assert isinstance(result, list), "Result should be a list"
    assert len(result) > 0, "Should have at least one category"


def test_get_categories_contains_strings():
    """Categories should be strings, not dicts or other types"""
    # ARRANGE: (setup implicit)
    
    # ACT
    result = db_helper.get_categories()
    
    # ASSERT
    for category in result:
        assert isinstance(category, str), f"Category should be string, got {type(category)}"


# ============================================================================
# TESTS: get_expenses_by_date()
# ============================================================================

def test_get_expenses_by_date_returns_list(test_date):
    """ARRANGE-ACT-ASSERT: get_expenses_by_date() returns a list"""
    # ARRANGE: Use test_date fixture (2026-05-08)
    
    # ACT
    result = db_helper.get_expenses_by_date(test_date)
    
    # ASSERT
    assert isinstance(result, list), "Result should be a list"


def test_get_expenses_by_date_filters_by_date(test_date):
    """Only expenses matching the date should be returned"""
    # ARRANGE: Get expenses for test_date
    
    # ACT
    result = db_helper.get_expenses_by_date(test_date)
    
    # ASSERT
    for expense in result:
        assert str(expense['expense_date']) == test_date, f"Date mismatch: {expense['expense_date']} != {test_date}"


def test_get_expenses_by_date_has_required_fields():
    """Each expense should have required fields"""
    # ARRANGE
    test_date = "2026-05-08"
    required_fields = ['id', 'expense_date', 'category', 'amount']
    
    # ACT
    result = db_helper.get_expenses_by_date(test_date)
    
    # ASSERT
    if len(result) > 0:  # Only check if there are expenses
        for expense in result:
            for field in required_fields:
                assert field in expense, f"Missing field: {field}"


# ============================================================================
# TESTS: add_or_update_expense()
# ============================================================================

def test_add_or_update_expense_returns_dict(test_expense_data):
    """ARRANGE-ACT-ASSERT: Adding expense returns a dict"""
    # ARRANGE: Use fixture with test data
    
    # ACT
    result = db_helper.add_or_update_expense(
        date_str=test_expense_data["date"],
        category=test_expense_data["category"],
        amount=test_expense_data["amount"],
        notes=test_expense_data["notes"]
    )
    
    # ASSERT
    assert isinstance(result, dict), "Result should be a dict"
    assert result['category'] == test_expense_data["category"]
    assert result['amount'] == test_expense_data["amount"]


def test_add_or_update_expense_creates_new():
    """Adding a new expense should increase count"""
    # ARRANGE
    unique_category = f"TestCategory_{datetime.now().timestamp()}"
    test_date = "2026-05-09"
    
    # ACT: Add new expense
    result = db_helper.add_or_update_expense(
        date_str=test_date,
        category=unique_category,
        amount=50.00,
        notes="Test new expense"
    )
    
    # ASSERT
    assert result is not None
    assert result['category'] == unique_category
    assert result['amount'] == 50.00


def test_add_or_update_expense_updates_existing(test_expense_data):
    """Updating same date+category should update, not create new row"""
    # ARRANGE: Add expense first time
    first_result = db_helper.add_or_update_expense(
        date_str=test_expense_data["date"],
        category=test_expense_data["category"],
        amount=test_expense_data["amount"],
        notes=test_expense_data["notes"]
    )
    first_id = first_result['id']
    
    # ACT: Update the same expense (same date + category)
    updated_result = db_helper.add_or_update_expense(
        date_str=test_expense_data["date"],
        category=test_expense_data["category"],
        amount=199.99,  # Different amount
        notes="Updated test"
    )
    
    # ASSERT: Should be same ID (updated, not new)
    assert updated_result['id'] == first_id, "Should update existing, not create new"
    assert updated_result['amount'] == 199.99, "Amount should be updated"


# ============================================================================
# TESTS: get_expenses_by_date_range()
# ============================================================================

def test_get_expenses_by_date_range_returns_list():
    """ARRANGE-ACT-ASSERT: get_expenses_by_date_range() returns a list"""
    # ARRANGE
    start_date = "2026-05-01"
    end_date = "2026-05-31"
    
    # ACT
    result = db_helper.get_expenses_by_date_range(start_date, end_date)
    
    # ASSERT
    assert isinstance(result, list), "Result should be a list"


def test_get_expenses_by_date_range_filters_dates():
    """Only expenses within range should be returned"""
    # ARRANGE
    start_date = "2026-05-01"
    end_date = "2026-05-31"
    
    # ACT
    result = db_helper.get_expenses_by_date_range(start_date, end_date)
    
    # ASSERT
    for expense in result:
        expense_date_str = str(expense['expense_date'])
        assert expense_date_str >= start_date, f"Date {expense_date_str} is before {start_date}"
        assert expense_date_str <= end_date, f"Date {expense_date_str} is after {end_date}"


# ============================================================================
# INTEGRATION TEST
# ============================================================================

def test_full_workflow():
    """ARRANGE-ACT-ASSERT: Full workflow from add to retrieve"""
    # ARRANGE
    test_date = f"2026-05-{datetime.now().day:02d}"
    unique_category = f"Integration_Test_{datetime.now().timestamp()}"
    test_amount = 123.45
    
    # ACT: Add expense
    added = db_helper.add_or_update_expense(
        date_str=test_date,
        category=unique_category,
        amount=test_amount,
        notes="Integration test"
    )
    
    # ACT: Retrieve expenses for that date
    retrieved = db_helper.get_expenses_by_date(test_date)
    
    # ASSERT: Expense should be in list
    found = False
    for exp in retrieved:
        if exp['category'] == unique_category and exp['amount'] == test_amount:
            found = True
            break
    
    assert found, f"Added expense not found in retrieval"