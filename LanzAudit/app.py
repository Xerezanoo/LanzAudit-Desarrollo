from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/password-recovery')
def passwordRecovery():
    return render_template("password-recovery.html")

@app.route('/dashboard')
def home():
    return render_template("index.html")

@app.route('/faq')
def faq():
    return render_template("faq.html")

@app.route('/license')
def license():
    return render_template("license.html")

if __name__ == "__main__":
    app.run(debug=True)