from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send
import json 

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on('connect')
def handle_connection():
    #print('New connection: ')
    with open('data.json') as file:
        data = json.load(file)
        emit('connection_response', {'data': data})


def update(update):
    print("Broadcasting update")
    emit('update', { "data" : update}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=8000)



