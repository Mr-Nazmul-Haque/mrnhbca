from flask import Flask, render_template
import subprocess
import pandas as pd

app = Flask(__name__)

@app.route("/")
def dashboard():
    # Run original uad.py (logic untouched)
    subprocess.Popen(["python", "uad.py"])

    # Read CSV for graph / activity display
    try:
        df = pd.read_csv("activity_log.csv")
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        activities = df.tail(50).to_dict(orient="records")
        usage = df['AppName'].value_counts().to_dict()
    except:
        activities = []
        usage = {}

    return render_template("index.html", activities=activities, usage=usage)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
