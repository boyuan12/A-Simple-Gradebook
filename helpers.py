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


def get_best_elective(wishes, exists, user_id):
    """
    ### Get the best elective based on the provided arguments.

    Args:
    - codes: list - contains subject_id that their wish electives
    - exist: list - contains periods that they already had
    - user_id: int - the primary key from users table for the student
    """

    get_elective = False
    d_id = c.execute("SELECT district_id FROM users WHERE user_id=:id", {
        "id": user_id
    }).fetchall()[0][0]
    # loop through their wishes
    for wish in wishes:
        # check for available periods
        avails = {}
        periods = []
        subs = c.execute(
            "SELECT period FROM teacher_subject WHERE subject_id=:s_id AND current_enrollment < max_enrollment"
        ).fetchall()
        for i in subs:
            periods.append(i[0])
        # compare with exists period
        if (sorted(periods) == sorted(exists)):
            continue
        else:
            avail = [x for x in subs if x not in exists]  # [3]
            period = random.choice(avail)  # choose a random period
            avails = c.execute(
                "SELECT id FROM teacher_subject WHERE subject_id=:s_id AND current_enrollment < max_enrollment AND period=:period"
            ).fetchall()
            ts_id = random.choice(avails)
            c.execute(
                "UPDATE teacher_subject SET current_enrollment = :new WHERE id=:id",
                {
                    "new":
                    c.execute(
                        "SELECT current_enrollment FROM teacher_subject WHERE id=:id",
                        {
                            "id": ts_id
                        }).fetchall()[0][0] + 1,
                    "id":
                    ts_id
                })
            c.execute(
                "INSERT INTO student_subject (student_id, teacher_subject_id) VALUES (:s_id, :ts_id)",
                {"s_id": user_id})
            conn.commit()
            get_elective = True

    # get a random elective that is available (possible machine learning)