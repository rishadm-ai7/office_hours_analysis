from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_usxer, login_required, logout_user, current_user
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired 
import os
from flask_wtf.file import MultipleFileField

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class UploadForm(FlaskForm):
    excel_files = MultipleFileField('Excel Files', validators=[DataRequired(), FileAllowed(['xls', 'xlsx'], 'Excel files only!')])
    push_data = SubmitField('Push Data')


users = {'admin': {'password': 'admin'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class UploadForm(FlaskForm):
    multiple_files = MultipleFileField('Excel Files', validators=[DataRequired(), FileAllowed(['xls', 'xlsx'], 'Excel files only!')])
    push_data = SubmitField('Push Data')

def process_data(df):
    try:
        pattern = r'\b(\d{2}-\w{3}-\d{4})\b'
        date_series = pd.Series(df.to_string()).str.extract(pattern)
        report_date_str = pd.to_datetime(date_series[0], format='%d-%b-%Y').dt.strftime('%Y-%m-%d').iloc[0]

        start_location = np.where(df == 'SNo')
        row_num, col_num = start_location[0][0], start_location[1][0]
        df = df.iloc[row_num:, col_num:]
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        df = df.dropna(axis=1, how='any')
        df['report_date'] = report_date_str
        db_credentials = {
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST'),
            'port': os.getenv('DB_PORT'),
            'database': os.getenv('DB_DATABASE')
        }

        engine = create_engine(f"postgresql://{db_credentials['user']}:{db_credentials['password']}@{db_credentials['host']}:{db_credentials['port']}/{db_credentials['database']}")
        df.to_sql('public.office_hours', con=engine, index=False, if_exists='append')

        return f"Data pushed successfully!"
    except Exception as e:
        return f"Error processing and pushing data: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in users and password == users[username]['password']:
            user = User(username)
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = UploadForm()

    if form.validate_on_submit():
        excel_files = form.multiple_files.data

        for excel_file in excel_files:
            df = pd.read_excel(excel_file)
            result_message = process_data(df)
            flash(result_message, 'success')

    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
