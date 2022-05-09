from io import BytesIO
from flask import Flask, render_template, redirect, url_for, request, send_file, session
import mysql.connector
import pandas as pd
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import sqlalchemy
app = Flask(__name__)

app.config['SECRET_KEY'] = 'supersecretkey'


# Enter your database connection details below
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'amine_oualid'
app.config['MYSQL_PASSWORD'] = 'Esith.2022'
app.config['MYSQL_DB'] = 'pythonlogin'
app.config['MYSQL_DB1'] = 'smartflow'
app.config['MYSQL_DB2'] = 'sap_mm'
# Intialize MySQL
mysql = MySQL(app)



@app.route("/", methods=['GET', 'POST'])
@app.route('/index')
@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))



# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
@app.route("/forward/", methods=['POST'])
def move_forward():
 
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM smartflow.inventory_product;')

    account = cursor.fetchall()


    df= pd.DataFrame(data=account, columns=['id','title','quantity','type'])
    
    df.to_csv("inventory_product.csv")
    return render_template('home.html')

@app.route("/integration/", methods=['POST'])
def integration():
 
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    df=pd.read_csv("inventory_product.csv")

    database_connection = sqlalchemy.create_engine('mysql+mysqlconnector://{0}:{1}@{2}/{3}'.
                                               format(app.config['MYSQL_USER'], app.config['MYSQL_PASSWORD'], 
                                                      app.config['MYSQL_HOST'], app.config['MYSQL_DB2']))
    df.to_sql(con=database_connection, name='inventory_product', if_exists='replace')
    return render_template('home.html')

    
if __name__ == '__main__':
    app.run(debug=True)
