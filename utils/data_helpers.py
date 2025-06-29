# utils/data_helpers.py
"""Helper functions for test data manipulation"""

import random
import string
from datetime import datetime, timedelta
from faker import Faker
from typing import Dict, List, Any


class DataHelpers:
    """Class chứa các hàm hỗ trợ tạo và xử lý dữ liệu test"""

    def __init__(self, locale: str = 'vi_VN'):
        self.fake = Faker(locale)

    def generate_random_string(self, length: int = 10) -> str:
        """Tạo chuỗi ngẫu nhiên"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_random_email(self) -> str:
        """Tạo email ngẫu nhiên"""
        return self.fake.email()

    def generate_random_phone(self) -> str:
        """Tạo số điện thoại ngẫu nhiên"""
        return self.fake.phone_number()

    def generate_random_name(self) -> str:
        """Tạo tên ngẫu nhiên"""
        return self.fake.name()

    def generate_random_address(self) -> str:
        """Tạo địa chỉ ngẫu nhiên"""
        return self.fake.address()

    def generate_test_user(self) -> Dict[str, str]:
        """Tạo thông tin user test hoàn chỉnh"""
        return {
            'username': f"user_{self.generate_random_string(8)}",
            'email': self.generate_random_email(),
            'password': f"Pass{self.generate_random_string(6)}!",
            'full_name': self.generate_random_name(),
            'phone': self.generate_random_phone(),
            'address': self.generate_random_address()
        }

    def get_future_date(self, days: int = 30) -> str:
        """Lấy ngày trong tương lai"""
        future_date = datetime.now() + timedelta(days=days)
        return future_date.strftime("%Y-%m-%d")

    def get_past_date(self, days: int = 30) -> str:
        """Lấy ngày trong quá khứ"""
        past_date = datetime.now() - timedelta(days=days)
        return past_date.strftime("%Y-%m-%d")

    @staticmethod
    def merge_test_data(*data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Gộp nhiều nguồn dữ liệu test"""
        merged_data = {}
        for data in data_sources:
            merged_data.update(data)
        return merged_data
