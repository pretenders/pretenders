from os.path import join, dirname

from bottle import static_file, jinja2_template as template

from pretenders.server import app

STATIC_FILE_LOCATION = join(dirname(__file__), 'static')


@app.route('/')
def homepage():
    return template('index.html')


@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root=STATIC_FILE_LOCATION)
