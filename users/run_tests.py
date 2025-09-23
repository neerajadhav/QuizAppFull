#!/usr/bin/env python3
"""
Test runner script for the users microservice.

This script provides various testing modes and configurations:
- Run all tests
- Run specific test categories
- Run with coverage reporting
- Run performance tests
- Run integration tests only
"""

import argparse
import asyncio
import os
import subprocess
import sys
from pathlib import Path


def run_command(command: list, description: str = "") -> int:
    """Run a command and return the exit code."""
    if description:
        print(f"\n🔄 {description}")
        print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=False)
        return result.returncode
    except FileNotFoundError:
        print(f"❌ Command not found: {command[0]}")
        return 1


def ensure_test_db():
    """Ensure test database is set up."""
    print("🗃️  Setting up test database...")
    
    # Set test environment
    os.environ["TESTING"] = "1"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://testuser:testpass@localhost:5432/testdb"
    
    # Run migrations if needed
    return run_command([
        "python", "-m", "alembic", "upgrade", "head"
    ], "Running database migrations for tests")


def run_unit_tests(coverage: bool = True, verbose: bool = False) -> int:
    """Run unit tests."""
    command = ["python", "-m", "pytest"]
    
    if coverage:
        command.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "not integration and not slow",
        "tests/"
    ])
    
    return run_command(command, "Running unit tests")


def run_integration_tests(verbose: bool = False) -> int:
    """Run integration tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "integration",
        "tests/test_integration.py"
    ])
    
    return run_command(command, "Running integration tests")


def run_specific_tests(pattern: str, verbose: bool = False) -> int:
    """Run tests matching a specific pattern."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend(["-k", pattern, "tests/"])
    
    return run_command(command, f"Running tests matching: {pattern}")


def run_auth_tests(verbose: bool = False) -> int:
    """Run authentication-related tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "auth or -k auth",
        "tests/test_auth.py"
    ])
    
    return run_command(command, "Running authentication tests")


def run_rbac_tests(verbose: bool = False) -> int:
    """Run RBAC-related tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "rbac or -k rbac",
        "tests/test_rbac.py"
    ])
    
    return run_command(command, "Running RBAC tests")


def run_profile_tests(verbose: bool = False) -> int:
    """Run profile-related tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "profile or -k profile",
        "tests/test_profile.py"
    ])
    
    return run_command(command, "Running profile tests")


def run_all_tests(coverage: bool = True, verbose: bool = False) -> int:
    """Run all tests."""
    command = ["python", "-m", "pytest"]
    
    if coverage:
        command.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "--cov-report=xml"
        ])
    
    if verbose:
        command.append("-v")
    
    command.append("tests/")
    
    return run_command(command, "Running all tests")


def run_security_tests(verbose: bool = False) -> int:
    """Run security-focused tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "security or -k security",
        "tests/"
    ])
    
    return run_command(command, "Running security tests")


def run_performance_tests(verbose: bool = False) -> int:
    """Run performance tests."""
    command = ["python", "-m", "pytest"]
    
    if verbose:
        command.append("-v")
    
    command.extend([
        "-m", "slow",
        "tests/"
    ])
    
    return run_command(command, "Running performance tests")


def generate_coverage_report() -> int:
    """Generate detailed coverage report."""
    print("📊 Generating coverage report...")
    
    # Generate HTML report
    html_result = run_command([
        "python", "-m", "coverage", "html"
    ], "Generating HTML coverage report")
    
    if html_result == 0:
        print("✅ HTML coverage report generated in htmlcov/")
    
    # Generate terminal report
    terminal_result = run_command([
        "python", "-m", "coverage", "report"
    ], "Generating terminal coverage report")
    
    return max(html_result, terminal_result)


def clean_test_artifacts():
    """Clean test artifacts and cache files."""
    print("🧹 Cleaning test artifacts...")
    
    # Remove pytest cache
    cache_dirs = [".pytest_cache", "__pycache__", "htmlcov", ".coverage"]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            if os.path.isfile(cache_dir):
                os.remove(cache_dir)
                print(f"Removed file: {cache_dir}")
            else:
                import shutil
                shutil.rmtree(cache_dir)
                print(f"Removed directory: {cache_dir}")
    
    # Remove __pycache__ directories recursively
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                cache_path = os.path.join(root, dir_name)
                import shutil
                shutil.rmtree(cache_path)
                print(f"Removed: {cache_path}")


def lint_and_format():
    """Run linting and formatting checks."""
    print("🔍 Running code quality checks...")
    
    # Run flake8 if available
    flake8_result = run_command([
        "python", "-m", "flake8", "app/", "tests/"
    ], "Running flake8 linting")
    
    # Run black formatting check
    black_result = run_command([
        "python", "-m", "black", "--check", "app/", "tests/"
    ], "Checking code formatting with black")
    
    # Run isort import sorting check
    isort_result = run_command([
        "python", "-m", "isort", "--check-only", "app/", "tests/"
    ], "Checking import sorting with isort")
    
    return max(flake8_result, black_result, isort_result)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Test runner for users microservice")
    
    # Test type arguments
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--auth", action="store_true", help="Run authentication tests")
    parser.add_argument("--rbac", action="store_true", help="Run RBAC tests")
    parser.add_argument("--profile", action="store_true", help="Run profile tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    
    # Test configuration arguments
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-k", "--keyword", help="Run tests matching keyword")
    
    # Utility arguments
    parser.add_argument("--setup-db", action="store_true", help="Set up test database")
    parser.add_argument("--coverage-report", action="store_true", help="Generate coverage report only")
    parser.add_argument("--clean", action="store_true", help="Clean test artifacts")
    parser.add_argument("--lint", action="store_true", help="Run linting and formatting checks")
    
    args = parser.parse_args()
    
    # Handle utility commands first
    if args.clean:
        clean_test_artifacts()
        return 0
    
    if args.lint:
        return lint_and_format()
    
    if args.setup_db:
        return ensure_test_db()
    
    if args.coverage_report:
        return generate_coverage_report()
    
    # Ensure test database is ready
    db_setup_result = ensure_test_db()
    if db_setup_result != 0:
        print("❌ Failed to set up test database")
        return db_setup_result
    
    # Determine coverage setting
    use_coverage = not args.no_coverage
    
    # Run appropriate tests
    if args.keyword:
        return run_specific_tests(args.keyword, args.verbose)
    elif args.unit:
        return run_unit_tests(use_coverage, args.verbose)
    elif args.integration:
        return run_integration_tests(args.verbose)
    elif args.auth:
        return run_auth_tests(args.verbose)
    elif args.rbac:
        return run_rbac_tests(args.verbose)
    elif args.profile:
        return run_profile_tests(args.verbose)
    elif args.security:
        return run_security_tests(args.verbose)
    elif args.performance:
        return run_performance_tests(args.verbose)
    elif args.all:
        return run_all_tests(use_coverage, args.verbose)
    else:
        # Default: run unit tests
        print("No specific test type specified. Running unit tests by default.")
        print("Use --help to see all available options.")
        return run_unit_tests(use_coverage, args.verbose)


if __name__ == "__main__":
    sys.exit(main())
