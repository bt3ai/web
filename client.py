# client.py
import socketio
import random
import time
sio = socketio.Client(logger=True, engineio_logger=True)

@sio.event
def connect():
    print('Connected to server')

@sio.event
def response(data):
    print('Server says:', data)

@sio.event
def disconnect():
    print('Disconnected from server')

sio.connect('https://daoyi.ai')
for i in range(100000):
    num = random.randint(1, 12)
    num2 = random.randint(1, 1000)
    num_str = str(num2 )
    msg = {'Id': num, 'Status': num_str}
    sio.emit('update_message', msg) 
    time.sleep(1)
sio.wait()
