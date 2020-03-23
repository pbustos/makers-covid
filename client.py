from socketIO_client import SocketIO, LoggingNamespace
"""
def on_aaa_response(args):
    print(1, args['data'])

socketIO = SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on(1, on_aaa_response)
socketIO.emit('prueba')
socketIO.wait(seconds=1)
"""

def lectura_json(args):
    print('solicitando:', args['data'])

socketIO = SocketIO('localhost', 8000, LoggingNamespace)
socketIO.on('solicitando', lectura_json)
socketIO.emit('json')
socketIO.wait(seconds=1)