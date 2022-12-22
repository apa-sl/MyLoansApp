# import os
import mysql.connector
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from decimal import Decimal
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to mysql database
db = mysql.connector.connect(
    host="127.0.0.1",
    user="ENTER_USER_NAME",
    password="ENTER_PASSWORD",
    database="ENTER_DB_NAME"
)
# initialize a cursor that is always catching all rows from the query and as dicts (not as tuples)
cursor = db.cursor(buffered=True, dictionary=True)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/login", methods=["GET", "POST"])
def login():

    #forget any user_id
    session.clear()

    # user reached route via POST (by submitting a form via POST)
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Please provide username", 403)
        elif not request.form.get("password"):
            return apology("Please provide password", 403)

        # query database for username
        query = ("SELECT * FROM users WHERE email = %s")
        data = (request.form.get("username"),)
        cursor.execute(query, data)
        user = cursor.fetchone()

        # check if username exists and password is correct
        if user == None or not check_password_hash(user["password_hash"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # remember logged in user in the session
        session["user_id"] = user["id"]
        print(session)
        # redirect user to the home page
        return redirect("/")

    # user reached the view via GET (by a link)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # user reached route via POST (by submitting a form)
    if request.method == "POST":
        # save provided data as variables:
        name = request.form.get("name")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # validate provied data
        ## check if name is provided:
        if not name:
            return apology("Please provide your name", 400)
        ## check if username is provided:
        if not username:
            return apology("must provide username", 400)
        ## Check that pasword is provided
        elif not password:
            return apology("must provide password", 400)
        ## Check that password is retyped
        elif not confirmation:
            return apology("must retype password", 400)
        ## Check if there is mismatch in password:
        elif password != confirmation:
            return apology("password mismatch", 400)

        ## query DB for username
        query = ("SELECT * FROM users WHERE email = %s")
        data = (username,)
        cursor.execute(query, data)
        user = cursor.fetchone()
        print(type(user))
        print(user)
        ## check if provided username already exists
        if user != None:
            return apology("username already in use", 400)\

        # add user to the database
        ## Generate password hash
        password_hash = generate_password_hash(password)

        ## insert into db
        query = ("INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)")
        data = (name, username, password_hash)
        cursor.execute(query, data)
        db.commit()
        
        # login freshly registered user
        # Remember which user has logged in
        query = ("SELECT * FROM users WHERE email = %s")
        data = (username,)
        cursor.execute(query, data)
        user = cursor.fetchone()
        session["user_id"] = user["id"]

        # Redirect user to home page
        return redirect("/")

    # user reached route via GET (as by url or link)
    else:
        return render_template("register.html")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    
    if request.method == "POST":

        # TODO
        return render_template("index.html")
    else:
        # get loans in progress (count & amount)
        query = ("SELECT COUNT(id) AS id FROM loans WHERE loan_amount_outstanding != 0 AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        result = cursor.fetchone()
        loans_inpro_count = result["id"]

        query = ("SELECT SUM(loan_amount_outstanding) AS sum FROM loans WHERE loan_amount_outstanding != 0 AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        result = cursor.fetchone()
        loans_inpro_amount = result["sum"]

        # get closed loans (count & amount)
        query = ("SELECT COUNT(id) AS id FROM loans WHERE loan_amount_outstanding = 0 AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        result = cursor.fetchone()
        loans_closed_count = result["id"]

        query = ("SELECT SUM(loan_amount_total) AS sum FROM loans WHERE loan_amount_outstanding = 0 AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        result = cursor.fetchone()
        loans_closed_amount = result["sum"]

        # get installments due this month
        query = ("SELECT loans.id AS id, loans.name AS name, installments.amount AS installment_amount, installments.payment_date AS due FROM installments JOIN loans ON installments.loan_id = loans.id WHERE MONTH(payment_date) = MONTH(CURDATE()) AND payment_status = False AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        loans_now = cursor.fetchall()

        # get total amount to pay this month
        loans_now_total = 0
        for loan in loans_now:
            loans_now_total += loan["installment_amount"]

        # get installments due next month
        query = ("SELECT loans.id AS id, loans.name AS name, installments.amount AS installment_amount, installments.payment_date AS due FROM installments JOIN loans ON installments.loan_id = loans.id WHERE MONTH(payment_date) = MONTH(DATE_ADD(CURDATE(), INTERVAL 1 MONTH)) AND payment_status = False AND user_id = %s")
        data = (session["user_id"],)
        cursor.execute(query, data)
        loans_soon = cursor.fetchall()

        # get total amount to pay next month
        loans_soon_total = 0
        for loan in loans_soon:
            loans_soon_total += loan["installment_amount"]
        return render_template("index.html", loans_inpro_count = loans_inpro_count, loans_inpro_amount = loans_inpro_amount, loans_closed_count = loans_closed_count, loans_closed_amount = loans_closed_amount, month_current = loans_now, month_current_total = loans_now_total, month_next = loans_soon, month_next_total = loans_soon_total)


@app.route("/add-loan", methods=["GET", "POST"])
@login_required
def add_loan():
    cursor.execute("SELECT * FROM vendors")
    vendors = cursor.fetchall()

    if request.method == "POST":
        # get loan data from the form
        loan = {}
        loan["name"] = request.form.get("loan_name")
        loan["vendor_id"] = int(request.form.get("vendor"))
        if "id_needed" in request.form:
            loan["id_needed"] = True
            loan["agreement_id"] = request.form.get("agreement_id")
        else:
            loan["id_needed"] = False
            loan["agreement_id"]  = None
        loan["start_date"] = datetime.strptime(request.form.get("start_date"), '%Y-%m-%d')
        loan["installment_amount"] = Decimal(request.form.get("installment_amount"))
        loan["installments_count"] = int(float(request.form.get("installments_count")))
        loan["end_date"] = loan["start_date"] + relativedelta(months=+loan["installments_count"]
        if "last_installment_diff" in request.form:
            loan["last_installment_diff"] = True
            loan["last_installment_amount"] = Decimal(request.form.get("last_installment_amount"))
        else:
            loan["last_installment_diff"] = False
        loan["due_day"] = int(float(request.form.get("due_day")))

        # validate loan data from the form
        if not loan["name"]:
            print("Provide proper name")
            return render_template("add-loan.html", vendors=vendors)
        if not loan["vendor_id"]:
            print("Select proper vendor")
            return render_template("add-loan.html", vendors=vendors)
        if loan["id_needed"] == True and not loan["agreement_id"]:
             print("Provide agreement ID")
             return render_template("add-loan.html", vendors=vendors)
        if not loan["installment_amount"]:
            print("Provide proper installment amount")
            return render_template("add-loan.html", vendors=vendors)
        if not loan["start_date"]:
            print("Provide proper start date")
            return render_template("add-loan.html", vendors=vendors)
        if not loan["installments_count"]:
            print("Provide proper start date")
            return render_template("add-loan.html", vendors=vendors)
        if loan["last_installment_diff"] == True and not loan["last_installment_amount"]:
            print("Provide proper last installment amount")
            return render_template("add-loan.html", vendors=vendors)
        if not loan["due_day"]:
            print("Provide proper due day")
            return render_template("add-loan.html", vendors=vendors)
        # TODO: , add loan to the DB, inform user that it has been added.

        # calculate loan total amount
        if loan["last_installment_diff"] == True:
            loan["amount_total"] = loan["installment_amount"] * (loan["installments_count"] - 1) + loan["last_installment_amount"]

        else:
            loan["amount_total"] = loan["installment_amount"] * loan["installments_count"]
        
        print(loan)
        # store loan in the DB
        try:
            # add loan to the loans table & get id of the newly created loan
            query = ("INSERT INTO loans (name, user_id, vendor_id, start_date, end_date, agreement_id, due_day, loan_amount_total, loan_amount_outstanding) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
            data = (loan["name"], session["user_id"], loan["vendor_id"], loan["start_date"], loan["end_date"], loan["agreement_id"], loan["due_day"], loan["amount_total"], loan["amount_total"])
            cursor.execute(query, data)

            # get the id of newly inserted loan into the db
            loan["id"] = cursor.lastrowid

            # add installments for the loan to the installments table
            installments_to_add = loan["installments_count"]
            # if last installment amount is different, add it and regular installments - 1
            if loan["last_installment_diff"] == True:
                installments_to_add -= 1
                query = ("INSERT INTO installments (loan_id, amount, payment_date) VALUES (%s, %s, %s)")
                data = (loan["id"], loan["last_installment_amount"], loan["end_date"])
                cursor.execute(query, data)
            # add regular installments
            for i in range(installments_to_add):
                installment_payment_date = loan["start_date"] + relativedelta(months=+(i+1))
                print(installment_payment_date)
                query = ("INSERT INTO installments (loan_id, amount, payment_date) VALUES (%s, %s, %s)")
                data = (loan["id"], loan["installment_amount"], installment_payment_date)
                cursor.execute(query, data)
            
            # commit changes in the database
            db.commit()

        except mysql.connector.Error as err:
            # rollback in case of error
            db.rollback()
            print("Something went wrong with SQL: {}".format(err))

        return render_template("index.html")
        #return render_template("add-loan.html")
    else:
        return render_template("add-loan.html", vendors=vendors)
        
@app.route("/loan-details/<int:loan_id>", methods=["GET", "POST"])
@login_required
def loan_details(loan_id):
    query = ("SELECT loans.id AS id, loans.name AS name, vendors.name AS vendor, agreement_id, loan_amount_total, loan_amount_outstanding FROM loans JOIN vendors ON loans.vendor_id = vendors.id WHERE loans.id = %s")
    data = (loan_id,)
    cursor.execute(query, data)
    session["loan"] = cursor.fetchone() # we should get a 1 dictionary with details requested in the SQL query
    query = ("SELECT id, amount, payment_date, payment_status FROM installments WHERE loan_id = %s")
    data = (loan_id,)
    cursor.execute(query, data)
    session["loan"]["installments"] = cursor.fetchall()

    print(session["loan"])
    return render_template("loan_details.html", loan=session["loan"])

@app.route("/installment-edit/<int:loan_id>/<int:installment_id>/<string:action>", methods=["GET", "POST"])
@login_required
def installment_edit(loan_id, installment_id, action):
    match action:
        case "pay":
            status = 1
            try:
                # update installment status in db
                print(status)
                query = ("UPDATE installments SET payment_status = '%s' WHERE id = %s")
                data = (status, installment_id)
                cursor.execute(query, data)

                # update loan outstanding amount in db
                ## get updated installment amount
                query = ("SELECT amount FROM installments WHERE id = %s")
                data = (installment_id,)
                cursor.execute(query, data)
                installment_amount = cursor.fetchone()
                ## get current loan amount outstanding and decrease it by paid installment amount
                query = ("SELECT loan_amount_outstanding FROM loans WHERE id = %s")
                data = (loan_id,)
                cursor.execute(query, data)
                result = cursor.fetchone()
                loan_amount_outstanding = result["loan_amount_outstanding"] - installment_amount["amount"]
                ## update loan amount outstanding in the DB
                query = ("UPDATE loans SET loan_amount_outstanding = %s WHERE id = %s")
                data = (loan_amount_outstanding, loan_id)
                cursor.execute(query, data)

                # commit changes in the database
                db.commit()
                return render_template("loan_details.html", loan=session["loan"])
    
            except mysql.connector.Error as err:
                # rollback in case of error
                db.rollback()
                # return print("Something went wrong with SQL: {}".format(err))
                return render_template("loan_details.html", loan=session["loan"])
    
        case "undopay":
            status = 0
            try:
                # update installment status in db
                print(status)
                query = ("UPDATE installments SET payment_status = '%s' WHERE id = %s")
                data = (status, installment_id)
                cursor.execute(query, data)

                # update loan outstanding amount in db
                ## get updated installment amount
                query = ("SELECT amount FROM installments WHERE id = %s")
                data = (installment_id,)
                cursor.execute(query, data)
                installment_amount = cursor.fetchone()
                print(installment_amount)
                ## get current loan amount outstanding and decrease it by paid installment amount
                query = ("SELECT loan_amount_outstanding FROM loans WHERE id = %s")
                data = (loan_id,)
                cursor.execute(query, data)
                result = cursor.fetchone()
                loan_amount_outstanding = result["loan_amount_outstanding"] + installment_amount["amount"]
                ## update loan amount outstanding in the DB
                query = ("UPDATE loans SET loan_amount_outstanding = %s WHERE id = %s")
                data = (loan_amount_outstanding, loan_id)
                cursor.execute(query, data)

                # commit changes in the database
                db.commit()
                return render_template("loan_details.html", loan=session["loan"])
    
            except mysql.connector.Error as err:
                # rollback in case of error
                db.rollback()
                # return print("Something went wrong with SQL: {}".format(err))
                return render_template("loan_details.html", loan=session["loan"])
        
        case _:
            return redirect("/")
    
    
    # return redirect("/loan-details/loan_id")
    