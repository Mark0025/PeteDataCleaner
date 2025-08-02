#!/bin/bash

# Activate virtual environment
source .venv/bin/activate

# Run Python tests with verbose output
echo "Running Python Tests..."
python3 -m pytest tests/ -v

# Run specific test suites
echo "Running GUI Workflow Tests..."
python3 -m unittest tests/test_gui_workflow.py

# Run data standardization tests
echo "Running Data Standardization Tests..."
python3 -m unittest tests/test_data_standardizer.py

# Run backend tests
echo "Running Backend Tests..."
python3 -m unittest tests/test_backend.py

# Generate test report
echo "Generating Test Report..."
python3 utils/whatsworking.py

# Deactivate virtual environment
deactivate

echo "All tests completed." 