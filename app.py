from flask import Flask, render_template
from config import SECRET_KEY

from routes.events import events_bp
from routes.tickets import tickets_bp
from routes.admin import admin_bp

app = Flask(__name__)
app.secret_key = SECRET_KEY

@app.route("/")
def home():
    return render_template("index.html")

app.register_blueprint(events_bp)
app.register_blueprint(tickets_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)