import pytest
import pandas as pd
from src.performance_dashboard.utils import load_data
from src.dashboards.app import dummy_dataset

@pytest.fixture
def sample_df():
    user_id = 101
    df = load_data(user_id)
    return df

@pytest.fixture
def processed_data():
    df, skills, dates = dummy_dataset(101)
    return df, skills, dates

def test_df_not_empty(sample_df):
    assert not sample_df.empty
    
def test_df_has_date_column(sample_df):
    assert "Datum" in sample_df.columns

def test_dummy_df_logic(processed_data):
    df, skills, dates = processed_data
    assert isinstance(skills, list)
    assert len(dates) > 0
    assert "Datum" not in skills