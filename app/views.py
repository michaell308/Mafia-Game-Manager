from flask import Flask, render_template
from app import app
from flask.ext.socketio import SocketIO

socketio = SocketIO(app)

user = {'username': 'Yan'} 
messages = [ 
		{
			'author': {'username':'John'},
			'body':'Hi'
		},
		{
			'author':{'username': 'Johnny'},
			'body': 'Hi!'
		}
		]

@app.route('/')
@app.route('/index')
def index():
	return render_template('chatsystem.html')

@app.route('/message/', methods=['GET', 'POST'])
def echo():
    ret_data = {"value": request.args.get('echoValue')}
    return render_template('chatsystem.html',
    						messages)

@socketio.on('my event', namespace='/chat')
def test_message(message):
    emit('my response', {'data': message['data']})

@socketio.on('new message', namespace='/chat')
def broadcast_message(message):
	print "hi"
	message.append({'username': user.username, 'message': message})
	emit('new message', {'username': user.username, 'message': message}, broadcast=True)

@socketio.on('connect', namespace='/chat')
def test_connect():
    emit('chat logs', {'data': messages})

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    print "Client dicsconnected lol"

if __name__ == '__main__':
	socketio.run(app)