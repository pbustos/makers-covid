from socketIO_client import SocketIO, LoggingNamespace


def response(args):
    print('solicitando:', args['data'])

socketIO = SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on('connection_response', response)
socketIO.emit('connect')
socketIO.wait(seconds=1)


while True:
    socketIO.wait(seconds=1)

