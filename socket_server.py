import eventlet
import socketio

sio = socketio.Server(async_mode='eventlet')
app = socketio.WSGIApp(sio)

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def message(sid, data):
    print('Message received:', data)
    sio.emit('message', data)  # Broadcast the message to all connected clients

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 8001)), app)
