from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, flash
from urllib.parse import urlparse, urljoin
from flask_login import LoginManager, login_user, current_user
from flask_login import logout_user
from app import forms
from app.models import db, User, Ticket, Hotel, Customer
from app.models import LogTrail, FlightInquiry, HotelInquiry
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import timedelta, date

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
            if role == "AD":
                if((userRole != role) and role != "ANY"):
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
                loggedUser = current_user
                fullName = loggedUser.firstName + ' ' + loggedUser.lastName
                if loggedUser.role == "AD":
                    role = "Admin"
                elif loggedUser.role == "RO":
                    role = "Reservation Officer"
                else:
                    role = "Financial Officer"
                event = (fullName + ' (' + role + ') logged in')
                newLogTrail = LogTrail(event=event)
                db.session.add(newLogTrail)
                db.session.commit()
                if role == "RO":
                    return redirect(url_for('main.UserHomeRO'))
                elif role == "FO":
                    return redirect(url_for('main.LogIn'))
                else:
                    return redirect(url_for('main.UserHomeRO'))
            flash('Invalid Credentials', 'error')
            return render_template('employee/login.html', form=form)
        flash('Username does not Exist', category='error')
        return render_template('employee/login.html', form=form)
    return render_template('employee/login.html', form=form)


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
    return render_template('employee/register.html', form=form)


@view.route('/logout')
def LogOut():
    user = current_user
    fullName = user.firstName + ' ' + user.lastName
    if user.role == "AD":
        role = "Admin"
    elif user.role == "RO":
        role = "Reservation Officer"
    else:
        role = "Financial Officer"
    event = (fullName + ' (' + role + ') logged out')
    newLogTrail = LogTrail(event=event)
    db.session.add(newLogTrail)
    db.session.commit()
    logout_user()
    return redirect(url_for('main.LogIn'))


# Reservation Officer Side
@view.route('/user/home', methods=['GET', 'POST'])
@login_required(role="RO")
def UserHomeRO():
    return render_template('result.html')


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
                           isPackaged=form.isPackaged.data,
                           price=form.price.data)
        db.session.add(newTicket)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('employee/flights/addTicket.html', form=form)


@login_required(role="RO")
@view.route('/hotel/add', methods=['GET', 'POST'])
def CreateHotel():
    form = forms.RegisterHotel()
    if form.validate_on_submit():
        newHotel = Hotel(name=form.name.data,
                         roomType=form.roomType.data,
                         capacity=form.capacity.data,
                         details=form.details.data,
                         checkIn=form.checkIn.data,
                         checkOut=form.checkOut.data,
                         expirationDate=form.expirationDate.data,
                         isPackaged=form.isPackaged.data,
                         price=form.price.data)
        db.session.add(newHotel)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('employee/hotels/addHotel.html', form=form)


# Financial Officer
# Customer Side
@view.route('/')
def HomePage():
    return render_template('customer/homepage.html')


@view.route('/flight/summary/id/<int:id>', methods=['GET', 'POST'])
def FlightSummary(id):
    flightSummary = Ticket.query.get(id)
    return render_template('customer/flightCounter.html',
                           flightSummary=flightSummary)


@view.route('/flight/add/Customer/<int:counter>', methods=['GET', 'POST'])
@forms.csrf.exempt
def BookCustomerFlights(counter):
    form = forms.RegisterCustomerFlights(meta={'csrf': False})
    if form.validate_on_submit():
        for data in form.customer:
            customer = Customer(firstName=data.firstName.data,
                                lastName=data.lastName.data)
            db.session.add(customer)
            db.session.commit()
        return redirect(url_for('main.FlightSummary'))
    for count in range(counter):
        form.customer.pop_entry()
        form.customer.append_entry()
    return render_template('customer/flightCustomerForm.html', form=form,
                           counter=counter)


@view.route('/inquiry')
def Inquire():
    return render_template('customer/inquiry.html')


@view.route('/inquiry/flights', methods=['GET', 'POST'])
def InquireFlights():
    form = forms.InquiryFlights()
    if form.validate_on_submit():
        data = FlightInquiry(firstName=form.firstName.data,
                             lastName=form.lastName.data,
                             email=form.email.data,
                             origin=form.origin.data,
                             arrival=form.arrival.data,
                             departureDate=form.departureDate.data,
                             arrivalDate=form.arrivalDate.data,
                             time=form.time.data,
                             adult=form.adult.data,
                             child=form.child.data,
                             infant=form.child.data,
                             note=form.note.data)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('main.Inquire'))
    return render_template('customer/inquiryFlight.html', form=form)


@view.route('/inquiry/hotels', methods=['GET', 'POST'])
def InquireHotels():
    form = forms.InquiryHotels()
    if form.validate_on_submit():
        if form.checkOut.data < form.checkIn.data:
            errorMessage = ('%s must be greater than %s'
                            % (form.checkOut.label.text,
                               form.checkIn.label.text))
            form.checkOut.errors.append(errorMessage)
            return render_template('customer/inquiryHotel.html', form=form)
        data = HotelInquiry(firstName=form.firstName.data,
                            lastName=form.lastName.data,
                            email=form.email.data,
                            location=form.location.data,
                            budget=form.budget.data,
                            guest=form.guest.data,
                            checkIn=form.checkIn.data,
                            checkOut=form.checkOut.data,
                            note=form.note.data)
        db.session.add(data)
        db.session.commit()
        return redirect(url_for('main.Inquire'))
    return render_template('customer/inquiryHotel.html', form=form)


@view.route('/view/flights', methods=['GET', 'POST'])
def ViewFlights():
    now = date.today()
    viewFlights = Ticket.query.filter(Ticket.isExpired.is_(False)).all()
    (Ticket.query.filter(Ticket.expirationDate <= now)
     .update({Ticket.isExpired: True}))
    db.session.commit()
    return render_template('customer/viewFlights.html',
                           viewFlights=viewFlights)


@view.route('/view/hotels', methods=['GET', 'POST'])
def ViewHotels():
    viewHotels = Hotel.query.all()
    db.session.commit()
    return render_template('customer/viewHotels.html', viewHotels=viewHotels)
