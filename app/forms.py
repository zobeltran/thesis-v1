from flask_wtf import FlaskForm, CSRFProtect, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms import IntegerField, TextAreaField, FormField, FieldList
from wtforms import DecimalField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from wtforms.validators import NumberRange, ValidationError, Optional
from datetime import date

csrf = CSRFProtect()
# Validation Messages
# Register User Validations
usernameLength = ('Username has a minimum of 4 and a maximum '
                  'of 100 characters.')
passwordLength = ('Password has a minimum of 8 and a maximum '
                  'of 100 characters.')
firstNameLength = ('First Name has a maximum of 100 characters.')
lastNameLength = ('Last Name has a maximum of 100 characters.')
contactnoLength = ('Contact Number must be at least 7 digits')
# Register Ticket Validations
originLength = ('Origin has a maximum of 50 characters.')
arrivalLength = ('Arrival has a maximum of 50 characters.')
numberAdult = ('Number of Adult must be at least 1')
# Register Hotel Validations
hotelNameLength = ('Name has a maximum of 100 characters.')
roomTypeLength = ('Room Type has a maximum of 100 characters')
roomDetailsLength = ('Room Details has maximum of 300 characters')
# Inquire Hotel Validations
numberGuest = ('Number of Guest must be at least 1')
budget = ('Budget must be at lease 500 pesos')
# Register Package Validations
destinationLength = ('Destination has a maximum of 50 characters.')
# Fight Counter
customerCount = ('Customer Count must not be lower than 1')


def DateCheck(form, field):
    if field.data < date.today():
        raise ValidationError(('%s must not be past '
                               'today' % (field.label.text)))


def AfterDateCheck(form, field, fieldTwo):
    if field.data > fieldTwo.data:
        raise ValidationError(field.label +
                              (' must not be before '
                               + fieldTwo.label))


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
    recaptcha = RecaptchaField()


class RegisterTicket(FlaskForm):
    flightNo = StringField('Flight Number',
                           [InputRequired('Flight Number is Required')])
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
    arrivalTime = TimeField('Arrival Time',
                            [InputRequired('Arrival Time is Required')])
    returnDate = DateField('Return Date',
                           [InputRequired('Return Date is Required')])
    returnTime = TimeField('Return Time',
                           [InputRequired('Return Time is Required')])
    slots = IntegerField('Slots',
                         [InputRequired('Slots are Required')])
    price = DecimalField('Price',
                         [InputRequired('Price is Required')])
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
    checkIn = DateField('Check In Date',
                        [InputRequired('CheckIn Date is Required')])
    checkOut = DateField('Check Out Date',
                         [InputRequired('Check Out Date is Required')])
    expirationDate = DateField('Expiration Date',
                               [InputRequired('Expiration Date is Required')])
    price = DecimalField('Price',
                         [InputRequired('Price is Required')])
    isPackaged = BooleanField('Packaged')


class RegisterCustomerFlightsFields(FlaskForm):
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    contactNo = IntegerField('Contact Number',
                             [InputRequired('Contact Number is Required'),
                              Length(min=7, message=contactnoLength)])


class RegisterCustomerFlights(FlaskForm):
    customer = FieldList(FormField(RegisterCustomerFlightsFields))


class RegisterCustomerHotelsFields(FlaskForm):
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    contactNo = IntegerField('Contact Number',
                             [InputRequired('Contact Number is Required'),
                              Length(min=7, message=contactnoLength)])


class RegisterCustomerHotels(FlaskForm):
    customer = FieldList(FormField(RegisterCustomerHotelsFields))


class InquiryFlights(FlaskForm):
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    origin = StringField('Origin Location',
                         [InputRequired('Origin Location is Required'),
                          Length(max=100, message=originLength)])
    arrival = StringField('Arrival Location',
                          [InputRequired('Arrival Location is Required'),
                           Length(max=100, message=arrivalLength)])
    departureDate = DateField('Departure Date',
                              [InputRequired('Departure Date is Required')])
    arrivalDate = DateField('Arrival Date',
                            [InputRequired('Arrival Date is Required')])
    time = SelectField('Desired Time',
                       choices=[('AM', 'AM'),
                                ('PM', 'PM')])
    adult = IntegerField('Number of Adults',
                         [InputRequired('Number is Required'),
                          NumberRange(min=1, message=numberAdult)],
                         default=1)
    child = IntegerField('Number of Child',
                         [InputRequired('Number is Required')],
                         default=0)
    infant = IntegerField('Number of Infant(Below 2 years old)',
                          [InputRequired('Number is Required')],
                          default=0)
    note = TextAreaField('Note')


class InquiryHotels(FlaskForm):
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=100, message=firstNameLength)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=100, message=lastNameLength)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    location = StringField('Location',
                           [InputRequired('Please input a location')])
    budget = IntegerField('Budget Range',
                          [InputRequired('Input Budget Range'),
                           NumberRange(min=500, message=budget)],
                          default=500)
    guest = IntegerField('Number of Guest',
                         [InputRequired('Input Number of Guest'),
                          NumberRange(min=1, message=numberGuest)],
                         default=1)
    checkIn = DateField('Check-in Date',
                        [InputRequired('Check-in Date is Required'),
                         DateCheck])
    checkOut = DateField('Check-out Date',
                         [InputRequired('Check-out Date is Required'),
                          DateCheck])
    note = TextAreaField('Note')


class RegisterPackage(FlaskForm):
    destination = StringField('Destination',
                              [InputRequired('Input Destination'),
                               Length(max=50, message='destinationLength')])
    price = DecimalField('Price',
                         [InputRequired('Price is Required')])
    days = IntegerField('Days of Stay',
                        [InputRequired('Days of Stay Required')])
    intenerary = TextAreaField('Intenerary',
                               [InputRequired('Intenerary is Required')])
    inclusions = TextAreaField('Inclusions',
                               [InputRequired('Inclusions is Required')])
    remainingSlots = IntegerField('Remaining Slots',
                                  [InputRequired('Slots is Required')])
    expirationDate = DateField('Expiration Date',
                               [InputRequired('Expiration Date is Required')])
    hotels = SelectField('Hotels', coerce=int)
    tickets = SelectField('Flights', coerce=int)


class CustomerCount(FlaskForm):
    customerCounter = IntegerField('Customer Count',
                                   [InputRequired('Customer Count is Needed'),
                                    NumberRange(min=1,
                                                message=customerCount)])
