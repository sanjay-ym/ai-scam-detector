from flask import Flask, request, jsonify
import pickle
from collections import Counter
import os
import re

app = Flask(__name__)

# ------------------ LOAD MODEL ------------------

model_lr = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ------------------ STATS FUNCTION ------------------

def update_stats(is_scam, words_list):

    try:
        with open("stats.txt", "r") as f:
            scam, safe = map(int, f.read().split(","))
    except:
        scam, safe = 0, 0

    if is_scam:
        scam += 1
    else:
        safe += 1

    with open("stats.txt", "w") as f:
        f.write(f"{scam},{safe}")

    # Save analytics words
    try:
        with open("words.txt", "r") as f:
            data = f.read().split(",")
    except:
        data = []

    data.extend(words_list)

    with open("words.txt", "w") as f:
        f.write(",".join(data))


# ------------------ HOME ------------------

@app.route('/')

def home():

    return '''
    <html>

    <head>

    <title>AI Scam Detector</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{
        background: linear-gradient(135deg,#141e30,#243b55);
        color:white;
        height:100vh;
    }

    .card{
        border-radius:25px;
        box-shadow:0px 10px 40px rgba(0,0,0,0.5);
        background:#ffffff;
        color:black;
    }

    textarea{
        height:120px;
    }

    </style>

    </head>

    <body class="d-flex justify-content-center align-items-center">

    <div class="card p-4" style="width:500px;">

        <h2 class="text-center mb-3">🛡 AI Scam Detection System</h2>

        <form method="POST" action="/predict">

            <textarea class="form-control"
            name="msg"
            placeholder="Enter suspicious message"></textarea>

            <button class="btn btn-danger mt-3 w-100">
            Detect Scam
            </button>

        </form>

        <form method="POST"
        action="/upload"
        enctype="multipart/form-data"
        class="mt-3">

            <input class="form-control"
            type="file"
            name="file">

            <button class="btn btn-secondary mt-2 w-100">
            Upload File
            </button>

        </form>

        <a href="/dashboard"
        class="btn btn-dark mt-3">
        📊 Open Dashboard
        </a>

        <a href="/reset"
        class="btn btn-warning mt-2">
        Reset Analytics
        </a>

    </div>

    </body>
    </html>
    '''


# ------------------ PREDICT ------------------

@app.route('/predict', methods=['POST'])

def predict():

    msg = request.form['msg']

    data = vectorizer.transform([msg])

    result = model_lr.predict(data)[0]

    prob = model_lr.predict_proba(data)[0][1]

    scam_percent = round(prob * 100, 2)

    safe_percent = round((1 - prob) * 100, 2)

    # ------------------ RISK LEVEL ------------------

    if prob > 0.8:
        level = "EXTREME"
        color = "darkred"

    elif prob > 0.6:
        level = "HIGH"
        color = "red"

    elif prob > 0.4:
        level = "MEDIUM"
        color = "orange"

    else:
        level = "LOW"
        color = "green"

    # ------------------ DANGER WORDS ------------------

    danger_words = [
        "win",
        "free",
        "otp",
        "bank",
        "offer",
        "urgent",
        "click",
        "verify",
        "account",
        "gift",
        "prize",
        "money"
    ]

    found = [w for w in danger_words if w in msg.lower()]

    # ------------------ PHISHING DETECTION ------------------

    phishing_words = [
        "http",
        "https",
        ".xyz",
        ".ru",
        ".tk",
        "login",
        "verify",
        "account"
    ]

    phishing_found = [
        w for w in phishing_words if w in msg.lower()
    ]

    # ------------------ LINK DETECTION ------------------

    urls = re.findall(r'(https?://\\S+)', msg)

    # ------------------ EXPLAINABLE AI ------------------

    highlighted = msg

    for w in danger_words:

        highlighted = highlighted.replace(
            w,
            f"<span style='color:red;font-weight:bold'>{w}</span>"
        )

    update_stats(result == 1, found)

    # ------------------ RESULT PAGE ------------------

    if result == 1:

        return f"""

        <body style="
        background:#1b1b1b;
        color:white;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        ">

        <div style="
        background:white;
        color:black;
        width:650px;
        padding:35px;
        border-radius:25px;
        box-shadow:0px 10px 40px rgba(0,0,0,0.6);
        ">

        <h1 style="color:red;">
        ⚠ SCAM DETECTED
        </h1>

        <hr>

        <h3>
        Scam Probability:
        <span style="color:red;">
        {scam_percent}%
        </span>
        </h3>

        <h4>
        Safe Probability:
        <span style="color:green;">
        {safe_percent}%
        </span>
        </h4>

        <h4>
        Threat Level:
        <span style="color:{color};">
        {level}
        </span>
        </h4>

        <hr>

        <h5>🧠 Explainable AI Analysis</h5>

        <p>
        <b>Detected Scam Keywords:</b>
        {', '.join(found) if found else 'None'}
        </p>

        <p>
        <b>Phishing Indicators:</b>
        {', '.join(phishing_found) if phishing_found else 'None'}
        </p>

        <p>
        <b>URLs Found:</b>
        {', '.join(urls) if urls else 'No Links'}
        </p>

        <p>
        <b>Highlighted Message:</b>
        <br><br>
        {highlighted}
        </p>

        <hr>

        <a href="/"
        style="
        padding:12px 20px;
        background:black;
        color:white;
        border-radius:10px;
        text-decoration:none;
        ">
        ⬅ Back
        </a>

        </div>

        </body>
        """

    else:

        return f"""

        <body style="
        background:#e8fff0;
        display:flex;
        justify-content:center;
        align-items:center;
        height:100vh;
        ">

        <div style="
        background:white;
        width:600px;
        padding:35px;
        border-radius:25px;
        text-align:center;
        ">

        <h1 style="color:green;">
        ✅ SAFE MESSAGE
        </h1>

        <hr>

        <h3>
        Safe Probability:
        {safe_percent}%
        </h3>

        <p>{highlighted}</p>

        <a href="/">⬅ Back</a>

        </div>

        </body>
        """


# ------------------ FILE UPLOAD ------------------

@app.route('/upload', methods=['POST'])

def upload():

    file = request.files['file']

    lines = file.read().decode('utf-8').splitlines()

    output = ""

    for msg in lines:

        data = vectorizer.transform([msg])

        result = model_lr.predict(data)[0]

        words = ["win","free","otp","bank","click"]

        found = [w for w in words if w in msg.lower()]

        update_stats(result == 1, found)

        if result == 1:

            output += f"""
            <p style='color:red;'>
            ⚠ Scam → {msg}
            </p>
            """

        else:

            output += f"""
            <p style='color:green;'>
            ✅ Safe → {msg}
            </p>
            """

    return f"""

    <body style='padding:40px;font-family:Arial;'>

    <h1>📁 File Scan Results</h1>

    <hr>

    {output}

    <br>

    <a href='/'>⬅ Back</a>

    </body>
    """


# ------------------ DASHBOARD ------------------

@app.route('/dashboard')

def dashboard():

    try:

        with open("stats.txt", "r") as f:
            scam, safe = map(int, f.read().split(","))

    except:

        scam, safe = 0, 0

    total = scam + safe

    percent = (scam / total * 100) if total else 0

    return f"""

    <html>

    <head>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="
    background:#0f2027;
    color:white;
    padding:40px;
    ">

    <h1 class="text-center">
    📊 Threat Intelligence Dashboard
    </h1>

    <div class="row mt-5 text-center">

        <div class="col-md-4">

            <div class="card bg-danger text-white p-4">

                <h2>{scam}</h2>

                <h4>Scam Messages</h4>

            </div>

        </div>

        <div class="col-md-4">

            <div class="card bg-success text-white p-4">

                <h2>{safe}</h2>

                <h4>Safe Messages</h4>

            </div>

        </div>

        <div class="col-md-4">

            <div class="card bg-primary text-white p-4">

                <h2>{total}</h2>

                <h4>Total Analysis</h4>

            </div>

        </div>

    </div>

    <div class="card mt-5 p-4">

        <h3 class="text-center text-dark">
        Scam Percentage: {percent:.2f}%
        </h3>

        <canvas id="chart"></canvas>

    </div>

    <script>

    const ctx = document.getElementById('chart');

    new Chart(ctx, {

        type: 'doughnut',

        data: {

            labels: ['Scam', 'Safe'],

            datasets: [{
    data: [scam, safe],
    backgroundColor: ['red', 'green']
            }]

        }

    });

    </script>

    <div class="text-center mt-4">

    <a href="/"
    class="btn btn-light">
    ⬅ Back
    </a>

    </div>

    </body>
    </html>
    """


# ------------------ RESET ------------------

@app.route('/reset')

def reset():

    open("stats.txt", "w").write("0,0")

    open("words.txt", "w").write("")

    return """
    <h2>Analytics Reset Done</h2>
    <a href="/">Back</a>
    """


# ------------------ API ------------------

@app.route('/api', methods=['POST'])

def api():

    msg = request.form['msg']

    data = vectorizer.transform([msg])

    result = model_lr.predict(data)[0]

    prob = model_lr.predict_proba(data)[0][1]

    scam_percent = round(prob * 100, 2)

    safe_percent = round((1 - prob) * 100, 2)

    # Risk level
    if prob > 0.8:
        level = "EXTREME"

    elif prob > 0.6:
        level = "HIGH"

    elif prob > 0.4:
        level = "MEDIUM"

    else:
        level = "LOW"

    # Danger words
    danger_words = [
        "win",
        "free",
        "otp",
        "bank",
        "offer",
        "urgent",
        "click",
        "verify",
        "account",
        "gift",
        "prize",
        "money"
    ]

    found = [w for w in danger_words if w in msg.lower()]

    # Phishing detection
    phishing_words = [
        "http",
        "https",
        ".xyz",
        ".ru",
        ".tk",
        "login",
        "verify",
        "account"
    ]

    phishing_found = [
        w for w in phishing_words if w in msg.lower()
    ]

    # Scam response
    if result == 1:

        return jsonify({

            "prediction": "Scam",

            "probability": scam_percent,

            "safe_probability": safe_percent,

            "risk_level": level,

            "danger_words": found,

            "phishing_indicators": phishing_found,

            "status": "danger"

        })

    # Safe response
    else:

        return jsonify({

            "prediction": "Safe",

            "probability": safe_percent,

            "risk_level": "LOW",

            "danger_words": found,

            "phishing_indicators": phishing_found,

            "status": "safe"

        })


# ------------------ RUN ------------------

port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port)
