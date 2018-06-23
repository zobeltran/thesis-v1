from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms import IntegerField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import InputRequired, Length, EqualTo, Email


class LoginForm(FlaskForm):
    username = StringField('Username',
                           [InputRequired('Username Required'),
                            Length(min=4, max=15)])
    password = PasswordField('Password',
                             [InputRequired('Password is Required'),
                              Length(min=8, max=80)])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField('Username',
                           [InputRequired('Username is Required')])
    password = PasswordField('Password',
                             [InputRequired('Password is Required'),
                              Length(min=8, max=80),
                              EqualTo('confirm',
                                      'Your Password does not Match')])
    confirm = PasswordField('Repeat Password',
                            [InputRequired('Repeat your Password')])
    firstName = StringField('First Name',
                            [InputRequired('First Name is Required'),
                             Length(max=50)])
    lastName = StringField('Last Name',
                           [InputRequired('Last Name is Required'),
                            Length(max=50)])
    email = StringField('Email',
                        [InputRequired('Email is Required'),
                         Email('Not a valid Email')])
    role = SelectField('Role',
                       choices=[('RO', 'Reservation Officer'),
                                ('FO', 'Financial Officer'),
                                ('AD', 'Admin')])


class RegisterTicket(FlaskForm):
    origin = StringField('Origin',
                         [InputRequired('Origin is Required')])
    arrival = StringField('Arrival',
                          [InputRequired('Arrival is Required')])
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
