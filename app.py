from flask import Flask, request
import pickle
import os
import PyPDF2

app = Flask(__name__)

# ------------------ LOAD MODEL ------------------

model_lr = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))

# ------------------ HOME PAGE ------------------

@app.route('/')
def home():

    return """

    <html>

    <head>

    <title>AI Scam Detection System</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{
        background: linear-gradient(to right,#141e30,#243b55);
        color:white;
        font-family:Arial;
    }

    .main-box{
        margin-top:50px;
    }

    .card{
        border-radius:20px;
        box-shadow:0px 8px 25px rgba(0,0,0,0.5);
        border:none;
    }

    textarea{
        border-radius:15px !important;
    }

    .btn{
        border-radius:12px;
    }

    </style>

    </head>

    <body>

    <div class="container main-box">

    <div class="text-center">

    <h1>
    🛡 AI Scam Detection & Threat Analysis System
    </h1>

    <p>
    Advanced AI Based Cybersecurity Intelligence Platform
    </p>

    </div>

    <div class="card bg-dark text-white p-5 mt-4">

    <h3>
    📩 Message Analysis
    </h3>

    <form action="/predict" method="POST">

    <textarea
    name="msg"
    class="form-control"
    rows="5"
    placeholder="Enter suspicious message..."
    required></textarea>

    <br>

    <button class="btn btn-danger">
    Analyze Message
    </button>

    </form>

    <hr>

    <h3>
    📂 File Threat Analysis
    </h3>

    <form action="/upload"
    method="POST"
    enctype="multipart/form-data">

    <input
    type="file"
    name="file"
    class="form-control"
    required>

    <br>

    <button class="btn btn-primary">
    Upload & Analyze File
    </button>

    </form>

    <br>

    <a href="/dashboard"
    class="btn btn-success">
    📊 Open Analytics Dashboard
    </a>

    </div>

    </div>

    </body>

    </html>

    """

# ------------------ PREDICT MESSAGE ------------------

@app.route('/predict', methods=['POST'])
def predict():

    msg = request.form['msg']

    data = vectorizer.transform([msg])

    result = model_lr.predict(data)[0]

    prob = model_lr.predict_proba(data)[0][1]

    scam_percent = round(prob * 100, 2)

    safe_percent = round((1 - prob) * 100, 2)

    # ---------------- SAVE STATS ----------------

    try:

        with open("stats.txt", "r") as f:
            scam, safe = map(int, f.read().split(","))

    except:
        scam, safe = 0, 0

    if result == 1:
        scam += 1
    else:
        safe += 1

    with open("stats.txt", "w") as f:
        f.write(f"{scam},{safe}")

    # ---------------- RISK LEVEL ----------------

    if prob > 0.8:
        level = "EXTREME"

    elif prob > 0.6:
        level = "HIGH"

    elif prob > 0.4:
        level = "MEDIUM"

    else:
        level = "LOW"

    # ---------------- DANGER WORDS ----------------

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

    # ---------------- RESULT PAGE ----------------

    if result == 1:

        color = "danger"
        title = "⚠ Scam Message Detected"

    else:

        color = "success"
        title = "✅ Message Appears Safe"

    return f"""

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="
    background:#101820;
    color:white;
    font-family:Arial;
    padding:40px;
    ">

    <div class="container">

    <div class="card bg-dark text-white p-5">

    <h1 class="text-{color}">
    {title}
    </h1>

    <hr>

    <h3>
    Scam Probability: {scam_percent}%
    </h3>

    <h3>
    Safe Probability: {safe_percent}%
    </h3>

    <h3>
    Risk Level: {level}
    </h3>

    <h4>
    🚨 Danger Words:
    </h4>

    <p>
    {', '.join(found) if found else 'None'}
    </p>

    <h4>
    🌐 Phishing Indicators:
    </h4>

    <p>
    {', '.join(phishing_found) if phishing_found else 'None'}
    </p>

    <div class="progress mt-4" style="height:35px;">

    <div class="progress-bar bg-{color}"
    style="width:{scam_percent}%">
    {scam_percent}%
    </div>

    </div>

    <br>

    <a href="/"
    class="btn btn-{color}">
    ⬅ Back
    </a>

    </div>

    </div>

    </body>

    </html>

    """

# ------------------ FILE ANALYSIS ------------------

@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return "<h2>No file selected</h2>"

    file = request.files['file']

    text = ""

    if file.filename.endswith('.txt'):

        text = file.read().decode('utf-8')

    elif file.filename.endswith('.pdf'):

        pdf_reader = PyPDF2.PdfReader(file)

        for page in pdf_reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

    else:

        return """

        <h2 style="font-family:Arial;padding:40px;">
        ❌ Only TXT and PDF supported
        </h2>

        """

    data = vectorizer.transform([text])

    result = model_lr.predict(data)[0]

    prob = model_lr.predict_proba(data)[0][1]

    scam_percent = round(prob * 100, 2)

    safe_percent = round((1 - prob) * 100, 2)

    # ---------------- SAVE STATS ----------------

    try:

        with open("stats.txt", "r") as f:
            scam, safe = map(int, f.read().split(","))

    except:
        scam, safe = 0, 0

    if result == 1:
        scam += 1
    else:
        safe += 1

    with open("stats.txt", "w") as f:
        f.write(f"{scam},{safe}")

    # ---------------- RESULT STYLE ----------------

    if result == 1:

        title = "⚠ Scam File Detected"
        color = "danger"

    else:

        title = "✅ File Appears Safe"
        color = "success"

    return f"""

    <html>

    <head>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    </head>

    <body style="
    background:linear-gradient(to right,#141e30,#243b55);
    color:white;
    font-family:Arial;
    padding:40px;
    ">

    <div class="container">

    <div class="card bg-dark text-white p-5">

    <h1 class="text-{color}">
    {title}
    </h1>

    <hr>

    <h3>
    📄 File Name:
    {file.filename}
    </h3>

    <h3>
    ⚠ Scam Probability:
    {scam_percent}%
    </h3>

    <h3>
    🛡 Safe Probability:
    {safe_percent}%
    </h3>

    <div class="progress mt-4" style="height:35px;">

    <div class="progress-bar bg-{color}"
    style="width:{scam_percent}%">

    {scam_percent}%

    </div>

    </div>

    <br>

    <a href="/"
    class="btn btn-{color}">
    ⬅ Back
    </a>

    </div>

    </div>

    </body>

    </html>

    """

# ------------------ RESET DASHBOARD ------------------

@app.route('/reset')
def reset():

    with open("stats.txt", "w") as f:
        f.write("0,0")

    return """

    <body style="
    background:black;
    color:white;
    font-family:Arial;
    padding:50px;
    text-align:center;
    ">

    <h1>
    ✅ Dashboard Reset Successful
    </h1>

    <br>

    <a href="/dashboard"
    style="
    background:green;
    color:white;
    padding:12px 25px;
    text-decoration:none;
    border-radius:10px;
    ">
    Go To Dashboard
    </a>

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
    background:linear-gradient(to right,#141e30,#243b55);
    color:white;
    font-family:Arial;
    padding:40px;
    ">

    <div class="container">

    <h1 class="text-center mb-5">
    📊 Threat Intelligence Dashboard
    </h1>

    <div class="row text-center">

    <div class="col-md-4">

    <div class="card bg-danger text-white p-4">

    <h1>{scam}</h1>

    <h3>Scam Messages</h3>

    </div>

    </div>

    <div class="col-md-4">

    <div class="card bg-success text-white p-4">

    <h1>{safe}</h1>

    <h3>Safe Messages</h3>

    </div>

    </div>

    <div class="col-md-4">

    <div class="card bg-primary text-white p-4">

    <h1>{total}</h1>

    <h3>Total Analysis</h3>

    </div>

    </div>

    </div>

    <div class="card mt-5 p-4">

    <h2 class="text-center text-dark">
    Scam Detection Analytics
    </h2>

    <h3 class="text-center text-danger">
    Scam Percentage: {percent:.2f}%
    </h3>

    <canvas id="chart"></canvas>

    </div>

    <br>

    <div class="text-center">

    <a href="/reset"
    class="btn btn-danger btn-lg">
    🔄 Reset Dashboard
    </a>

    <br><br>

    <a href="/"
    class="btn btn-light btn-lg">
    ⬅ Back Home
    </a>

    </div>

    </div>

    <script>

    const ctx = document.getElementById('chart');

    new Chart(ctx, {{

        type: 'pie',

        data: {{

            labels: ['Scam', 'Safe'],

            datasets: [{{
                data: [{scam}, {safe}],
                backgroundColor: ['red', 'green']
            }}]

        }}

    }});

    </script>

    </body>

    </html>

    """

# ------------------ RUN ------------------

port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port)
