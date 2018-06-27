from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms import IntegerField, TextAreaField, FormField, FieldList
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, Length, EqualTo, Email

csrf = CSRFProtect()
# Validation Messages
# Register User Validations
usernameLength = ('Username has a minimum of 4 and a maximum '
                  'of 100 characters.')
passwordLength = ('Password has a minimum of 8 and a maximum '
                  'of 100 characters.')
firstNameLength = ('First Name has a maximum of 100 characters.')
lastNameLength = ('Last Name has a maximum of 100 characters.')
# Register Ticket Validations
originLength = ('Origin has a maximum of 50 characters.')
arrivalLength = ('Arrival has a maximum of 50 characters.')
# Register Hotel Validations
hotelNameLength = ('Name has a maximum of 100 characters.')
roomTypeLength = ('Room Type has a maximum of 100 characters')
roomDetailsLength = ('Room Details has maximum of 300 characters')


class LoginForm(FlaskForm):
    username = StringField('Username',
                           [InputRequired('Username Required')])
    password = PasswordField('Password',
                             [InputRequired('Password is Required')])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           [InputRequired('Username is Required'),
                            Length(min=4, max=100, message=usernameLength)])
    password = PasswordField('Password',
                             [InputRequired('Password is Required'),
                              Length(min=8, max=100, message=passwordLength),
                              EqualTo('confirm',
                                      'Your Password does not Match')])
    confirm = PasswordField('Repeat Password',
                            [InputRequired('Repeat your Password')])
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    role = SelectField('Role',
                       choices=[('RO', 'Reservation Officer'),
                                ('FO', 'Financial Officer'),
                                ('AD', 'Admin')])


class RegisterTicket(FlaskForm):
    origin = StringField('Origin',
                         [InputRequired('Origin is Required'),
                          Length(max=50, message=originLength)])
    arrival = StringField('Arrival',
                          [InputRequired('Arrival is Required'),
                           Length(max=50, message=arrivalLength)])
    departureDate = DateField('Departure Date',
                              [InputRequired('Departure Date is Required')])
    departureTime = TimeField('Departure Time',
                              [InputRequired('Departure Time is Required')])
    arrivalDate = DateField('Arrival Date',
                            [InputRequired('Arrival Date is Required')])
    arrivalTime = TimeField('Arrival Time', [])
    slots = IntegerField('Slots',
                         [InputRequired('Slots are Required')])
    isPackaged = BooleanField('Packaged')


class RegisterHotel(FlaskForm):
    name = StringField('Hotel Name',
                       [InputRequired('Hotel Name is Required'),
                        Length(max=100, message=hotelNameLength)])
    roomType = StringField('Room Type',
                           [InputRequired('Room Type is Required'),
                            Length(max=100, message=roomTypeLength)])
    capacity = IntegerField('Number of Capacity',
                            [InputRequired('Capacity is Required')])
    details = TextAreaField('Room Details',
                            [InputRequired('Room Details is Required'),
                             Length(max=300, message=roomDetailsLength)])
    stayDays = IntegerField('Days of Stay',
                            [InputRequired('Days of Stay is Required')])
    stayNights = IntegerField('Nights of Stay',
                              [InputRequired('Nights of Stay is Required')])
    expirationDate = DateField('Expiration Date',
                               [InputRequired('Expiration Date is Required')])
    isPackaged = BooleanField('Packaged')


class RegisterCustomerFlightsFields(FlaskForm):
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])


class RegisterCustomerFlights(FlaskForm):
    customer = FieldList(FormField(RegisterCustomerFlightsFields))
