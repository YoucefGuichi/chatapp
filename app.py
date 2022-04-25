from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import pandas
import pandas as pd

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.config["SESSION_TYPE"] = "filesystem"

Session(app)
socketio = SocketIO(app, manage_session=False)


@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("home.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    df = pd.read_csv('database.csv')
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username in df['Username'].values:
            nb = df.index[df['Username'] == username].values
            if password == df.iloc[nb.max(None)]['Password']:
                return render_template('index.html')
            else:
                print('Username or password incorrect')
        else:
            print('Username or password incorrect')

    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    df = pd.read_csv('database.csv')
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmPassword = request.form.get("confirmPassword")
        ID = df['ID'].max() + 1
        if email is not None and username is not None and password is not None and confirmPassword is not None:
            if password == confirmPassword:
                if not (email in df['Email'].values) and not (username in df['Username'].values):
                    new_user = {
                        'ID': [ID],
                        'Username': [username],
                        'Password': [password],
                        'Email': [email]
                    }
                    df = pd.DataFrame(new_user)
                    df.to_csv('database.csv', mode='a', index=False, columns=['ID', 'Username', 'Password', 'Email'])
                    return render_template('login.html')
                else:
                    print("User already exist!!")
            else:
                print("Passwords do not match!!")
        else:
            print("Please fill all the form")

    return render_template('register.html')


@app.route("/join_chat", methods=["GET", "POST"])
def join_chat():
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


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room_name')
    join_room(room)
    emit('status', {'msg': session.get('nickname') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room_name')
    emit('message', {'msg': session.get('nickname') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room_name')
    username = session.get('nickname')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True)
