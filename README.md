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

## Configuration

Edit `config.py` to change:
- Password for access
- Secret key for sessions

## Default Password

Change the password in `config.py` (currently set to "your_password_here")
