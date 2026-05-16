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

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{
        background: linear-gradient(to right,#141e30,#243b55);
        color:white;
        font-family:Arial;
    }

    .main-box{
        margin-top:80px;
    }

    .card{
        border-radius:20px;
        box-shadow:0px 8px 25px rgba(0,0,0,0.4);
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
    Advanced Cybersecurity Intelligence Platform
    </p>

    </div>

    <div class="card p-5 mt-4">

    <h3 class="text-dark">
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

    <h3 class="text-dark">
    📂 File Threat Analysis
    </h3>
c
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
    class="btn btn-dark">
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

    # ---------------- PHISHING DETECTION ----------------

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

    # ---------------- SCAM RESULT ----------------

    if result == 1:

        return f"""

        <body style="
        background:#121212;
        color:white;
        font-family:Arial;
        padding:40px;
        ">

        <div class="container">

        <div class="card bg-dark text-white p-5 shadow-lg">

        <h1 class="text-danger">
        ⚠ Threat Detected
        </h1>

        <hr>

        <h3>
        Scam Probability: {scam_percent}%
        </h3>

        <h4>
        Risk Level:
        <span class="text-warning">{level}</span>
        </h4>

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

        <div class="progress mt-4">

        <div class="progress-bar bg-danger"
        style="width:{scam_percent}%">
        {scam_percent}%
        </div>

        </div>

        <br>

        <a href="/"
        class="btn btn-danger">
        ⬅ Back
        </a>

        </div>

        </div>

        </body>

        """

    # ---------------- SAFE RESULT ----------------

    else:

        return f"""

        <body style="
        background:#e8fff0;
        font-family:Arial;
        padding:40px;
        ">

        <div class="container">

        <div class="card p-5 shadow-lg">

        <h1 class="text-success">
        ✅ Message Appears Safe
        </h1>

        <hr>

        <h3>
        Safe Probability: {safe_percent}%
        </h3>

        <h4>
        Risk Level: LOW
        </h4>

        <h4>
        🌐 Phishing Indicators:
        </h4>

        <p>
        {', '.join(phishing_found) if phishing_found else 'None'}
        </p>

        <div class="progress mt-4">

        <div class="progress-bar bg-success"
        style="width:{safe_percent}%">
        {safe_percent}%
        </div>

        </div>

        <br>

        <a href="/"
        class="btn btn-success">
        ⬅ Back
        </a>

        </div>

        </div>

        </body>

        """

# ------------------ FILE UPLOAD ANALYSIS ------------------

@app.route('/upload', methods=['POST'])
def upload():

    if 'file' not in request.files:
        return "<h2>No file selected</h2>"

    file = request.files['file']

    text = ""

    # TXT FILE

    if file.filename.endswith('.txt'):

        text = file.read().decode('utf-8')

    # PDF FILE

    elif file.filename.endswith('.pdf'):

        pdf_reader = PyPDF2.PdfReader(file)

        for page in pdf_reader.pages:

            extracted = page.extract_text()

            if extracted:
                text += extracted

    else:

        return """

        <body style="font-family:Arial;padding:40px;">

        <h2>
        ❌ Only TXT and PDF files supported
        </h2>

        <a href="/">
        Go Back
        </a>

        </body>

        """

    # ---------------- AI ANALYSIS ----------------

    data = vectorizer.transform([text])

    result = model_lr.predict(data)[0]

    prob = model_lr.predict_proba(data)[0][1]

    scam_percent = round(prob * 100, 2)

    safe_percent = round((1 - prob) * 100, 2)

    if prob > 0.8:
        level = "EXTREME"

    elif prob > 0.6:
        level = "HIGH"

    elif prob > 0.4:
        level = "MEDIUM"

    else:
        level = "LOW"

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
        "money"
    ]

    found = [w for w in danger_words if w in text.lower()]

    # ---------------- SCAM FILE ----------------
# ---------------- FILE TYPE ----------------

file_type = file.filename.split('.')[-1].upper()

# ---------------- SCAM FILE ----------------

if result == 1:

    return f"""

    <html>

    <head>

    <title>Threat Analysis Result</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{{
        background:linear-gradient(to right,#141e30,#243b55);
        color:white;
        font-family:Arial;
        padding:40px;
    }}

    .main-card{{
        background:#1c1c1c;
        border-radius:25px;
        padding:40px;
        box-shadow:0px 10px 30px rgba(0,0,0,0.5);
    }}

    .badge-box{{
        padding:15px;
        border-radius:15px;
        text-align:center;
        font-weight:bold;
        font-size:20px;
    }}

    </style>

    </head>

    <body>

    <div class="container">

    <div class="main-card">

    <h1 class="text-danger text-center">
    ⚠ HIGH RISK FILE DETECTED
    </h1>

    <hr>

    <div class="row text-center mt-4">

        <div class="col-md-4">

            <div class="badge-box bg-danger">

                Scam Probability

                <h2>{scam_percent}%</h2>

            </div>

        </div>

        <div class="col-md-4">

            <div class="badge-box bg-warning text-dark">

                Risk Level

                <h2>{level}</h2>

            </div>

        </div>

        <div class="col-md-4">

            <div class="badge-box bg-primary">

                File Type

                <h2>{file_type}</h2>

            </div>

        </div>

    </div>

    <div class="mt-5">

    <h3>
    🚨 Suspicious Keywords
    </h3>

    <div class="alert alert-danger mt-3">

    {', '.join(found) if found else 'No keywords detected'}

    </div>

    </div>

    <div class="mt-4">

    <h3>
    📊 Threat Meter
    </h3>

    <div class="progress" style="height:35px;">

    <div class="progress-bar progress-bar-striped progress-bar-animated bg-danger"
    style="width:{scam_percent}%">

    {scam_percent}%

    </div>

    </div>

    </div>

    <div class="mt-5">

    <h4>
    🛡 Security Recommendation
    </h4>

    <ul>

    <li>Do not click suspicious links</li>

    <li>Avoid sharing OTP or bank details</li>

    <li>Verify sender identity</li>

    <li>Scan attachments before opening</li>

    </ul>

    </div>

    <div class="text-center mt-5">

    <a href="/"
    class="btn btn-danger btn-lg">
    ⬅ Back to Home
    </a>

    <a href="/dashboard"
    class="btn btn-light btn-lg">
    📊 Dashboard
    </a>

    </div>

    </div>

    </div>

    </body>

    </html>

    """

# ---------------- SAFE FILE ----------------

else:

    return f"""

    <html>

    <head>

    <title>Threat Analysis Result</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{{
        background:linear-gradient(to right,#11998e,#38ef7d);
        color:white;
        font-family:Arial;
        padding:40px;
    }}

    .main-card{{
        background:white;
        color:black;
        border-radius:25px;
        padding:40px;
        box-shadow:0px 10px 30px rgba(0,0,0,0.4);
    }}

    .badge-box{{
        padding:15px;
        border-radius:15px;
        text-align:center;
        font-weight:bold;
        font-size:20px;
        color:white;
    }}

    </style>

    </head>

    <body>

    <div class="container">

    <div class="main-card">

    <h1 class="text-success text-center">
    ✅ FILE APPEARS SAFE
    </h1>

    <hr>

    <div class="row text-center mt-4">

        <div class="col-md-4">

            <div class="badge-box bg-success">

                Safe Probability

                <h2>{safe_percent}%</h2>

            </div>

        </div>

        <div class="col-md-4">

            <div class="badge-box bg-primary">

                Risk Level

                <h2>LOW</h2>

            </div>

        </div>

        <div class="col-md-4">

            <div class="badge-box bg-dark">

                File Type

                <h2>{file_type}</h2>

            </div>

        </div>

    </div>

    <div class="mt-5">

    <h3>
    📊 Safety Meter
    </h3>

    <div class="progress" style="height:35px;">

    <div class="progress-bar progress-bar-striped progress-bar-animated bg-success"
    style="width:{safe_percent}%">

    {safe_percent}%

    </div>

    </div>

    </div>

    <div class="mt-5">

    <h4>
    🛡 Security Status
    </h4>

    <ul>

    <li>No major phishing indicators found</li>

    <li>File content appears safe</li>

    <li>AI analysis completed successfully</li>

    <li>Threat level is minimal</li>

    </ul>

    </div>

    <div class="text-center mt-5">

    <a href="/"
    class="btn btn-success btn-lg">
    ⬅ Back to Home
    </a>

    <a href="/dashboard"
    class="btn btn-dark btn-lg">
    📊 Dashboard
    </a>

    </div>

    </div>

    </div>

    </body>

    </html>

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

    <title>Threat Intelligence Dashboard</title>

    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">

    <style>

    body{{
        background:linear-gradient(to right,#0f2027,#203a43,#2c5364);
        color:white;
        font-family:Arial;
        padding:40px;
    }}

    .card-box{{
        border-radius:20px;
        padding:30px;
        box-shadow:0px 8px 25px rgba(0,0,0,0.4);
    }}

    </style>

    </head>

    <body>

    <div class="container">

    <h1 class="text-center mb-5">
    📊 Threat Intelligence Dashboard
    </h1>

    <div class="row text-center">

        <div class="col-md-4">

            <div class="card-box bg-danger">

                <h1>{scam}</h1>

                <h4>Scam Messages</h4>

            </div>

        </div>

        <div class="col-md-4">

            <div class="card-box bg-success">

                <h1>{safe}</h1>

                <h4>Safe Messages</h4>

            </div>

        </div>

        <div class="col-md-4">

            <div class="card-box bg-primary">

                <h1>{total}</h1>

                <h4>Total Analysis</h4>

            </div>

        </div>

    </div>

    <div class="card mt-5 p-4">

        <h2 class="text-dark text-center">
        Scam Detection Analytics
        </h2>

        <h4 class="text-center text-danger">
        Scam Percentage: {percent:.2f}%
        </h4>

        <canvas id="chart"></canvas>

    </div>

    <div class="card mt-4 p-4 bg-dark text-white">

        <h3>
        🛡 System Status: ACTIVE
        </h3>

        <p>
        AI Threat Analysis Engine is running successfully.
        </p>

        <ul>

        <li>✔ Scam Message Detection</li>

        <li>✔ PDF Threat Analysis</li>

        <li>✔ TXT File Analysis</li>

        <li>✔ Phishing Detection</li>

        <li>✔ Risk Level Analytics</li>

        </ul>

    </div>

    <div class="text-center mt-4">

    <a href="/"
    class="btn btn-light btn-lg">
    ⬅ Back
    </a>

    </div>

    </div>

    <script>

    const ctx = document.getElementById('chart');

    new Chart(ctx, {{

        type: 'doughnut',

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
