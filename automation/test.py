import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("Testing step by step imports...")

# Test 1: Import pages package
try:
    import pages

    print("✅ Import pages - OK")
    print(f"Pages location: {pages.__file__}")
except Exception as e:
    print(f"❌ Import pages failed: {e}")

# Test 2: Import pages.users
try:
    import pages.users

    print("✅ Import pages.users - OK")
    print(f"Users location: {pages.users.__file__}")
except Exception as e:
    print(f"❌ Import pages.users failed: {e}")

# Test 3: Import pages.users.users_page
try:
    import pages.users.users_page

    print("✅ Import pages.users.users_page - OK")
    print(f"Module contents: {dir(pages.users.users_page)}")
except Exception as e:
    print(f"❌ Import pages.users.users_page failed: {e}")

# Test 4: Import UsersPage class
try:
    from pages.users.users_page import UsersPage

    print("✅ Import UsersPage class - OK")
    print(f"UsersPage: {UsersPage}")
except Exception as e:
    print(f"❌ Import UsersPage class failed: {e}")
