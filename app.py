from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import pandas as pd
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
DATABASE = 'typing_analyzer.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize DB on app start
with app.app_context():
    from database import init_db
    init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_typing():
    data = request.json
    raw_text = data.get('text', '')
    keydown_events = data.get('keydownEvents', [])
    keyup_events = data.get('keyupEvents', [])

    total_chars = len(raw_text)
    total_words = len(raw_text.split()) if raw_text.strip() else 0

    start_time = keydown_events[0]['timestamp'] if keydown_events else datetime.now().timestamp() * 1000
    end_time = keyup_events[-1]['timestamp'] if keyup_events else datetime.now().timestamp() * 1000
    duration_ms = end_time - start_time
    duration_seconds = duration_ms / 1000.0

    if duration_seconds <= 0:
        duration_seconds = 1

    avg_speed_wpm = (total_words / (duration_seconds / 60)) if total_words > 0 else 0

    total_pauses = 0
    if len(keyup_events) > 1:
        for i in range(1, len(keyup_events)):
            delay = keyup_events[i]['timestamp'] - keyup_events[i-1]['timestamp']
            if delay > 500:
                total_pauses += 1

    total_backspaces = sum(1 for event in keydown_events if event.get('key') == 'Backspace')

    burst_count = 0
    if len(keydown_events) > 2:
        for i in range(2, len(keydown_events)):
            delay1 = keydown_events[i]['timestamp'] - keydown_events[i-1]['timestamp']
            delay2 = keydown_events[i-1]['timestamp'] - keydown_events[i-2]['timestamp']
            if delay1 < 150 and delay2 < 150:
                burst_count += 1

    burst_percentage = (burst_count / len(keydown_events) * 100) if keydown_events else 0

    mood_report = "Your typing patterns reveal: "
    mood = "Neutral"

    if total_backspaces > len(raw_text) / 5 and total_words > 10:
        mood_report += "You seem to be correcting yourself quite often, indicating a potential **low focus** or **uncertainty**."
        mood = "Uncertain"
    elif total_pauses > total_words / 3 and total_words > 10:
        mood_report += "Frequent pauses suggest you're in **thinking mode**, carefully considering your words."
        mood = "Thoughtful"
    elif avg_speed_wpm > 60 and burst_percentage > 30:
        mood_report += "Your fast bursts and high speed show **high confidence** and fluency!"
        mood = "Confident"
    elif avg_speed_wpm < 20 and total_words > 5:
        mood_report += "Your typing speed is quite slow, perhaps you're feeling a bit **stressed** or unmotivated."
        mood = "Stressed"
    else:
        mood_report += "Your typing pattern is fairly balanced, indicating a **steady and focused** approach."
        mood = "Steady"

    if avg_speed_wpm < 40:
        challenge = "Try a 5-minute speed drill to boost your WPM!"
    elif total_backspaces > len(raw_text) / 10:
        challenge = "Focus on accuracy today. Type carefully to minimize backspaces."
    elif total_pauses > total_words / 5:
        challenge = "Practice free-writing for 10 minutes to improve your flow and reduce pauses."
    else:
        challenge = "Keep up the great work! Try writing a short story to maintain your rhythm."

    # Save to DB
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (raw_text, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words, duration_seconds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (raw_text, mood_report, avg_speed_wpm, total_pauses, total_backspaces, burst_percentage, total_words, duration_seconds)
        )
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()

    # The frontend expects simple chartData keys (avgSpeed, totalPauses, ...)
    return jsonify({
        'moodReport': mood_report,
        'mood': mood,
        'avgSpeed': round(avg_speed_wpm, 2),
        'totalPauses': total_pauses,
        'totalBackspaces': total_backspaces,
        'burstPercentage': round(burst_percentage, 2),
        'totalWords': total_words,
        'challenge': challenge,
        'chartData': {
            'avgSpeed': round(avg_speed_wpm, 2),
            'totalPauses': total_pauses,
            'totalBackspaces': total_backspaces,
            'burstPercentage': round(burst_percentage, 2)
        }
    })

@app.route('/history')
def get_history():
    conn = get_db_connection()
    sessions = conn.execute('SELECT * FROM sessions ORDER BY timestamp DESC').fetchall()
    conn.close()

    history_data = []
    for session in sessions:
        # session['timestamp'] is stored as text DATETIME in DB default CURRENT_TIMESTAMP
        # convert to display format
        ts = session['timestamp']
        try:
            timestamp_obj = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            formatted_date = timestamp_obj.strftime('%Y-%m-%d %H:%M')
        except Exception:
            formatted_date = ts

        history_data.append({
            'id': session['id'],
            'date': formatted_date,
            'mood': session['mood'],
            'avg_speed': round(session['avg_speed'], 2) if session['avg_speed'] is not None else 0,
            'total_pauses': session['total_pauses'],
            'total_backspaces': session['total_backspaces'],
            'burst_percentage': round(session['burst_percentage'], 2) if session['burst_percentage'] is not None else 0,
            'total_words': session['total_words']
        })
    return jsonify(history_data)

@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT timestamp, mood, avg_speed, total_pauses, total_backspaces, burst_percentage, total_words, raw_text FROM sessions ORDER BY timestamp DESC", conn)
    conn.close()

    output = BytesIO()
    df.to_csv(output, index=False, encoding='utf-8')
    output.seek(0)

    return send_file(output,
                     mimetype='text/csv',
                     download_name='typing_history.csv',
                     as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
