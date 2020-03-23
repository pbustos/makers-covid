from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import json 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('connect')
def handle_connection():
    #print('New connection: ')
    with open('data.json') as file:
        data = json.load(file)
        emit('connection_response', {'data': data})


def update(update):
    print("Broadcasting update")
    socketio.emit('update', { "data" : update}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=8000)
    

