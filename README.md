# Refrigeration Cycles Calculator

A Django web application for calculating refrigeration cycles with thermodynamic properties and COP analysis.

## Features

- Calculate COP (Coefficient of Performance)
- P-h diagram visualization  
- Multiple refrigerant support (R-134a, R-22, R-410A)
- Persian UI with Bootstrap
- Component work analysis

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup Commands

```bash
# 1. Create project directory
mkdir refrigeration
cd refrigeration

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Upgrade pip
python.exe -m pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create Django project
django-admin startproject refrigeration_project .
python manage.py startapp cycles

# 7. Create directories
mkdir templates templates\cycles static media

# 8. Create .env file
echo SECRET_KEY=django-insecure-your-secret-key > .env
echo DEBUG=True >> .env
echo ALLOWED_HOSTS=localhost,127.0.0.1 >> .env

# 9. Database setup
python manage.py makemigrations cycles
python manage.py migrate

# 10. Create superuser (optional)
python manage.py createsuperuser

# 11. Load sample data
python manage.py shell

In Django shell:
python
from cycles.models import Refrigerant
Refrigerant.objects.create(name='R-134a', chemical_formula='CF3CH2F', critical_temp=374.21, critical_pressure=4059280)
Refrigerant.objects.create(name='R-22', chemical_formula='CHClF2', critical_temp=369.3, critical_pressure=4990000)
Refrigerant.objects.create(name='R-410A', chemical_formula='Mix', critical_temp=344.5, critical_pressure=4901200)
exit()

bash
# 12. Run server
python manage.py runserver

Visit: `http://127.0.0.1:8000`

## Troubleshooting

If pip install fails:
bash
pip install --upgrade setuptools wheel
pip install Django matplotlib numpy plotly django-crispy-forms crispy-bootstrap4 Pillow python-decouple
