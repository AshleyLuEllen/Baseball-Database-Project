from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User, Teams


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class TeamYearSelectForm(FlaskForm):
    team_choices = sorted(set(map(lambda t: f"{t.name}, {t.teamID}", Teams.query.all())))
    year_choices = sorted(set(map(lambda t: f"{t.yearID}", Teams.query.all())), reverse=True)
    Team = SelectField('Team', choices=team_choices, validators=[DataRequired()], id='select_team')
    Year = SelectField('Year', choices=year_choices, validators=[DataRequired()], id='select_year')
    submit = SubmitField('Update Favorites')


class TeamYearSelectFormS(FlaskForm):
    team_choices = sorted(set(map(lambda t: f"{t.name}, {t.teamID}", Teams.query.all())))
    year_choices = sorted(set(map(lambda t: f"{t.yearID}", Teams.query.all())), reverse=True)
    Team = SelectField('Team', choices=team_choices, validators=[DataRequired()], id='select_team')
    Year = SelectField('Year', choices=year_choices, validators=[DataRequired()], id='select_year')
    submit = SubmitField('Search this team')


class TableSelectForm(FlaskForm):
    choices = ['Roster', 'Batting', 'Pitching', 'Managers']
    tableSelection = SelectField('Table', choices=choices, validators=[DataRequired()], id='select_table')
