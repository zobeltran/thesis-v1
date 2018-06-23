from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, flash
from urllib.parse import urlparse, urljoin
from flask_login import LoginManager, login_user, current_user
from flask_login import logout_user
from app import forms
from app.models import db, User, Ticket
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import timedelta

view = Blueprint('main', __name__, template_folder='templates',
                 static_folder='static', static_url_path='/%s' % __name__)

bcrypt = Bcrypt()

loginManager = LoginManager()
loginManager.login_view = 'main.LogIn'
loginManager.login_message = 'Please log in'
loginManager.login_message_category = 'warning'


@loginManager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return loginManager.unauthorized()
            userRole = current_user.role
            if(userRole != role and role != "ANY"):
                return loginManager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper


# User Side
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (test_url.scheme in ('http', 'https') and
            ref_url.netloc == test_url.netloc)


@view.route('/login', methods=['GET', 'POST'])
def LogIn():
    session['next'] = request.args.get('next')
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            inputPassword = form.password.data
            dbPassword = user.password
            checkBcrypt = bcrypt.check_password_hash(dbPassword, inputPassword)
            role = user.role
            if checkBcrypt:
                login_user(user)
                if role == "RO":
                    return redirect(url_for('main.UserHomeRO'))
                elif role == "FO":
                    return redirect(url_for('main.Login'))
                else:
                    return redirect(url_for('main.UserHomeAD'))
            flash('Invalid Credentials', 'error')
            return render_template('login.html', form=form)
        flash('Username does not Exist', category='error')
        return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@view.route('/user/register', methods=['GET', 'POST'])
def Register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        passwordBcrypt = bcrypt.generate_password_hash(form.password.data)
        emailUnique = User.query.filter_by(email=form.email.data)
        usernameUnique = User.query.filter_by(username=form.username.data)
        if usernameUnique:
            flash('Username already Existing', 'error')
        elif emailUnique:
            flash('Email already Existing', 'error')
        else:
            newUser = User(username=form.username.data,
                           password=passwordBcrypt.decode('utf-8'),
                           firstName=form.firstName.data,
                           lastName=form.lastName.data,
                           email=form.email.data,
                           role=form.role.data)
            db.session.add(newUser)
            db.session.commit()
            return redirect(url_for('main.LogIn'))
    return render_template('register.html', form=form)


@view.route('/logout')
def LogOut():
    logout_user()
    return redirect(url_for('main.LogIn'))


# Admin Side
@view.route('/user/home', methods=['GET', 'POST'])
@login_required(role="AD")
def UserHomeAD():
    return render_template('result.html')


# Reservation Officer Side
@view.route('/user/home', methods=['GET', 'POST'])
@login_required(role="RO")
def UserHomeRO():
    return render_template('result.html')


# Financial Officer Side


@login_required(role="RO")
@view.route('/ticket/add', methods=['GET', 'POST'])
def CreateTicket():
    form = forms.RegisterTicket()
    if form.validate_on_submit():
        expireDate = form.departureDate.data - timedelta(days=7)
        newTicket = Ticket(origin=form.origin.data,
                           arrival=form.arrival.data,
                           departureDate=form.departureDate.data,
                           departureTime=form.departureTime.data,
                           returnDate=form.arrivalDate.data,
                           returnTime=form.arrivalTime.data,
                           expirationDate=expireDate,
                           remainingSlots=form.slots.data,
                           isPackaged=form.isPackaged.data)
        db.session.add(newTicket)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('addTicket.html', form=form)
# Customer Side
