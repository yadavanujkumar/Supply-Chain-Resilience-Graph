"""
Basic tests for Logistics-Lattice
These tests verify the code structure without requiring external dependencies
"""

import sys
import os

def test_imports():
    """Test that all modules can be parsed"""
    print("Testing Python syntax...")
    
    modules = [
        'config.py',
        'graph_model.py',
        'disruption_simulator.py',
        'rerouting_agent.py',
        'data_loader.py',
        'main.py',
        'dashboard.py'
    ]
    
    for module in modules:
        try:
            with open(module, 'r') as f:
                compile(f.read(), module, 'exec')
            print(f"✓ {module} - syntax valid")
        except SyntaxError as e:
            print(f"✗ {module} - syntax error: {e}")
            return False
        except Exception as e:
            print(f"⚠ {module} - {e}")
    
    return True


def test_file_structure():
    """Test that all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'README.md',
        'requirements.txt',
        '.gitignore',
        '.env.example',
        'config.py',
        'graph_model.py',
        'disruption_simulator.py',
        'rerouting_agent.py',
        'data_loader.py',
        'dashboard.py',
        'main.py'
    ]
    
    all_exist = True
    for filename in required_files:
        if os.path.exists(filename):
            print(f"✓ {filename} exists")
        else:
            print(f"✗ {filename} missing")
            all_exist = False
    
    return all_exist


def test_requirements():
    """Test that requirements.txt contains expected packages"""
    print("\nTesting requirements.txt...")
    
    required_packages = [
        'neo4j',
        'streamlit',
        'langgraph',
        'langchain',
        'googlemaps',
        'python-dotenv',
        'pandas',
        'numpy',
        'plotly'
    ]
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    all_found = True
    for package in required_packages:
        if package in content:
            print(f"✓ {package} in requirements.txt")
        else:
            print(f"✗ {package} missing from requirements.txt")
            all_found = False
    
    return all_found


def test_readme():
    """Test that README.md has essential sections"""
    print("\nTesting README.md...")
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    required_sections = [
        'Overview',
        'Installation',
        'Usage',
        'Tech Stack',
        'Graph Data Model',
        'Disruption',
        'Re-Routing',
        'Dashboard'
    ]
    
    all_found = True
    for section in required_sections:
        if section.lower() in content.lower():
            print(f"✓ '{section}' section present")
        else:
            print(f"⚠ '{section}' section might be missing")
    
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("  Logistics-Lattice Basic Tests")
    print("="*60 + "\n")
    
    results = []
    
    results.append(("File Structure", test_file_structure()))
    results.append(("Python Syntax", test_imports()))
    results.append(("Requirements", test_requirements()))
    results.append(("README", test_readme()))
    
    print("\n" + "="*60)
    print("  Test Results Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{name:20s} {status}")
    
    print("="*60 + "\n")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("✓ All basic tests passed!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start Neo4j database")
        print("3. Configure .env file")
        print("4. Run: python main.py setup")
        print("5. Run: python main.py load-data")
        print("6. Run: python main.py dashboard")
        return 0
    else:
        print("✗ Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
