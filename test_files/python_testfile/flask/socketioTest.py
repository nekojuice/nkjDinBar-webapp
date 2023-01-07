from flask import Flask, render_template, Response
from flask_socketio import SocketIO



app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('socketTest.html')


@socketio.on('clicktest')
def test(text,text2):
    print(text,text2)

@socketio.on('msg')
def test(text):
    print(text)

# @socketio.on('send')
# def chat(data):
#     socketio.emit('get', data)

# @socketio.on('test')
# def test():
#     socketio.send("test")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port='5000')