# NBA Head-to-Head Matchup Analyzer
Who's really better?

How does SGA perform when matched up against a defensive-minded ball hawk like Dyson Daniels? How does Jokic play when you put him against a powerhouse like Wemby? The Head-to-Head Matchup Analyzer was built to answer these questions.

This app goes beyond standard box score statistics. Pit any two active players against each other and see a detailed, aggregated statistical breakdown of only the games where they have played head-to-head. 

## Installation
This project is divided into two parts: A Django backend and a React frontend.
### Prereqs:
- Python 3.10+
- Node.js
- Git
### 1. Django Setup
```
# 1. Clone the repository
git clone https://github.com/mrayl/H2H-Analysis
cd H2H-Analysis/backend

# 2. Create + Activate a Python Virtual Environment
python -m venv
venv\Scripts\activate

# 3. Install required Python Packages
pip install django djangorestframework django-cors-headers nba_api pandas

# 4. Run migrations
python manage.py migrate

# 5. Populate NBA player database
python manage.py populate_players
```
### 2. React Setup
Set up the user interface in a seperate terminal:
```
# 1. Navigate to frontend directory
cd ../frontend

# 2. Install node modules
npm install
```

## 2. Getting Started
Both servers must be running simultaneously to run the application.
### Terminal 1:
```
# In the /backend directory
python manage.py runserver
# API will be live at http://localhost:8000
```
### Terminal 2:
```
# In the /frontend directory
npm run dev
# The app will be live at http://localhost:5173
```

Open ```http://localhost:5173``` to see and use the application.

## License
The MIT License (MIT)

Copyright (C) 2025 Matthew R. Rayl

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
