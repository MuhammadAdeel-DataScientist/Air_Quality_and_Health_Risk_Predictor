"""
Air Quality Predictor - Project Setup Script
Run this to create the complete project structure
"""

import os

def create_project_structure():
    """Creates the complete folder structure for the project"""
    
    # Main project folders
    folders = [
        'data/raw',
        'data/processed',
        'data/models',
        'data/external',
        'notebooks',
        'src/data_pipeline',
        'src/models',
        'src/api',
        'src/utils',
        'src/config',
        'frontend/src',
        'frontend/public',
        'tests',
        'docs',
        'logs',
        'scripts'
    ]
    
    print("Creating project structure...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
        print(f"✓ Created: {folder}")
    
    # Create __init__.py files for Python packages
    init_files = [
        'src/__init__.py',
        'src/data_pipeline/__init__.py',
        'src/models/__init__.py',
        'src/api/__init__.py',
        'src/utils/__init__.py',
        'src/config/__init__.py',
        'tests/__init__.py'
    ]
    
    for init_file in init_files:
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write('"""Package initialization"""')
        print(f"✓ Created: {init_file}")
    
    # Create .gitignore
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Jupyter Notebooks
.ipynb_checkpoints
*.ipynb_checkpoints

# Environment variables
.env
.env.local
config.ini

# Data files
data/raw/*.csv
data/raw/*.json
data/processed/*.csv
data/processed/*.pkl
*.sqlite
*.db

# Models
*.h5
*.pkl
*.joblib
*.pt
*.pth

# Logs
logs/*.log
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# API keys
**/api_keys.txt
**/credentials.json
"""
    
    with open('.gitignore', 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    print("✓ Created: .gitignore")
    
    # Create README.md
    readme_content = """# Air Quality & Health Risk Predictor

## Overview
An end-to-end data science project that predicts air quality and assesses health risks for different demographics using machine learning.

## Features
- Real-time AQI predictions for any location
- 7-day and 30-day forecasts using LSTM and Prophet models
- Health risk assessment for vulnerable groups
- Interactive pollution heatmaps
- Historical trend analysis

## Tech Stack
- **ML/DL**: TensorFlow, Keras, Prophet, Scikit-learn
- **Backend**: FastAPI, PostgreSQL
- **Frontend**: React.js / Streamlit
- **Deployment**: Heroku / AWS
- **APIs**: OpenWeatherMap, IQAir, OpenAQ

## Project Status
Work in Progress

## Getting Started

### Installation
```bash
# Clone the repository
git clone <your-repo-url>
cd air-quality-predictor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Copy `.env.example` to `.env`
2. Add your API keys
3. Run data collection scripts

## Project Structure
```
air-quality-predictor/
├── data/              # Data storage
├── notebooks/         # Jupyter notebooks
├── src/              # Source code
├── frontend/         # Web interface
├── tests/            # Unit tests
└── docs/             # Documentation
```

## Results
Coming soon...

## Author
Your Name - [Your LinkedIn] - [Your Email]

## License
MIT License
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ Created: README.md")
    
    print("\n✅ Project structure created successfully!")
    print("\n📝 Next steps:")
    print("1. Run: python -m venv venv")
    print("2. Activate: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)")
    print("3. Install packages: pip install -r requirements.txt")

if __name__ == "__main__":
    create_project_structure()