# Load Flow

### Requirements
- Python3.12
- Poetry

### How to set & run the project
```bash
# Creates a Python virtualenv
python3.12 -m venv .venv

# Activates virtualenv
source .venv/bin/activate

# Install Poetry dependency manager
pip insatll poetry

# Install our project dependencies
poetry install

# We can also install from requirements file
pip install -r requirements.txt

# In case we update dependencies in Poetry we can update requirements file
poetry export --without-hashes --format=requirements.txt > requirements.txt

# To run load_flow we can just 
python src/load_flow.py
```
