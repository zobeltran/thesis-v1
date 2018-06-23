from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


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
    origin = db.Column("Origin", db.String(100))
    arrival = db.Column("Arrival", db.String(100))
    departureDate = db.Column("DepartureDate", db.Date)
    departureTime = db.Column("DepartureTime", db.Time)
    returnDate = db.Column("ReturnDate", db.Date)
    returnTime = db.Column("ReturnTime", db.Time)
    remainingSlots = db.Column("RemainingSlots", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    isExpired = db.Column("IsExpired", db.Boolean, default=False)
    isPackaged = db.Column("IsPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now())

    __tablename__ = "Tickets"


# Hotel Model
class Hotel(db.Model):
    id = db.Column("Id", db.Integer, primary_key=True)
    name = db.Column("Name", db.String(250))
    roomType = db.Column("Room Type", db.String(250))
    capacity = db.Column("Capacity", db.String(250))
    details = db.Column("Details", db.String(250))
    stayDays = db.Column("Days", db.Integer)
    stayNights = db.Column("Nights", db.Integer)
    expirationDate = db.Column("ExpirationDate", db.Date)
    isExpired = db.Column("IsExpired", db.Boolean)
    isPackaged = db.Column("isPackaged", db.Boolean, default=False)
    dateCreated = db.Column('DateCreated', db.DateTime, default=db.func.now())
    dateUpdated = db.Column('DateUpdated', db.DateTime, onupdate=db.func.now())

    __tablename__ = "Hotels"
