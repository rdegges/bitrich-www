#!/usr/bin/env python3
"""Verify that the BitRich setup is correct."""
import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python version: {version.major}.{version.minor}.{version.micro}")
        print("   Required: Python 3.10 or higher")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_files():
    """Check that required files exist."""
    required_files = [
        'app.py',
        'config.py',
        'manage.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'app/__init__.py',
        'app/models.py',
        'app/forms.py',
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} (missing)")
            all_exist = False
    
    return all_exist


def check_imports():
    """Check that key imports work."""
    imports_to_check = [
        ('flask', 'Flask'),
        ('flask_sqlalchemy', 'SQLAlchemy'),
        ('flask_login', 'LoginManager'),
        ('flask_bcrypt', 'Bcrypt'),
        ('flask_wtf', 'FlaskForm'),
        ('dotenv', 'load_dotenv'),
        ('stripe', None),
        ('sendgrid', None),
    ]
    
    all_imported = True
    for module, attr in imports_to_check:
        try:
            mod = __import__(module, fromlist=[attr] if attr else [])
            if attr:
                getattr(mod, attr)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} (not installed)")
            all_imported = False
        except AttributeError:
            print(f"⚠️  {module} (installed but {attr} not found)")
            all_imported = False
    
    return all_imported


def check_env_file():
    """Check if .env file exists."""
    if Path('.env').exists():
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env file not found (copy .env.example to .env)")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("BitRich Setup Verification")
    print("=" * 60)
    
    print("\n📋 Checking Python Version...")
    python_ok = check_python_version()
    
    print("\n📁 Checking Required Files...")
    files_ok = check_files()
    
    print("\n📦 Checking Dependencies...")
    imports_ok = check_imports()
    
    print("\n⚙️  Checking Configuration...")
    env_ok = check_env_file()
    
    print("\n" + "=" * 60)
    if python_ok and files_ok and imports_ok:
        print("✅ Setup verification PASSED!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your API keys")
        print("2. Run: flask --app manage.py init-db")
        print("3. Run: python app.py")
        print("4. Visit: http://localhost:5000")
    else:
        print("❌ Setup verification FAILED")
        print("\nPlease fix the issues above before running the application.")
        if not imports_ok:
            print("\nTo install dependencies, run:")
            print("  pip install -r requirements.txt")
    print("=" * 60)


if __name__ == '__main__':
    main()
