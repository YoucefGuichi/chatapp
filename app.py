import csv

from flask import Flask, render_template, url_for
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_session import Session
import pandas as pd

app = Flask(__name__)
app.secret_key = 'super secret key yeep'
app.config['SESSION_TYPE'] = 'filesystem'

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
                return render_template('index.html', message=username)
            else:
                msg = "Username or password incorrect"
                return render_template('login.html', message=msg)
        else:
            msg = "Username or password incorrect"
            return render_template('login.html', message=msg)

    return render_template('login.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    df = pd.read_csv('database.csv')
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirmPassword")
        user_id = df['ID'].max() + 1
        if (email == "") or (username == "") or (password == "") or (confirm_password == ""):
            msg = "Please fill all the form"
            return render_template('register.html', message=msg)
        else:
            if password == confirm_password:
                if not (email in df['Email'].values) and not (username in df['Username'].values):
                    new_user = [user_id, username, password, email]
                    with open("database.csv", "a") as database:
                        db_writer = csv.writer(database)
                        db_writer.writerow(new_user)
                    return render_template('login.html')
                else:
                    msg = "User already exist"
                    return render_template('register.html', message=msg)
            else:
                msg = "Passwords are not the same"
                return render_template('register.html', message=msg)

    return render_template('register.html')


@app.route("/join_chat", methods=["GET", "POST"])
def join_chat():
    return render_template("index.html")


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":

        user_name = request.form.get("user_name")
        room_name = request.form.get("room")
        room_from_rooms_list = request.form.get("rooms_list")

        if room_name == "":
            session["room_name"] = room_from_rooms_list
        else:
            session["room_name"] = room_name

        session["username"] = user_name

        return render_template("chat_template.html", session=session)
    else:
        return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    users_data = pd.read_csv("database.csv")
    user_data_2 = users_data
    if request.method == "POST":
        # edit data
        if request.form.get("submit_button") == "Edit":
            user_name = request.form.get("username")
            password = request.form.get("password")
            id = request.form.get("id")
            user_data_2.set_index("ID", inplace=True)
            print(user_data_2.at[int(id), "Username"])
            user_data_2.at[int(id), "Username"] = user_name
            user_data_2.at[int(id), "Password"] = password
            user_data_2.to_csv("database.csv")

        # delete a particular row
        elif request.form.get("submit_button") == "Delete":
            user_data_2.set_index("ID", inplace=True)
            id = request.form.get("id")
            user_data_2.drop(index=int(id), inplace=True)
            user_data_2.to_csv("database.csv")

    users_data = pd.read_csv("database.csv")
    users_data.reset_index(inplace=True)
    users_data.rename({"Unnamed: 0": "id"})
    users = user_data_2.itertuples()
    column_names = user_data_2.columns.values

    return render_template("admin.html", users=users, column_names=column_names)


@socketio.on('join', namespace='/chat')
def join(message):
    room = session.get('room_name')
    print(room)
    print(session.get("username"))
    join_room(room)
    emit('status', {'msg': session.get('username') + ' has entered the room.'}, room=room)


@socketio.on('text', namespace='/chat')
def text(message):
    room = session.get('room_name')
    emit('message', {'msg': session.get('username') + ' : ' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
def left(message):
    room = session.get('room_name')
    username = session.get('username')
    leave_room(room)
    session.clear()
    emit('status', {'msg': username + ' has left the room.'}, room=room)


if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=80)
