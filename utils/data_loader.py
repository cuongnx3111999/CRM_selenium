# utils/data_loader.py
"""Load test data from various sources (Excel, JSON, CSV)"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional

from config.settings import Settings


class DataLoader:
    """Class để load dữ liệu test từ các file"""

    @staticmethod
    def load_json(filename: str) -> Dict[str, Any]:
        """Load data từ file JSON"""
        file_path = Settings.get_test_data_path(filename)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    @staticmethod
    def load_excel(filename: str, sheet_name: str = 0) -> pd.DataFrame:
        """Load data từ file Excel"""
        file_path = Settings.get_test_data_path(filename)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return pd.read_excel(file_path, sheet_name=sheet_name)

    @staticmethod
    def load_csv(filename: str) -> pd.DataFrame:
        """Load data từ file CSV"""
        file_path = Settings.get_test_data_path(filename)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return pd.read_csv(file_path, encoding='utf-8')

    @staticmethod
    def get_test_users(filename: str = "users.xlsx") -> List[Dict[str, str]]:
        """Load danh sách user test"""
        df = DataLoader.load_excel(filename)
        return df.to_dict('records')

    @staticmethod
    def get_login_data(filename: str = "test_data.json") -> Dict[str, Any]:
        """Load dữ liệu login"""
        data = DataLoader.load_json(filename)
        return data.get('login', {})
