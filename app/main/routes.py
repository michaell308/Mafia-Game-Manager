from flask import session, render_template
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
	"""
	Default page is chat for now
	"""
	return render_template('chatsystem.html')


