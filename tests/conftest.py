import sys
import os

# Add backend folder to Python path so tests can import db_helper
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))