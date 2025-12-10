"""
Test Runner for Air Quality & Health Risk Predictor
Runs all tests and generates coverage report

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --unit       # Run only unit tests
    python run_tests.py --api        # Run only API tests
    python run_tests.py --coverage   # Generate detailed coverage report
"""

import subprocess
import sys
from pathlib import Path
import argparse

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message:^70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def check_requirements():
    """Check if required packages are installed"""
    print_header("Checking Requirements")
    
    required_packages = ['pytest', 'pytest-cov', 'requests']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            missing_packages.append(package)
            print_error(f"{package} is NOT installed")
    
    if missing_packages:
        print_info(f"Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True


def run_tests(test_type='all', coverage=False):
    """Run tests based on type"""
    
    # Base command
    cmd = ['pytest', 'tests/', '-v']
    
    # Add coverage if requested
    if coverage:
        cmd.extend(['--cov=src', '--cov=backend', '--cov-report=html', '--cov-report=term'])
    
    # Filter by test type
    if test_type == 'unit':
        cmd.append('tests/test_health_risk.py')
        cmd.append('tests/test_data_processing.py')
        print_header("Running Unit Tests")
    elif test_type == 'api':
        cmd.append('tests/test_api_endpoints.py')
        print_header("Running API Tests")
    elif test_type == 'integration':
        cmd.append('tests/test_integration.py')
        print_header("Running Integration Tests")
    elif test_type == 'model':
        cmd.append('tests/test_model_predictions.py')
        print_header("Running Model Tests")
    else:
        print_header("Running All Tests")
    
    # Run tests
    try:
        result = subprocess.run(cmd, check=False)
        
        if result.returncode == 0:
            print_success("\nAll tests passed!")
            
            if coverage:
                print_info("\nCoverage report generated: htmlcov/index.html")
                print_info("Open in browser to view detailed coverage")
            
            return True
        else:
            print_error("\nSome tests failed!")
            return False
            
    except FileNotFoundError:
        print_error("pytest not found. Install it with: pip install pytest pytest-cov")
        return False
    except Exception as e:
        print_error(f"Error running tests: {e}")
        return False


def create_test_structure():
    """Create test directory structure if it doesn't exist"""
    print_header("Setting Up Test Structure")
    
    tests_dir = Path("tests")
    tests_dir.mkdir(exist_ok=True)
    print_success(f"Created {tests_dir}/")
    
    # Create __init__.py
    init_file = tests_dir / "__init__.py"
    if not init_file.exists():
        init_file.touch()
        print_success(f"Created {init_file}")
    
    # List of test files to create
    test_files = [
        "conftest.py",
        "test_health_risk.py",
        "test_api_endpoints.py",
        "test_data_processing.py",
        "test_model_predictions.py",
        "test_integration.py"
    ]
    
    for test_file in test_files:
        file_path = tests_dir / test_file
        if not file_path.exists():
            file_path.touch()
            print_info(f"Created empty {file_path}")
        else:
            print_success(f"{file_path} already exists")
    
    print_success("\nTest structure ready!")
    print_info("Copy test code from the comprehensive test suite artifact into these files")


def generate_test_report():
    """Generate a test summary report"""
    print_header("Test Summary Report")
    
    cmd = [
        'pytest', 'tests/', 
        '--tb=no',  # No traceback
        '-q',  # Quiet mode
        '--co'  # Collect only
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print_error(f"Could not generate report: {e}")


def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='Run Air Quality Predictor Tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--api', action='store_true', help='Run only API tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--model', action='store_true', help='Run only model tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--setup', action='store_true', help='Setup test structure')
    parser.add_argument('--check', action='store_true', help='Check requirements only')
    
    args = parser.parse_args()
    
    # Setup test structure if requested
    if args.setup:
        create_test_structure()
        return
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    if args.check:
        return
    
    # Determine test type
    if args.unit:
        test_type = 'unit'
    elif args.api:
        test_type = 'api'
    elif args.integration:
        test_type = 'integration'
    elif args.model:
        test_type = 'model'
    else:
        test_type = 'all'
    
    # Run tests
    success = run_tests(test_type, args.coverage)
    
    # Generate report if all tests passed
    if success:
        generate_test_report()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()