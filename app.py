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

    if result == 1:

        return f"""

        <body style="
        background:black;
        color:white;
        font-family:Arial;
        padding:40px;
        ">

        <h1 style="color:red;">
        ⚠ Scam File Detected
        </h1>

        <h2>
        Scam Probability: {scam_percent}%
        </h2>

        <h3>
        Risk Level: {level}
        </h3>

        <h3>
        Danger Words:
        {', '.join(found)}
        </h3>

        <div style="
        background:#333;
        width:100%;
        height:30px;
        border-radius:10px;
        overflow:hidden;
        ">

        <div style="
        background:red;
        width:{scam_percent}%;
        height:30px;
        text-align:center;
        ">
        {scam_percent}%
        </div>

        </div>

        <br>

        <a href="/"
        style="
        background:red;
        color:white;
        padding:10px 20px;
        text-decoration:none;
        border-radius:10px;
        ">
        ⬅ Back
        </a>

        </body>

        """

    # ---------------- SAFE FILE ----------------

    else:

        return f"""

        <body style="
        background:#e8fff0;
        font-family:Arial;
        padding:40px;
        ">

        <h1 style="color:green;">
        ✅ File Appears Safe
        </h1>

        <h2>
        Safe Probability: {safe_percent}%
        </h2>

        <h3>
        Risk Level: LOW
        </h3>

        <div style="
        background:#ccc;
        width:100%;
        height:30px;
        border-radius:10px;
        overflow:hidden;
        ">

        <div style="
        background:green;
        width:{safe_percent}%;
        height:30px;
        text-align:center;
        color:white;
        ">
        {safe_percent}%
        </div>

        </div>

        <br>

        <a href="/"
        style="
        background:green;
        color:white;
        padding:10px 20px;
        text-decoration:none;
        border-radius:10px;
        ">
        ⬅ Back
        </a>

        </body>

        """

# ------------------ DASHBOARD ------------------

@app.route('/dashboard')
def dashboard():

    return """

    <body style="
    background:#0f2027;
    color:white;
    font-family:Arial;
    padding:40px;
    ">

    <h1>
    📊 Threat Intelligence Dashboard
    </h1>

    <div style="
    background:#1c1c1c;
    padding:30px;
    border-radius:20px;
    margin-top:30px;
    ">

    <h3>
    🛡 System Status: ACTIVE
    </h3>

    <p>
    AI Threat Analysis Engine is running successfully.
    </p>

    <p>
    Features Enabled:
    </p>

    <ul>
    <li>✔ Scam Message Detection</li>
    <li>✔ PDF Threat Analysis</li>
    <li>✔ TXT File Analysis</li>
    <li>✔ Phishing Detection</li>
    <li>✔ Risk Level Analytics</li>
    </ul>

    <a href="/"
    style="
    background:white;
    color:black;
    padding:10px 20px;
    text-decoration:none;
    border-radius:10px;
    ">
    ⬅ Back
    </a>

    </div>

    </body>

    """

# ------------------ RUN ------------------

port = int(os.environ.get("PORT", 5000))

app.run(host="0.0.0.0", port=port)
