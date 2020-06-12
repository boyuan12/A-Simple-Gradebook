import os
import smtplib
import random
import string
from flask import render_template, session, redirect, request
from functools import wraps


def upload_file(UPLOAD_FOLDER):
    file = request.files["file"]
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return file.filename


def send_email(receiver, subject, body):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.ehlo()
        server.starttls()
        server.login('longlivesaltienation@gmail.com', 'longlivesalties')
        msg = f"Subject: {subject}\n\n{body}"
        server.sendmail('longlivesaltienation@gmail.com', receiver, msg)
        server.quit()
    except:
        print('An error occurred while sending email')


def random_string(digits=30):
    random_str = ""
    for i in range(digits):
        char = random.choice(string.ascii_letters)
        random_str += char

    return random_str


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login?next=" + request.path)
        return f(*args, **kwargs)

    return decorated_function


def dcode_to_did(d_code):
    return c.execute("SELECT * FROM districts WHERE code=:d_code", {
        "d_code": d_code
    }).fetchall()[0][0]
