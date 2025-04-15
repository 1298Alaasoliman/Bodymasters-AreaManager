from flask import Flask
from flask_login import LoginManager, current_user

app = Flask(__name__)
login_manager = LoginManager(app)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return f'Current user: {current_user.username}, Role: {current_user.role}'
    else:
        return 'No user is logged in'

if __name__ == '__main__':
    app.run(debug=True)
