import os

from flask import Flask, redirect, url_for
from dotenv import load_dotenv

from routes.auth import auth


load_dotenv()


app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise ValueError("FLASK_SECRET_KEY is not set")


app.register_blueprint(auth)


@app.route("/")
def home():
    return redirect(url_for("auth.login"))


if __name__ == "__main__":
    app.run(debug=True)