# Typing Analyzer

A Flask-based web application that analyzes subconscious typing patterns to provide insights into user focus, confidence, and stress levels. The project is designed with heuristic rules instead of complex machine learning models.

## Features
- Capture typing metadata: speed, pauses, corrections, bursts, and slowdowns.
- Apply heuristic analysis:
  - Long pauses indicate thinking mode.
  - Many corrections suggest low focus.
  - Fast bursts suggest high confidence.
- Dashboard with interactive charts using Chart.js.
- Store session history in SQLite and allow CSV export.
- Suggest daily typing challenges for improvement.

## Tech Stack
- Backend: Flask (Python)
- Frontend: TailwindCSS, Chart.js, Vanilla JavaScript
- Database: SQLite
- Deployment: Heroku or Vercel

## Setup Instructions
1. Clone the repository:
git clone https://github.com/KishoreML-web/typing_analyzer.git
cd typing_analyzer

cpp
Copy code
2. Create a virtual environment:
python -m venv venv

markdown
Copy code
Activate it:
- On Linux/Mac: `source venv/bin/activate`
- On Windows: `venv\Scripts\activate`
3. Install dependencies:
pip install -r requirements.txt

markdown
Copy code
4. Run the Flask app:
python app.py

markdown
Copy code

## Demo Flow
1. User types in the provided editor.
2. The app records typing behavior.
3. Metrics and mood analysis are displayed on the dashboard.
4. Sessions are saved for history and export.

## License
This project is licensed under the MIT Licens
