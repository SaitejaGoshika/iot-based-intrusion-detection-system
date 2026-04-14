from flask import Flask, render_template, send_file
import joblib
import pandas as pd
import random
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Table
import threading
import time
import os

# keyboard trigger
import keyboard

app = Flask(__name__)

model = joblib.load("model.pkl")
columns = joblib.load("columns.pkl")
X_test = joblib.load("X_test.pkl")

history = []

# =============================
# STORE HISTORY
# =============================
def add_to_history(result, confidence):
    global history
    history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "result": result,
        "confidence": confidence
    })
    history = history[-10:]

# =============================
# KEYBOARD DETECTION (PRESS 'A')
# =============================
def keyboard_listener():
    while True:
        if keyboard.is_pressed('a'):
            add_to_history("attack", random.randint(85, 99))
            time.sleep(1)

# =============================
# DEVICE CHANGE SIMULATION (USB)
# =============================
initial_files = set(os.listdir("C:\\"))  # Windows root

def device_monitor():
    global initial_files
    while True:
        current_files = set(os.listdir("C:\\"))
        if current_files != initial_files:
            add_to_history("attack", random.randint(80, 95))
            initial_files = current_files
        time.sleep(5)

# Start background threads
threading.Thread(target=keyboard_listener, daemon=True).start()
threading.Thread(target=device_monitor, daemon=True).start()

# =============================
# MAIN ROUTE
# =============================
@app.route('/')
def home():
    global history

    sample = X_test.sample(1)

    prediction = model.predict(sample)[0]
    prob = model.predict_proba(sample)[0]

    confidence = round(max(prob) * 100, 2)
    result = "attack" if prediction == 1 else "normal"

    add_to_history(result, confidence)

    normal_count = sum(1 for h in history if h["result"] == "normal")
    attack_count = sum(1 for h in history if h["result"] == "attack")

    return render_template("index.html",
                           result=result,
                           confidence=confidence,
                           history=history,
                           normal_count=normal_count,
                           attack_count=attack_count)

# =============================
# BUTTON ATTACK
# =============================
@app.route('/attack')
def attack():
    add_to_history("attack", random.randint(90, 99))
    return home()

# =============================
# PDF DOWNLOAD
# =============================
@app.route('/download')
def download():
    file = "report.pdf"
    doc = SimpleDocTemplate(file)

    data = [["Time", "Status", "Confidence"]]
    for h in history:
        data.append([h["time"], h["result"], str(h["confidence"])])

    table = Table(data)
    doc.build([table])

    return send_file(file, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)