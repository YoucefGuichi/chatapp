from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


@app.route("/")
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


if __name__ == "__main__":
    socketio.run(app)

# todo: https://www.youtube.com/watch?v=2-S-PMWJVxM
