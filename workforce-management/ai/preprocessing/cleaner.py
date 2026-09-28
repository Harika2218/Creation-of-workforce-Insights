"""
Data Cleaning and Preprocessing Module
--------------------------------------
Handles data sanitization, null imputation, type validation,
and scaling for HR feature sets.
"""

from typing import Optional, List
import pandas as pd
import numpy as np

class DataCleaner:
    @staticmethod
    def fill_numeric_defaults(df: pd.DataFrame, columns: List[str], default_val: float = 0.0) -> pd.DataFrame:
        df = df.copy()
        for col in columns:
            if col in df.columns:
                df[col] = df[col].fillna(default_val)
        return df

    @staticmethod
    def cap_outliers(df: pd.DataFrame, col: str, lower_quantile: float = 0.01, upper_quantile: float = 0.99) -> pd.DataFrame:
        df = df.copy()
        if col in df.columns and len(df[col].dropna()) > 0:
            low = df[col].quantile(lower_quantile)
            high = df[col].quantile(upper_quantile)
            df[col] = df[col].clip(lower=low, upper=high)
        return df

    @staticmethod
    def parse_time_to_minutes(time_val: Optional[str]) -> Optional[int]:
        """
        Converts 'HH:MM:SS' or 'HH:MM' string to minutes from midnight.
        """
        if not time_val or pd.isna(time_val):
            return None
        try:
            parts = str(time_val).strip().split(':')
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return h * 60 + m
        except (ValueError, IndexError):
            return None
