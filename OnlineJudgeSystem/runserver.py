"""
This script runs the OnlineJudgeSystem application using a development server.
"""


from os import environ
from OnlineJudgeSystem import app
import os

from flask_cors import CORS  

CORS(app,supports_credentials=True)


if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SECRET_KEY'] = os.urandom(24)
    app.run(HOST, PORT)
