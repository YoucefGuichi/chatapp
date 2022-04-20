from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["SESSION_TYPE"] = "filesystem"


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        nickname = request.form["nickname"]
        room_name = request.form["room"]

        # pass values to session
        session["nickname"] = nickname
        session["room_name"] = room_name
        return render_template("chat_template.html", session=session)
    else:
        return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

# todo: https://www.youtube.com/watch?v=2-S-PMWJVxM
