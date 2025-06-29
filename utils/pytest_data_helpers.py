# utils/pytest_data_helpers.py
"""Data provider utilities for pytest data-driven testing"""

import pytest
import pandas as pd
from typing import List, Callable, Optional, Union
from pathlib import Path
import logging

from config.settings import Settings

# Setup logger
logger = logging.getLogger(__name__)


def csv_data_provider(
    file_path: str, filter_func: Optional[Callable] = None, test_name_column: str = "testcase", delimiter: str = ",", encoding: str = "utf-8"
):
    """
    Decorator để cung cấp dữ liệu test từ file CSV

    Args:
        file_path: Đường dẫn đến file CSV
        filter_func: Hàm tùy chọn để lọc dữ liệu (nhận DataFrame làm tham số)
        test_name_column: Tên cột chứa tên testcase để hiển thị trong báo cáo
        delimiter: Ký tự phân tách các trường trong file
        encoding: Mã hóa của file

    Returns:
        Pytest parametrize decorator với dữ liệu từ file CSV

    Raises:
        FileNotFoundError: Khi file không tồn tại
        pd.errors.EmptyDataError: Khi file CSV rỗng
        pd.errors.ParserError: Khi có lỗi parse CSV
    """

    def decorator(test_function):
        try:
            # Đọc dữ liệu từ file CSV vào DataFrame
            full_path = Settings.get_test_data_path(file_path)

            if not full_path.exists():
                raise FileNotFoundError(f"Test data file not found: {full_path}")

            logger.info(f"Loading CSV data from: {full_path}")
            df = pd.read_csv(full_path, delimiter=delimiter, encoding=encoding)

            if df.empty:
                logger.warning(f"CSV file is empty: {full_path}")
                return pytest.mark.skip(reason="No test data available")(test_function)

            # Áp dụng filter nếu có
            if filter_func:
                logger.debug(f"Applying filter function: {filter_func.__name__}")
                df = filter_func(df)

                if df.empty:
                    logger.warning("No data remaining after filtering")
                    return pytest.mark.skip(reason="No test data after filtering")(test_function)

            # Chuyển DataFrame thành list các dict
            test_data = df.fillna("").to_dict("records")

            # Tạo parameter ids để hiển thị trong báo cáo test
            ids = [f"{i + 1}-{row.get(test_name_column, f'row{i + 1}')}" for i, row in enumerate(test_data)]

            logger.info(f"Loaded {len(test_data)} test cases from CSV")

            # Áp dụng pytest.mark.parametrize cho hàm test
            return pytest.mark.parametrize("test_data", test_data, ids=ids)(test_function)

        except Exception as e:
            logger.error(f"Error loading CSV data: {e}")
            raise

    return decorator


def excel_data_provider(file_path: str, sheet_name: Union[str, int] = 0, filter_func: Optional[Callable] = None, test_name_column: str = "testcase"):
    """
    Decorator để cung cấp dữ liệu test từ file Excel

    Args:
        file_path: Đường dẫn đến file Excel
        sheet_name: Tên hoặc index của sheet
        filter_func: Hàm tùy chọn để lọc dữ liệu (nhận DataFrame làm tham số)
        test_name_column: Tên cột chứa tên testcase để hiển thị trong báo cáo

    Returns:
        Pytest parametrize decorator với dữ liệu từ file Excel

    Raises:
        FileNotFoundError: Khi file không tồn tại
        ValueError: Khi sheet không tồn tại
    """

    def decorator(test_function):
        try:
            # Đọc dữ liệu từ file Excel vào DataFrame
            full_path = Settings.get_test_data_path(file_path)

            if not full_path.exists():
                raise FileNotFoundError(f"Test data file not found: {full_path}")

            logger.info(f"Loading Excel data from: {full_path}, sheet: {sheet_name}")
            df = pd.read_excel(full_path, sheet_name=sheet_name, engine="openpyxl")

            if df.empty:
                logger.warning(f"Excel sheet is empty: {full_path}")
                return pytest.mark.skip(reason="No test data available")(test_function)

            # Áp dụng filter nếu có
            if filter_func:
                logger.debug(f"Applying filter function: {filter_func.__name__}")
                df = filter_func(df)

                if df.empty:
                    logger.warning("No data remaining after filtering")
                    return pytest.mark.skip(reason="No test data after filtering")(test_function)

            # Chuyển DataFrame thành list các dict
            test_data = df.fillna("").to_dict("records")

            # Tạo parameter ids để hiển thị trong báo cáo test
            ids = [f"{i + 1}-{row.get(test_name_column, f'row{i + 1}')}" for i, row in enumerate(test_data)]

            logger.info(f"Loaded {len(test_data)} test cases from Excel")

            # Áp dụng pytest.mark.parametrize cho hàm test
            return pytest.mark.parametrize("test_data", test_data, ids=ids)(test_function)

        except Exception as e:
            logger.error(f"Error loading Excel data: {e}")
            raise

    return decorator


def combined_filter(*filters: Callable) -> Callable:
    """
    Kết hợp nhiều filter với logic AND

    Args:
        *filters: Các filter function cần kết hợp

    Returns:
        Hàm filter kết hợp

    Raises:
        ValueError: Khi không có filter nào được cung cấp
    """
    if not filters:
        raise ValueError("At least one filter must be provided")

    def filter_func(df: pd.DataFrame) -> pd.DataFrame:
        result_df = df.copy()
        for filter_fn in filters:
            if callable(filter_fn):
                result_df = filter_fn(result_df)
                if result_df.empty:
                    break
        return result_df

    return filter_func


def _create_generic_filter(column_name: str, use_exact_match: bool = True) -> Callable:
    """
    Tạo generic filter function để tránh code duplication

    Args:
        column_name: Tên cột cần filter
        use_exact_match: True để dùng exact match, False để dùng contains

    Returns:
        Filter function
    """

    def filter_creator(value: Union[str, List[str]]) -> Callable:
        def filter_func(df: pd.DataFrame) -> pd.DataFrame:
            if column_name not in df.columns:
                logger.warning(f"Column '{column_name}' not found in DataFrame")
                return df

            if isinstance(value, list):
                if use_exact_match:
                    return df[df[column_name].isin(value)]
                else:
                    mask = df[column_name].apply(lambda x: any(item in str(x) for item in value))
                    return df[mask]
            else:
                if use_exact_match:
                    return df[df[column_name] == value]
                else:
                    return df[df[column_name].str.contains(str(value), na=False)]

        return filter_func

    return filter_creator


# Sử dụng generic filter để tạo các filter cụ thể
def filter_by_category(category: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên category

    Args:
        category: Tên category hoặc list các category để lọc

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("category", use_exact_match=True)(category)


def filter_by_field(field: Union[str, List[str]]) -> Callable:
    return _create_generic_filter("field", use_exact_match=True)(field)


def filter_by_test_function(test_function: Union[str, List[str]]) -> Callable:
    return _create_generic_filter("test_function", use_exact_match=True)(test_function)


def filter_by_expected_message(expected_message: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên expected_message

    Args:
        expected_message: Tên expected_message hoặc list các expected_message để lọc

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("expected_message", use_exact_match=False)(expected_message)


def filter_by_field(field: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên field

    Args:
        field: Tên field hoặc list các field để lọc

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("field", use_exact_match=False)(field)


def filter_by_expected_result(expected_result: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên expected_result

    Args:
        expected_result: Kết quả mong đợi để lọc

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("expected_result", use_exact_match=False)(expected_result)


def filter_by_test_function(test_function: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên test_function

    Args:
        test_function: Tên test function để lọc

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("test_function", use_exact_match=False)(test_function)


def filter_by_test_type(test_type: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên test_type

    Args:
        test_type: Loại test để lọc (ví dụ: 'positive', 'negative', 'boundary')

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("test_type", use_exact_match=True)(test_type)


def filter_by_priority(priority: Union[str, List[str]]) -> Callable:
    """
    Hàm tiện ích để tạo filter function dựa trên priority

    Args:
        priority: Độ ưu tiên để lọc (ví dụ: 'high', 'medium', 'low')

    Returns:
        Hàm filter nhận DataFrame làm tham số
    """
    return _create_generic_filter("priority", use_exact_match=True)(priority)
