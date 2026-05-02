from flask import Flask, request
import pickle
from collections import Counter

app = Flask(__name__)

# Load models
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

    # Save word analytics
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
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
    body { background: linear-gradient(to right,#4facfe,#00f2fe); }
    .card { border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,0.2); }
    </style>
    </head>

    <body class="d-flex justify-content-center align-items-center" style="height:100vh;">
    <div class="card p-4 text-center" style="width:420px;">

    <h3>🔐 AI Scam Detection</h3>

    <form method="POST" action="/predict">
        <input class="form-control mt-3" name="msg" placeholder="Enter message">
        <button class="btn btn-success mt-3 w-100">Check</button>
    </form>

    <form method="POST" action="/upload" enctype="multipart/form-data" class="mt-3">
        <input class="form-control" type="file" name="file">
        <button class="btn btn-secondary mt-2 w-100">Upload File</button>
    </form>

    <a href="/dashboard" class="btn btn-dark mt-3">📊 Dashboard</a>
    <a href="/reset" class="btn btn-danger mt-2">Reset</a>

    </div>
    </body>
    </html>
    '''


# ------------------ PREDICT ------------------
@app.route('/predict', methods=['POST'])
def predict():
    msg = request.form['msg']
    data = vectorizer.transform([msg])

    # ML prediction
    result = model_lr.predict(data)[0]
    prob = model_lr.predict_proba(data)[0][1]

    # Risk level
    if prob > 0.7:
        level = "HIGH"
    elif prob > 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"

    # Danger words
    words = ["win", "free", "otp", "bank", "click", "offer", "urgent"]
    found = [w for w in words if w in msg.lower()]

    # Highlight words (Explainable AI)
    highlighted = msg
    for w in words:
        highlighted = highlighted.replace(w, f"<span style='color:red;font-weight:bold'>{w}</span>")

    update_stats(result == 1, found)

    if result == 1:
        return f"""
        <body style="background:#ffe6e6; display:flex; justify-content:center; align-items:center; height:100vh;">
        <div style="background:white;padding:30px;border-radius:15px;text-align:center;">

        <h2 style="color:red;">⚠️ Scam ({prob*100:.2f}%)</h2>
        <p><b>Risk:</b> {level}</p>

        <p><b>Highlighted Message:</b><br>{highlighted}</p>

        <p><b>Detected Words:</b> {', '.join(found) if found else 'None'}</p>

        <a href="/">⬅ Back</a>
        </div>
        </body>
        """
    else:
        return f"""
        <body style="background:#e6ffe6; display:flex; justify-content:center; align-items:center; height:100vh;">
        <div style="background:white;padding:30px;border-radius:15px;text-align:center;">

        <h2 style="color:green;">✅ Safe</h2>

        <p><b>Message:</b><br>{highlighted}</p>

        <a href="/">⬅ Back</a>
        </div>
        </body>
        """


# ------------------ FILE ------------------
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
            output += f"{msg} → ⚠️ Scam<br>"
        else:
            output += f"{msg} → ✅ Safe<br>"

    return f"<h2>Results</h2>{output}<br><a href='/'>Back</a>"


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
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

    <style>
    body {{
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
    }}

    .card {{
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        animation: fadeIn 1s;
    }}

    @keyframes fadeIn {{
        from {{opacity:0; transform:translateY(30px);}}
        to {{opacity:1; transform:translateY(0);}}
    }}

    .stat-box {{
        border-radius: 15px;
        padding: 15px;
        color: white;
    }}

    .scam-box {{
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
    }}

    .safe-box {{
        background: linear-gradient(45deg, #11998e, #38ef7d);
    }}

    .total-box {{
        background: linear-gradient(45deg, #396afc, #2948ff);
    }}
    </style>
    </head>

    <body class="container py-5">

    <h1 class="text-center mb-4">📊 Analytics Dashboard</h1>

    <div class="row text-center mb-4">
        <div class="col-md-4">
            <div class="stat-box total-box">
                <h4>Total</h4>
                <h2>{total}</h2>
            </div>
        </div>

        <div class="col-md-4">
            <div class="stat-box scam-box">
                <h4>⚠️ Scam</h4>
                <h2>{scam}</h2>
            </div>
        </div>

        <div class="col-md-4">
            <div class="stat-box safe-box">
                <h4>✅ Safe</h4>
                <h2>{safe}</h2>
            </div>
        </div>
    </div>

    <div class="card p-4 text-center">
        <h4>Scam Percentage: {percent:.1f}%</h4>

        <canvas id="chart" style="max-width:300px; margin:auto;"></canvas>
    </div>

    <div class="text-center mt-4">
        <a href="/" class="btn btn-light">⬅ Back</a>
    </div>

    <script>
    const ctx = document.getElementById('chart');

    new Chart(ctx, {{
        type: 'doughnut',
        data: {{
            labels: ['Scam', 'Safe'],
            datasets: [{{
                data: [{scam}, {safe}],
                backgroundColor: ['#ff4b2b', '#38ef7d'],
                borderWidth: 0
            }}]
        }},
        options: {{
            plugins: {{
                legend: {{
                    labels: {{
                        color: 'white'
                    }}
                }}
            }}
        }}
    }});
    </script>

    </body>
    </html>
    """

# ------------------ RESET ------------------
@app.route('/reset')
def reset():
    open("stats.txt","w").write("0,0")
    open("words.txt","w").write("")
    return "<h2>Reset Done</h2><a href='/'>Back</a>"


# ------------------ RUN ------------------
import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
