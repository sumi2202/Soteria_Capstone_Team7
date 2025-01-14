from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dhfbdbfjksd hfjksdkjdh'


    @app.route('/')
    def homepage():
        return "Welcome!"


    return app