from flask import Flask
from os import getenv
from app.routes import view, loginManager, bcrypt
from app.models import db, migrate
from app.forms import csrf

# Flask Activation
app = Flask(__name__, static_folder=None)

# Config Set
secretKey = getenv('SECRET_KEY')
dbUri = getenv('SQLALCHEMY_DATABASE_URI')
sqlTrackModifcation = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
useSessionNext = getenv('USE_SESSION_FOR_NEXT')
recaptchaPub = getenv('RECAPTCHA_PUBLIC_KEY')
recaptchaPri = getenv('RECAPTCHA_PRIVATE_KEY')
# Config Activation
app.config['SECRET_KEY'] = secretKey
app.config['SQLALCHEMY_DATABASE_URI'] = dbUri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = sqlTrackModifcation
app.config['USE_SESSION_FOR_NEXT'] = useSessionNext
app.config['RECAPTCHA_PUBLIC_KEY'] = recaptchaPub
app.config['RECAPTCHA_PRIVATE_KEY'] = recaptchaPri

# Sql Alchemy Activation
db.init_app(app)

# Flask-Login Activation
loginManager.init_app(app)

# Flask-Migrate Activation
migrate.init_app(app, db)

# Bcrypt Activation
bcrypt.init_app(app)

# Register Blueprints
app.register_blueprint(view)

# CSRF
csrf.init_app(app)

if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run()
