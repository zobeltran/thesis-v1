from flask import Blueprint, render_template, request, redirect, session
from flask import url_for, flash
from urllib.parse import urlparse, urljoin
from flask_login import LoginManager, login_user, current_user
from flask_login import logout_user
from app import forms
from app.models import db, User, Ticket, Hotel, Customer
from app.models import LogTrail, FlightInquiry, HotelInquiry
from app.models import Package, FlightBooking, StripeCustomer
from app.models import Payments, HotelBooking, PackageBooking
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import timedelta, date, datetime
import stripe


view = Blueprint('main', __name__, template_folder='templates',
                 static_folder='static', static_url_path='/%s' % __name__)

bcrypt = Bcrypt()

loginManager = LoginManager()
loginManager.login_view = 'main.LogIn'
loginManager.login_message = 'Please log in'
loginManager.login_message_category = 'warning'

pubkey = 'pk_test_GjK3GmJJ1exs60wIcgTpfggq'
secretkey = 'sk_test_RXyvP1FBgkRyCwyEBGyZeymo'

stripe.api_key = secretkey

referenceNumber = datetime.now().strftime("%Y%m%d%H%M%S")


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
        user = User.query.filter(User.username == form.username.data).first()
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
                    return redirect(url_for('main.UserHomeFO'))
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
        emailUnique = User.query.filter(User.email == form.email.data).all()
        usernameUnique = (User.query
                          .filter(User.username == form.username.data).all())
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
            if form.role.data == "AD":
                role = "Admin"
            elif form.role.data == "RO":
                role = "Reservation Officer"
            else:
                role = "Financial Officer"
            event = (form.username.data +
                     ' registered as ' +
                     role)
            newLogTrail = LogTrail(event=event)
            db.session.add(newLogTrail)
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


@view.route('/user/home/FO', methods=['GET', 'POST'])
@login_required(role="FO")
def UserHomeFO():
    return render_template('result.html')


@view.route('/ticket/add', methods=['GET', 'POST'])
@login_required(role="RO")
def CreateTicket():
    form = forms.RegisterTicket()
    if form.validate_on_submit():
        expireDate = form.departureDate.data - timedelta(days=7)
        if form.arrivalDate.data < form.departureDate.data:
            errorMessage = ('%s must be greater than %s'
                            % (form.arrivalDate.label.text,
                               form.departureDate.label.text))
            form.arrivalDate.errors.append(errorMessage)
            return render_template('employee/flights/addTicket.html',
                                   form=form)
        if form.returnDate.data < form.arrivalDate.data:
            errorMessage = ('%s must be greater than %s'
                            % (form.returnDate.label.text,
                               form.arrivalDate.label.text))
            form.returnDate.errors.append(errorMessage)
            return render_template('employee/flights/addTicket.html',
                                   form=form)
        newTicket = Ticket(origin=form.origin.data,
                           arrival=form.arrival.data,
                           flightNo=form.flightNo.data,
                           departureDate=form.departureDate.data,
                           departureTime=form.departureTime.data,
                           arrivalDate=form.arrivalDate.data,
                           arrivalTime=form.arrivalTime.data,
                           returnDate=form.returnDate.data,
                           returnTime=form.returnTime.data,
                           expirationDate=expireDate,
                           remainingSlots=form.slots.data,
                           isPackaged=form.isPackaged.data,
                           price=form.price.data)
        db.session.add(newTicket)
        user = current_user
        fullName = user.firstName + ' ' + user.lastName
        if user.role == "AD":
            role = "Admin"
        elif user.role == "RO":
            role = "Reservation Officer"
        else:
            role = "Financial Officer"
        event = (fullName +
                 ' (' + role + ') created ' +
                 form.flightNo.data +
                 ' (' +
                 form.origin.data +
                 '-' +
                 form.arrival.data +
                 ')')
        newLogTrail = LogTrail(event=event)
        db.session.add(newLogTrail)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('employee/flights/addTicket.html', form=form)


@view.route('/hotel/add', methods=['GET', 'POST'])
@login_required(role="RO")
def CreateHotel():
    form = forms.RegisterHotel()
    if form.validate_on_submit():
        if form.checkOut.data < form.checkIn.data:
            errorMessage = ('%s must be greater than %s'
                            % (form.checkOut.label.text,
                               form.checkOut.label.text))
            form.checkOut.errors.append(errorMessage)
            return render_template('employee/hotels/addHotel.html',
                                   form=form)
        if form.checkIn.data <= form.expirationDate.data:
            errorMessage = ('%s must be less than %s'
                            % (form.expirationDate.label.text,
                               form.checkIn.label.text))
            form.expirationDate.errors.append(errorMessage)
            return render_template('employee/hotels/addHotel.html',
                                   form=form)
        newHotel = Hotel(name=form.name.data,
                         roomType=form.roomType.data,
                         capacity=form.capacity.data,
                         details=form.details.data,
                         checkIn=form.checkIn.data,
                         checkOut=form.checkOut.data,
                         remainingRooms=form.rooms.data,
                         expirationDate=form.expirationDate.data,
                         isPackaged=form.isPackaged.data,
                         price=form.price.data)
        db.session.add(newHotel)
        user = current_user
        fullName = user.firstName + ' ' + user.lastName
        if user.role == "AD":
            role = "Admin"
        elif user.role == "RO":
            role = "Reservation Officer"
        else:
            role = "Financial Officer"
        event = (fullName +
                 ' (' + role + ') created ' +
                 form.name.data +
                 ' (' +
                 form.roomType.data +
                 ')')
        newLogTrail = LogTrail(event=event)
        db.session.add(newLogTrail)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('employee/hotels/addHotel.html', form=form)


@view.route('/package/add', methods=['GET', 'POST'])
@login_required(role="RO")
def CreatePackage():
    form = forms.RegisterPackage()
    availableHotel = (Hotel.query.filter(Hotel.isExpired.is_(False))
                      .filter(Hotel.isPackaged.is_(True)).all())
    hotelList = [(h.id, (h.name + ' - ' + h.roomType)) for h in availableHotel]
    form.hotels.choices = hotelList
    availableTicket = (Ticket.query.filter(Ticket.isExpired.is_(False))
                       .filter(Ticket.isPackaged.is_(True)).all())
    ticketList = [(t.id, (t.flightNo + (' (' +
                                        t.origin +
                                        ' - ' +
                                        t.arrival +
                                        ')')))
                  for t in availableTicket]
    form.tickets.choices = ticketList
    if form.validate_on_submit():
        newPackage = Package(destination=form.destination.data,
                             days=form.days.data,
                             expirationDate=form.expirationDate.data,
                             remainingSlots=form.remainingSlots.data,
                             intenerary=form.intenerary.data,
                             inclusions=form.inclusions.data,
                             price=form.price.data,
                             hotel=form.hotels.data,
                             flight=form.tickets.data)
        db.session.add(newPackage)
        user = current_user
        fullName = user.firstName + ' ' + user.lastName
        if user.role == "AD":
            role = "Admin"
        elif user.role == "RO":
            role = "Reservation Officer"
        else:
            role = "Financial Officer"
        event = (fullName +
                 ' (' + role + ') created ' +
                 form.destination.data)
        newLogTrail = LogTrail(event=event)
        db.session.add(newLogTrail)
        db.session.commit()
        return redirect(url_for('main.UserHomeRO'))
    return render_template('employee/packages/addPackage.html', form=form)


@view.route('/inquiries', methods=['GET', 'POST'])
@login_required(role="RO")
def InquiriesLog():
    hotelInquiries = (HotelInquiry.query
                      .order_by(HotelInquiry.id.desc()).all())
    flightInquiries = (FlightInquiry.query
                       .order_by(FlightInquiry.id.desc()).all())
    return render_template('/employee/inquiries.html',
                           hotels=hotelInquiries,
                           flights=flightInquiries)


# Admin
@view.route('/logs')
@login_required(role="AD")
def LogTrails():
    logs = LogTrail.query.order_by(LogTrail.id.desc()).all()
    return render_template('employee/logs.html', logs=logs)


# Financial Officer
@view.route('/payments')
@login_required(role="FO")
def PaymentLogs():
    payments = Payments.query.order_by(Payments.id.desc()).all()
    ticketPaid = (FlightBooking.query
                  .filter(FlightBooking.isPaid.is_(True))
                  .order_by(FlightBooking.id.desc()).all())
    hotelPaid = (HotelBooking.query
                 .filter(HotelBooking.isPaid.is_(True))
                 .order_by(HotelBooking.id.desc()).all())
    packagePaid = (PackageBooking.query
                   .filter(PackageBooking.isPaid.is_(True))
                   .order_by(PackageBooking.id.desc()).all())
    return render_template('/employee/paymentLogs.html',
                           payments=payments,
                           tickets=ticketPaid,
                           hotels=hotelPaid,
                           packages=packagePaid)


# Customer Side
@view.route('/')
def HomePage():
    return render_template('customer/homepage.html')


@view.route('/flight/summary/id/<int:id>', methods=['GET', 'POST'])
def FlightSummary(id):
    flightSummary = Ticket.query.get(id)
    form = forms.CustomerCount()
    session['flightId'] = id
    if form.validate_on_submit():
        if form.customerCounter.data > flightSummary.remainingSlots:
            errorMessage = ('%s must be less than Remaining Slots'
                            % (form.customerCounter.label.text))
            form.customerCounter.errors.append(errorMessage)
            return render_template('customer/flightCounter.html',
                                   form=form, flightSummary=flightSummary)
        return redirect(url_for("main.BookCustomerFlights",
                                counter=form.customerCounter.data,
                                session=session['flightId']))
    return render_template('customer/flightCounter.html',
                           flightSummary=flightSummary, form=form)


@view.route('/hotel/summary/id/<int:id>', methods=['GET', 'POST'])
def HotelSummary(id):
    hotelSummary = Hotel.query.get(id)
    session['hotelId'] = id
    form = forms.RoomCount()
    if form.validate_on_submit():
        if form.rooms.data > hotelSummary.remainingRooms:
            errorMessage = ('%s must be less than Remaining Slots'
                            % (form.rooms.label.text))
            form.rooms.errors.append(errorMessage)
            return render_template('customer/hotelCounter.html',
                                   form=form, hotelSummary=hotelSummary)
        return redirect(url_for('main.BookCustomerHotels',
                                counter=form.rooms.data))
    return render_template('customer/hotelCounter.html',
                           hotelSummary=hotelSummary, form=form)


@view.route('/package/summary/id/<int:id>', methods=['GET', 'POST'])
def PackageSummary(id):
    packageSummary = Package.query.get(id)
    session['packageId'] = id
    form = forms.PackageCount()
    if form.validate_on_submit():
        if form.packageCount.data > packageSummary.remainingSlots:
            errorMessage = ('%s must be less than Remaining Slots'
                            % (form.packageCount.label.text))
            form.packageCount.errors.append(errorMessage)
            return render_template('customer/packageCounter.html',
                                   form=form, packageSummary=packageSummary)
        return redirect(url_for("main.BookCustomerPackages",
                                counter=form.packageCount.data,
                                id=id))
    return render_template('customer/packageCounter.html',
                           packageSummary=packageSummary, form=form)


@view.route('/flight/add/Customer/<int:counter>',
            methods=['GET', 'POST'])
def BookCustomerFlights(counter):
    form = forms.RegisterCustomerFlights(meta={'csrf': False})
    id = session['flightId']
    if form.validate_on_submit():
        for data in form.customer:
            customer = Customer(firstName=data.firstName.data,
                                lastName=data.lastName.data,
                                email=data.email.data,
                                contactNo=data.contactNo.data)
            db.session.add(customer)
            db.session.flush()
            flightTransaction = FlightBooking(referenceNumber=referenceNumber,
                                              customer=customer.id,
                                              flight=id)
            db.session.add(flightTransaction)
            db.session.commit()
        return redirect(url_for('main.PayFlights', counter=counter,
                                id=id, ref=referenceNumber))
    for count in range(counter):
        # form.customer.pop_entry()
        form.customer.append_entry()
    return render_template('customer/flightCustomerForm.html',
                           form=form,
                           counter=counter,
                           id=id)


@view.route('/hotel/add/Customer/<int:counter>', methods=['GET', 'POST'])
def BookCustomerHotels(counter):
    form = forms.RegisterCustomerHotels(meta={'csrf': False})
    id = session['hotelId']
    if form.validate_on_submit():
        for data in form.customer:
            customer = Customer(firstName=data.firstName.data,
                                lastName=data.lastName.data,
                                email=data.email.data,
                                contactNo=data.contactNo.data)
            db.session.add(customer)
            db.session.flush()
            hotelTransaction = HotelBooking(referenceNumber=referenceNumber,
                                            customer=customer.id,
                                            hotel=id)
            db.session.add(hotelTransaction)
            db.session.commit()
        return redirect(url_for('main.PayHotel', counter=counter,
                                id=id, ref=referenceNumber))
    form.customer.append_entry()
    return render_template('customer/hotelCustomerForm.html',
                           form=form,
                           counter=counter)


@view.route('/package/add/Customer/<int:counter>', methods=['GET', 'POST'])
def BookCustomerPackages(counter):
    form = forms.RegisterCustomerHotels(meta={'csrf': False})
    id = session['packageId']
    if form.validate_on_submit():
        for data in form.customer:
            customer = Customer(firstName=data.firstName.data,
                                lastName=data.lastName.data,
                                email=data.email.data,
                                contactNo=data.contactNo.data)
            db.session.add(customer)
            db.session.flush()
            pTransaction = PackageBooking(referenceNumber=referenceNumber,
                                          customer=customer.id,
                                          package=id)
            db.session.add(pTransaction)
            db.session.commit()
        return redirect(url_for('main.PayPackage', counter=counter,
                                id=id, ref=referenceNumber))
    for count in range(counter):
        # form.customer.pop_entry()
        form.customer.append_entry()
    return render_template('customer/packageCustomerForm.html',
                           form=form,
                           counter=counter)


@view.route('/inquiry')
def Inquire():
    return render_template('customer/inquiry.html')


@view.route('/inquiry/flights', methods=['GET', 'POST'])
def InquireFlights():
    form = forms.InquiryFlights()
    if form.validate_on_submit():
        if form.arrivalDate.data < form.departureDate.data:
            errorMessage = ('%s must be greater than %s'
                            % (form.arrivalDate.label.text,
                               form.departureDate.label.text))
            form.arrivalDate.errors.append(errorMessage)
            return render_template('customer/inquiryFlight.html', form=form)
            return render_template('customer/inquiryFlight.html', form=form)
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
    (Ticket.query.filter(Ticket.expirationDate <= now)
     .update({Ticket.isExpired: True}))
    db.session.commit()
    viewFlights = (Ticket.query.filter(Ticket.isExpired.is_(False))
                   .filter(Ticket.remainingSlots > 0)
                   .filter(Ticket.isPackaged.is_(False)).all())
    return render_template('customer/viewFlights.html',
                           viewFlights=viewFlights)


@view.route('/view/hotels/', methods=['GET', 'POST'])
def ViewHotels():
    now = date.today()
    (Hotel.query.filter(Hotel.expirationDate <= now)
     .update({Hotel.isExpired: True}))
    viewHotels = (Hotel.query.filter(Hotel.isExpired.is_(False))
                  .filter(Hotel.remainingRooms > 0)
                  .filter(Hotel.isPackaged.is_(False)).all())
    return render_template('customer/viewHotels.html', viewHotels=viewHotels)


@view.route('/view/packages', methods=['GET', 'POST'])
def ViewPackages():
    now = date.today()
    (Package.query.filter(Package.expirationDate <= now)
     .update({Package.isExpired: True}))
    viewPackages = (Package.query.filter(Package.isExpired.is_(False))
                    .filter(Package.remainingSlots > 0).all())
    return render_template('customer/viewPackages.html',
                           viewPackages=viewPackages)


@view.route('/payment/flights/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def PayFlights(counter, id, ref):
    flight = Ticket.query.get(id)
    return render_template('customer/paymentFlights.html',
                           flight=flight, referenceNumber=ref,
                           counter=counter, pubkey=pubkey)


@view.route('/payment/hotel/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def PayHotel(counter, id, ref):
    hotel = Hotel.query.get(id)
    return render_template('customer/paymentHotel.html',
                           hotel=hotel, referenceNumber=ref,
                           counter=counter, pubkey=pubkey)


@view.route('/payment/package/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def PayPackage(counter, id, ref):
    package = Package.query.get(id)
    return render_template('customer/paymentPackage.html',
                           package=package, referenceNumber=ref,
                           counter=counter, pubkey=pubkey)


@view.route('/charge/flights/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def ChargeFlights(counter, id, ref):
    flights = Ticket.query.get(id)
    email = request.form['stripeEmail']
    source = request.form['stripeToken']
    customer = (StripeCustomer.query
                .filter(StripeCustomer.email == email).first())
    price = int(flights.price) * counter
    if customer is None:
        customerStripe = (stripe.Customer
                          .create(email=email,
                                  source=source))
        newCustomer = StripeCustomer(email=email,
                                     stripeCustomerId=customerStripe.id)
        db.session.add(newCustomer)
        db.session.flush()
        db.session.commit()
        customer = (StripeCustomer.query
                    .filter(StripeCustomer.email == email).first())

    charge = stripe.Charge.create(customer=customer.stripeCustomerId,
                                  amount=price * 100,
                                  currency="php",
                                  description=(flights.flightNo +
                                               '(' +
                                               flights.origin +
                                               ' - ' +
                                               flights.arrival +
                                               ')'))
    newPayment = Payments(paymentReference=referenceNumber,
                          bookingReference=ref,
                          paymentFor='Flights',
                          stripeCustomer=customer.id,
                          stripeChargeId=charge.id)
    db.session.add(newPayment)
    db.session.commit()
    ticketCount = flights.remainingSlots - counter
    (Ticket.query.filter(Ticket.id == id)
     .update({Ticket.remainingSlots: ticketCount}))
    (FlightBooking.query.filter(FlightBooking.referenceNumber == ref)
     .update({FlightBooking.isPaid: True}))
    db.session.commit()
    return redirect(url_for('main.ConfirmFlight'))


@view.route('/charge/packages/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def ChargePackage(counter, id, ref):
    package = Package.query.get(id)
    email = request.form['stripeEmail']
    source = request.form['stripeToken']
    customer = (StripeCustomer.query
                .filter(StripeCustomer.email == email).first())
    price = int(package.price) * counter
    if customer is None:
        customerStripe = (stripe.Customer
                          .create(email=email,
                                  source=source))
        newCustomer = StripeCustomer(email=email,
                                     stripeCustomerId=customerStripe.id)
        db.session.add(newCustomer)
        db.session.flush()
        db.session.commit()
        customer = (StripeCustomer.query
                    .filter(StripeCustomer.email == email).first())
    charge = stripe.Charge.create(customer=customer.stripeCustomerId,
                                  amount=price * 100,
                                  currency="php",
                                  description=(package.destination))
    newPayment = Payments(paymentReference=referenceNumber,
                          bookingReference=ref,
                          paymentFor='Packages',
                          stripeCustomer=customer.id,
                          stripeChargeId=charge.id)
    db.session.add(newPayment)
    db.session.commit()
    packageCount = package.remainingSlots - counter
    (Package.query.filter(Package.id == id)
     .update({Package.remainingSlots: packageCount}))
    (PackageBooking.query.filter(PackageBooking.referenceNumber == ref)
     .update({PackageBooking.isPaid: True}))
    db.session.commit()
    return redirect(url_for('main.ConfirmPackage'))


@view.route('/charge/hotels/<int:counter>/<int:id>/<string:ref>',
            methods=['GET', 'POST'])
def ChargeHotel(counter, id, ref):
    hotels = Hotel.query.get(id)
    email = request.form['stripeEmail']
    source = request.form['stripeToken']
    customer = (StripeCustomer.query
                .filter(StripeCustomer.email == email).first())
    price = int(hotels.price) * counter
    if customer is None:
        customerStripe = (stripe.Customer
                          .create(email=email,
                                  source=source))
        newCustomer = StripeCustomer(email=email,
                                     stripeCustomerId=customerStripe.id)
        db.session.add(newCustomer)
        db.session.flush()
        db.session.commit()
        customer = (StripeCustomer.query
                    .filter(StripeCustomer.email == email).first())
    charge = stripe.Charge.create(customer=customer.stripeCustomerId,
                                  amount=price * 100,
                                  currency="php",
                                  description=(hotels.name +
                                               '(' +
                                               hotels.roomType +
                                               ')'))
    newPayment = Payments(paymentReference=referenceNumber,
                          bookingReference=ref,
                          paymentFor='Hotels',
                          stripeCustomer=customer.id,
                          stripeChargeId=charge.id)
    db.session.add(newPayment)
    db.session.commit()
    hotelCount = hotels.remainingRooms - counter
    (Hotel.query.filter(Hotel.id == id)
     .update({Hotel.remainingRooms: hotelCount}))
    (HotelBooking.query.filter(HotelBooking.referenceNumber == ref)
     .update({HotelBooking.isPaid: True}))
    db.session.commit()
    return redirect(url_for('main.ConfirmHotel'))


@view.route('/payment/packages/confimed',
            methods=['GET', 'POST'])
def ConfirmPackage():
    return render_template('customer/chargePackages.html')


@view.route('/payment/flights/confimed',
            methods=['GET', 'POST'])
def ConfirmFlight():
    return render_template('customer/chargeFlights.html')


@view.route('/payment/hotels/confimed',
            methods=['GET', 'POST'])
def ConfirmHotel():
    return render_template('customer/chargeHotel.html')
