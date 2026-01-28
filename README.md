# Task Schedule - Local Network Web App

A lightweight Flask web application for your local network.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python models.py
```

3. Run the app:
```bash
python app.py
```

4. Access from any device on your network:
- From this computer: http://localhost:5000
- From other devices: http://YOUR_IP_ADDRESS:5000
  - Find your IP: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)

## Users

Current users:
- **De** - password: percy
- **Michael** - password: percy

To add more users, use `models.add_user()`:
```python
from models import add_user
add_user('FirstName', 'password')
```
