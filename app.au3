from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Welcome to EduSupport</h1>
    <p>Connecting students with educational supporters.</p>
    """

if __name__ == "__main__":
    app.run(debug=True)