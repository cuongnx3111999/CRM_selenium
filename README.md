🚀 Cài đặt môi trường
Yêu cầu hệ thống
Python 3.10+

Git

Chrome browser (latest version)

Clone và setup dự án
bash
# Clone repository
git clone <repository-url>
cd my-selenium-pytest-framework

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -e .
🧪 Chạy test cases
Lệnh cơ bản
bash
# Chạy tất cả tests (với HTML report mặc định)
pytest

# Chạy theo markers
pytest -m login           # Chỉ test login
pytest -m users           # Chỉ test users

# Chạy theo keyword (tên test function)
pytest -k "test_login"     # Chạy các test có chứa "test_login"
pytest -k "add_user"       # Chạy các test có chứa "add_user"
pytest -k "validate"       # Chạy các test có chứa "validate"
pytest -k "not delete"     # Chạy các test KHÔNG chứa "delete"
pytest -k "login or users" # Chạy test chứa "login" HOẶC "users"

# Chạy song song (cần pytest-xdist)
pytest -n 2              # Chạy 2 process song song

# Retry khi test fail
pytest --reruns 2         # Retry 2 lần khi fail

# Debug mode
pytest --pdb              # Dừng tại breakpoint khi fail
pytest -s                 # Hiển thị print statements

# Chạy interactive mode
pytest -i                 # Tiếp tục chạy dù có lỗi

# Kết hợp options
pytest -m users -k "validate" -n 2 --reruns 1
pytest -k "login and not delete"
📁 Cấu trúc thư mục

my-selenium-pytest-framework/
├── pages/                     # Page Object Model
│   ├── base/                  # Base classes
│   │   ├── baselocators.py    # Base locators
│   │   ├── basepage.py        # Base page operations
│   │   └── baseactions.py     # Base business actions
│   ├── login/                 # Login module
│   │   ├── loginlocators.py   # Login locators
│   │   ├── loginpage.py       # Login page operations
│   │   └── loginactions.py    # Login business logic
│   └── users/                 # Users module
│       ├── userslocators.py   # Users locators
│       ├── userspage.py       # Users page operations
│       └── usersactions.py    # Users business logic
├── utils/                     # Utilities
│   ├── logger.py              # Logging system
│   ├── screenshot.py          # Screenshot capture
│   ├── drivermanager.py       # WebDriver manager
│   └── pytestdatahelpers.py   # Data helpers
├── config/                    # Configuration
│   ├── settings.py            # Main settings
│   └── browserconfig.py       # Browser config
├── tests/                     # Test cases
│   ├── test_login.py          # Login tests
│   └── test_users.py          # Users tests
├── data/                      # Test data
│   ├── datatestlogin.csv      # Login test data
│   └── datatestusers.csv      # Users test data
├── reports/                   # Test reports (auto-generated)
├── logs/                      # Log files
├── conftest.py               # Pytest configuration
├── pyproject.toml            # Project configuration
└── .env.test                 # Environment variables
🎯 Test đầu tiên
bash
# Chạy test login đơn giản
pytest -m login 

# Chạy test users
pytest -m users 

# Chạy test cụ thể theo tên
pytest -k "test_validate_required_fields" 

# Kiểm tra kết quả trong reports/ (tự động tạo theo ngày)
📋 Available Markers
smoke - Các test cơ bản, quan trọng

regression - Bộ test đầy đủ

login - Các test liên quan đến đăng nhập

users - Các test liên quan đến quản lý users

📊 Reports & Logs
HTML Reports: Tự động tạo trong reports/

Logs: Chi tiết trong logs/

Screenshots: Tự động capture khi test fail

- Chưa phát triển xong còn một số lỗi
- Autofill thiếu radio field sẽ phát triển sau 