import sys
from pathlib import Path


def setup_project_path():
    """
    Thêm thư mục gốc của project vào sys.path để dễ dàng import các module.
    """
    project_root = Path(__file__).parent.parent  # Lùi 2 cấp để đến thư mục gốc
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"✅ Đã thêm vào Python path: {project_root}")
    else:
        print(f"⚠️ Thư mục đã có trong Python path: {project_root}")
