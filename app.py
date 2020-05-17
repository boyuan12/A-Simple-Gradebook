from flask import Flask, render_template, request, flash, redirect, session, json, abort
import sqlite3
from helpers import upload_file, send_email, random_string, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from termcolor import colored
from werkzeug.exceptions import HTTPException
from openpyxl import load_workbook
import os

"""import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://6b4e24f141bd48a582f5b24b96095bbf@o393097.ingest.sentry.io/5241674",
    integrations=[FlaskIntegration()]
)"""

BASE_URL = "127.0.0.1:5000"

conn = sqlite3.connect('db.sqlite3', check_same_thread=False)
c = conn.cursor()

app = Flask(__name__)
app.config["SECRET_KEY"] = "haah"
app.config['UPLOAD_FOLDER'] = "files"

@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps({
        "code": e.code,
        "name": e.name,
        "description": e.description,
    })
    response.content_type = "application/json"
    return response


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/create-district", methods=["GET", "POST"])
def create_school():
    if request.method == "POST":
        # check for weather user provide all required information
        if not request.form.get("email") or not request.form.get("password") or not request.form.get("district-name") or not request.form.get("code") or not request.form.get("address") or not request.form.get("city") or not request.form.get("state") or not request.form.get("zip") or not request.form.get("motto"):
            flash("Please make sure to fill out all required fields", category="danger")
            return redirect("/create-district")

        if request.form.get("password") != request.form.get("confirmation"):
            flash("Wrong password confirmation")
            return redirect("/create-district")

        # check for whether the code already existed
        exist_code = c.execute("SELECT * FROM districts WHERE code=:code", {"code": request.form.get("code")}).fetchall()
        if len(exist_code) != 0:
            flash("Your code/district abbreviation already existed. Please change your district abbreviation", category="danger")
            return redirect("/create-district")

        # check whether the email already existed
        exist_code = c.execute("SELECT * FROM users WHERE email=:email", {"email": request.form.get("email")}).fetchall()
        if len(exist_code) != 0:
            flash("Your email already existed. Did you already registered?", category="danger")
            return redirect("/create-district")

        # get the address format
        if request.form.get("address2"):
            addr = request.form.get("address") + ", " + request.form.get("address2") + " " + request.form.get("city") + ", " + request.form.get("state") + " " + request.form.get("zip")
        else:
            addr = request.form.get("address") + ", " + request.form.get("city") + ", " + request.form.get("state") + " " + request.form.get("zip")

        # check for whether the address already existed
        exist_code = c.execute("SELECT * FROM districts WHERE address=:address", {"address": addr}).fetchall()
        if len(exist_code) != 0:
            flash("Your district address already existed. Did you already registered?", category="danger")
            return redirect("/create-district")

        filename = upload_file(app.config['UPLOAD_FOLDER'])

        c.execute("INSERT INTO districts (name, motto, logo, address, code) VALUES (:name, :motto, :logo, :address, :code)", {"name": request.form.get("district-name"), "motto": request.form.get("motto"), "logo": filename, "address": addr, "code": request.form.get("code")})

        conn.commit()

        district_id = c.execute("SELECT * FROM districts WHERE code=:code", {"code": request.form.get("code")}).fetchall()[0][0]

        print(colored(district_id, "red"))

        verification_str = random_string(50)
        c.execute("INSERT INTO users (school_id, name, username, password, role, district_id, email, verification) VALUES (0, :name, :username, :password, :role, :district_id, :email, :verification)", {"name": request.form.get("name"), "username": request.form.get("email"), "password": generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8), "role": "district-admin", "district_id": int(district_id), "email": request.form.get("email"), "verification": verification_str})
        conn.commit()

        send_email(request.form.get("email"), "Verify Your A Simple Gradebook Account!", f"Please click the link to verify your account:\n{BASE_URL}/verify/{verification_str}\n. Thanks for signing up!")

        return render_template("success.html", title="Register Success - Email Verification Needed", details="Thanks for registering! Please check your email to verify your email account. Once you click on the link in the email account, you will be directed for the next step to continue. Please check your spam folder as well. Thanks for signing up!")

    else:
        return render_template("create-district.html")


@app.route("/verify/<string:token>")
def verify(token):

    results = c.execute("SELECT * FROM users WHERE verification=:verification", {"verification": token}).fetchall()

    if len(results) != 1:
        return render_template("error.html", title="Wrong Verification Token", details="You provided wrong token or the email already verified. Please double check your email token. Thanks.")

    c.execute("UPDATE users SET verification=:verify WHERE verification=:token", {"verify": "verify", "token": token})
    conn.commit()

    flash("Your email is successfully verified. Please login", category="success")

    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        if not request.form.get("username") or not request.form.get("password"):
            flash("Please provide all required fields", category="danger")
            return redirect("/login")

        results = c.execute("SELECT * FROM users WHERE username=:username", {"username": request.form.get("username")}).fetchall()

        if len(results) != 1:
            flash("Wrong credentials, please register before use the service", category="danger")
            return redirect("/login")

        if check_password_hash(results[0][4], request.form.get("password")):
            if results[0][8] != "verified":
                flash("Please check your email for verification", category="warning")
            session["user_id"] = results[0][0]

            if request.args.get("next"):
                return redirect(f"/{request.args.get('next')}")

            if results[0][5] == "district-admin":
                district_info = c.execute("SELECT * FROM districts WHERE district_id=:id", {"id": results[0][6]}).fetchall()
                return redirect(f"/district-admin/{district_info[0][5]}")

        flash("Wrong credentials, please register before use the service", category="danger")
        return redirect("/login")

    else:
        return render_template("login.html")


@app.route("/district-admin/<string:code>")
@login_required
def district_admin_homepage(code):

    user_info = c.execute("SELECT * FROM users WHERE user_id=:user_id", {"user_id": session.get("user_id")}).fetchall()
    district = c.execute("SELECT * FROM districts WHERE code=:code", {"code": code}).fetchall()[0][0]
    if user_info[0][5] != "district-admin" or user_info[0][6] != district:
        abort(403)

    return render_template("district-admin-dashboard.html", code=code)


@app.route("/district-admin/<string:code>/schools", methods=["GET", "POST"])
@login_required
def district_admin_dashboard_school(code):

    user_info = c.execute("SELECT * FROM users WHERE user_id=:user_id", {"user_id": session.get("user_id")}).fetchall()
    district = c.execute("SELECT * FROM districts WHERE code=:code", {"code": code}).fetchall()[0][0]

    if user_info[0][5] != "district-admin" or user_info[0][6] != district:
        abort(403)

    if request.method == "POST":
        if request.form.get("name") and request.form.get("address") and request.form.get("description") and request.form.get("code"):
            # handle when the user submit a form manually
            c.execute("INSERT INTO schools (district_id, name, address, description, code) VALUES (:district_id, :name, :address, :description, :code)", {"district_id": int(district), "name": request.form.get("name"), "address": request.form.get("address"), "description": request.form.get("description"), "code": request.form.get("code")})
            conn.commit()
            return redirect(f"/district-admin/{code}/schools")

        elif request.files["excel"]:
            # handle when user submit an excel
            filename = upload_file(app.config["UPLOAD_FOLDER"])
            wb = load_workbook(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            sheet = wb.active

            # check if the columns is 4
            if sheet.max_columns != 4:
                flash("Wrong Format: Did you have EXACTLY 4 columns?", category="danger")
                return redirect(f"/district-admin/{code}/schools")

            for i in range(1, sheet.max_rows+1):
                name = sheet.cell(row=i, column=1)
                address = sheet.cell(row=i, column=2)
                description = sheet.cell(row=i, column=3)
                code = sheet.cell(row=i, column=4)

                c.execute("INSERT INTO schools (district_id, name, address, description, code) VALUES (:district_id, :name, :address, :description, :code)", {"district_id": int(district), "name": name, "address": address, "description": description, "code": code})
                conn.commit()

            return redirect(f"/district-admin/{code}/schools")

    else:
        schools = c.execute("SELECT * FROM schools WHERE district_id=:district_id", {"district_id": district}).fetchall()
        return render_template("district-admin-school.html", schools=schools, code=code)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")