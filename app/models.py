from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


# Log In Trail
class LogTrail(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    event = db.Column("Event", db.String(250))
    eventTime = db.Column("EventTime", db.DateTime, default=db.func.now())

    __tablename__ = "LogTrail"


# User Models
class User(db.Model, UserMixin):
    id = db.Column('Id', db.Integer, primary_key=True)
    username = db.Column('Username', db.String(100))
    password = db.Column('Password', db.String(250))
    email = db.Column('Email', db.String(250))
    firstName = db.Column('FirstName', db.String(250))
    lastName = db.Column('LastName', db.String(250))
    role = db.Column('Role', db.String(100))
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now())

    def getId(self):
        return self.id

    def isActive(self):
        return self.isActive

    def activateUser(self):
        self.activateUser = True

    def getUsername(self):
        return self.username

    def getRole(self):
        return self.role

    __tablename__ = 'Users'


# Tickets Model
class Ticket(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    flightNo = db.Column("FlightNo", db.String(100))
    origin = db.Column("Origin", db.String(100))
    arrival = db.Column("Arrival", db.String(100))
    departureDate = db.Column("DepartureDate", db.Date)
    departureTime = db.Column("DepartureTime", db.Time)
    arrivalDate = db.Column("ArrivalDate", db.Date)
    arrivalTime = db.Column("ArrivalTime", db.Time)
    returnDate = db.Column("ReturnDate", db.Date)
    returnTime = db.Column("ReturnTime", db.Time)
    remainingSlots = db.Column("RemainingSlots", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    price = db.Column('Price', db.Integer)
    isExpired = db.Column("IsExpired", db.Boolean, default=False)
    isPackaged = db.Column("IsPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now())
    ticketBooking = db.relationship("FlightBooking", backref='Flight',
                                    lazy=True)
    packageFlight = db.relationship('Package', backref='Tickets', lazy=True)

    __tablename__ = "Tickets"

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '{} ({} - {})'.format(self.flightNo,
                                     self.origin,
                                     self.arrival)


# Hotel Model
class Hotel(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(250))
    roomType = db.Column("Room Type", db.String(250))
    capacity = db.Column("Capacity", db.String(4))
    details = db.Column("Details", db.String(300))
    checkIn = db.Column("CheckIn", db.DateTime)
    checkOut = db.Column("CheckOut", db.DateTime)
    price = db.Column('Price', db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    isExpired = db.Column("IsExpired", db.Boolean, default=False)
    isPackaged = db.Column("isPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now())
    remainingRooms = db.Column('RemainingRooms', db.Integer)
    hotelBooking = db.relationship("HotelBooking", backref='Hotel',
                                   lazy=True)
    packageHotel = db.relationship('Package', backref='Hotels', lazy=True)

    __tablename__ = "Hotels"

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '{} ({})'.format(self.name,
                                self.roomType)


# Customer Model
class Customer(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    firstName = db.Column("FirstName", db.String(250))
    lastName = db.Column("LastName", db.String(250))
    email = db.Column("Email", db.String(100))
    contactNo = db.Column("Contact", db.String(50))
    hotelBooking = db.relationship("HotelBooking", backref='Customer',
                                   lazy=True)
    flightBooking = db.relationship("FlightBooking", backref='Customer',
                                    lazy=True)
    packageBooking = db.relationship("PackageBooking", backref='Customer',
                                     lazy=True)

    __tablename__ = "Customers"

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '{} {} ({})'.format(self.firstName,
                                   self.lastName,
                                   self.email)


class FlightInquiry(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    firstName = db.Column("FirstName", db.String(100))
    lastName = db.Column("lastName", db.String(100))
    email = db.Column("Email", db.String(100))
    origin = db.Column("Origin", db.String(100))
    arrival = db.Column("Arrival", db.String(100))
    departureDate = db.Column("DepartureDate", db.Date)
    arrivalDate = db.Column("ArrivalDate", db.Date)
    time = db.Column("DesiredTime", db.String(100))
    adult = db.Column("NumberOfAdults", db.Integer)
    child = db.Column("NumberOfChild", db.Integer)
    infant = db.Column("NumberOfInfant", db.Integer)
    note = db.Column("Note", db.String(300))

    __tablename__ = "FlightInquiry"


class HotelInquiry(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    firstName = db.Column("FirstName", db.String(100))
    lastName = db.Column("lastName", db.String(100))
    email = db.Column("Email", db.String(100))
    location = db.Column("Location", db.String(100))
    budget = db.Column("Budget", db.Integer)
    guest = db.Column("Guest", db.Integer)
    checkIn = db.Column("checkInDate", db.Date)
    checkOut = db.Column("checkOutDate", db.Date)
    note = db.Column("Note", db.String(300))

    __tablename__ = "HotelInquiry"


class Package(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    destination = db.Column("Destination", db.String(50))
    price = db.Column('Price', db.Integer)
    days = db.Column("DaysOfStay", db.Integer)
    intenerary = db.Column("Intenerary", db.String(1000))
    inclusions = db.Column("Inclusions", db.String(1000))
    remainingSlots = db.Column("RemainingSlots", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    note = db.Column("Note", db.String(1000))
    hotel = db.Column('HotelsFk', db.Integer, db.ForeignKey('Hotels.Id'))
    flight = db.Column('FlightFk', db.Integer, db.ForeignKey('Tickets.Id'))
    isExpired = db.Column('isExpired', db.Boolean, default=False)
    packageBooking = db.relationship("PackageBooking", backref='Package',
                                     lazy=True)

    __tablename__ = 'Packages'

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return '{}'.format(self.destination)


class PackageBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('Customers.Id'))
    package = db.Column('PackagesFk', db.Integer, db.ForeignKey('Packages.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'PackageBooking'


class HotelBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('Customers.Id'))
    hotel = db.Column('HotelsFk', db.Integer, db.ForeignKey('Hotels.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'HotelBooking'


class FlightBooking(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    referenceNumber = db.Column("ReferenceNumber", db.String(50))
    customer = db.Column('CustomersFk', db.Integer,
                         db.ForeignKey('Customers.Id'))
    flight = db.Column('FlightFk', db.Integer, db.ForeignKey('Tickets.Id'))
    isPaid = db.Column('IsPaid', db.Boolean, default=False)

    __tablename__ = 'TicketBooking'


class StripeCustomer(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    email = db.Column("Email", db.String(50))
    stripeCustomerId = db.Column("StripeCustomerId", db.String(50))

    __tablename__ = 'StripeCustomers'


class Payments(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    paymentReference = db.Column("PaymentReference", db.String(50))
    bookingReference = db.Column("BookingReference", db.String(50))
    paymentFor = db.Column("PaymentFor", db.String(50))
    stripeCustomer = db.Column("StripeCustomer",
                               db.ForeignKey('StripeCustomers.Id'))
    stripeChargeId = db.Column("StripChargeId", db.String(50))

    __tablename__ = "Payments"
