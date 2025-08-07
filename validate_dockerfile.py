#!/usr/bin/env python3
"""
Script to validate Dockerfile structure and best practices
Tests Dockerfile without requiring Docker runtime
"""
import os
import re

def validate_dockerfile_exists():
    """Check if Dockerfile exists"""
    if os.path.exists('Dockerfile'):
        print("✅ Dockerfile exists")
        return True
    else:
        print("❌ Dockerfile not found")
        return False

def validate_dockerfile_content():
    """Validate Dockerfile content and structure"""
    print("🔍 Validating Dockerfile content...")
    
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    checks = []
    
    # Check for AWS Lambda base image
    if 'public.ecr.aws/lambda/python:3.11' in content:
        checks.append(("✅ Uses official AWS Lambda Python base image", True))
    else:
        checks.append(("❌ Does not use official AWS Lambda base image", False))
    
    # Check for multi-stage build
    if 'FROM public.ecr.aws/lambda/python:3.11 as builder' in content:
        checks.append(("✅ Implements multi-stage build", True))
    else:
        checks.append(("❌ Does not implement multi-stage build", False))
    
    # Check for health check
    if 'HEALTHCHECK' in content:
        checks.append(("✅ Includes health check", True))
    else:
        checks.append(("❌ Missing health check", False))
    
    # Check for security configurations (non-root user)
    if 'useradd' in content and 'groupadd' in content:
        checks.append(("✅ Creates non-root user for security", True))
    else:
        checks.append(("❌ Missing non-root user configuration", False))
    
    # Check for Lambda handler
    if 'CMD ["lambda_function.lambda_handler"]' in content:
        checks.append(("✅ Sets correct Lambda handler", True))
    else:
        checks.append(("❌ Missing or incorrect Lambda handler", False))
    
    # Check for environment variables
    if 'ENV PYTHONPATH' in content and 'ENV LOG_LEVEL' in content:
        checks.append(("✅ Sets appropriate environment variables", True))
    else:
        checks.append(("❌ Missing environment variables", False))
    
    # Check for proper file copying
    if 'COPY src/app.py' in content and 'COPY src/lambda_function.py' in content:
        checks.append(("✅ Copies application files correctly", True))
    else:
        checks.append(("❌ Missing application file copying", False))
    
    # Check for requirements installation
    if 'pip install' in content and 'requirements.txt' in content:
        checks.append(("✅ Installs Python dependencies", True))
    else:
        checks.append(("❌ Missing dependency installation", False))
    
    # Print results
    passed = 0
    for message, success in checks:
        print(f"  {message}")
        if success:
            passed += 1
    
    print(f"\n📊 Dockerfile validation: {passed}/{len(checks)} checks passed")
    return passed == len(checks)

def validate_dockerignore():
    """Validate .dockerignore file"""
    print("🔍 Validating .dockerignore...")
    
    if not os.path.exists('.dockerignore'):
        print("❌ .dockerignore file not found")
        return False
    
    with open('.dockerignore', 'r') as f:
        content = f.read()
    
    required_patterns = [
        '__pycache__',
        '*.pyc',
        '.git',
        'tests/',
        '.pytest_cache',
        'venv/',
        '.coverage'
    ]
    
    checks = []
    for pattern in required_patterns:
        if pattern in content:
            checks.append(f"✅ Excludes {pattern}")
        else:
            checks.append(f"❌ Missing exclusion for {pattern}")
    
    for check in checks:
        print(f"  {check}")
    
    passed = len([c for c in checks if c.startswith("✅")])
    print(f"\n📊 .dockerignore validation: {passed}/{len(required_patterns)} patterns found")
    return passed >= len(required_patterns) * 0.8  # Allow 80% pass rate

def validate_application_structure():
    """Validate that required application files exist"""
    print("🔍 Validating application structure...")
    
    required_files = [
        'src/app.py',
        'src/lambda_function.py',
        'src/requirements.txt'
    ]
    
    checks = []
    for file_path in required_files:
        if os.path.exists(file_path):
            checks.append(f"✅ {file_path} exists")
        else:
            checks.append(f"❌ {file_path} missing")
    
    for check in checks:
        print(f"  {check}")
    
    passed = len([c for c in checks if c.startswith("✅")])
    print(f"\n📊 Application structure: {passed}/{len(required_files)} files found")
    return passed == len(required_files)

def validate_requirements_content():
    """Validate requirements.txt has necessary dependencies"""
    print("🔍 Validating requirements.txt content...")
    
    if not os.path.exists('src/requirements.txt'):
        print("❌ requirements.txt not found")
        return False
    
    with open('src/requirements.txt', 'r') as f:
        content = f.read()
    
    required_deps = ['Flask', 'awslambdaric']
    checks = []
    
    for dep in required_deps:
        if dep in content:
            checks.append(f"✅ {dep} dependency found")
        else:
            checks.append(f"❌ {dep} dependency missing")
    
    for check in checks:
        print(f"  {check}")
    
    passed = len([c for c in checks if c.startswith("✅")])
    print(f"\n📊 Requirements validation: {passed}/{len(required_deps)} dependencies found")
    return passed == len(required_deps)

def main():
    """Main validation function"""
    print("🐳 Validating Docker container configuration...")
    print("=" * 50)
    
    tests = [
        ("Dockerfile Existence", validate_dockerfile_exists),
        ("Dockerfile Content", validate_dockerfile_content),
        ("Dockerignore File", validate_dockerignore),
        ("Application Structure", validate_application_structure),
        ("Requirements Content", validate_requirements_content)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} validation passed")
            else:
                print(f"❌ {test_name} validation failed")
        except Exception as e:
            print(f"❌ {test_name} validation error: {str(e)}")
    
    print("\n" + "=" * 50)
    print(f"📊 Validation Results: {passed}/{total} validations passed")
    
    if passed == total:
        print("🎉 All validations passed! Dockerfile is properly configured.")
        print("\n📝 Next steps:")
        print("  1. Build the Docker image: docker build -t lambda-container-api .")
        print("  2. Test locally: python test_container.py")
        print("  3. Push to ECR when ready for deployment")
        return True
    else:
        print("💥 Some validations failed. Please fix issues before building.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)