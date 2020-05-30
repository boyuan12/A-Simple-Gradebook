# A Simple Gradebook
![Python application](https://github.com/boyuan12/A-Simple-Gradebook/workflows/Python%20application/badge.svg)
[![Code style: yapf](https://img.shields.io/badge/code%20style-yapf-blue)](https://github.com/google/yapf)


This is A Simple Gradebook (ASG), not that simple after all. This is a gradebook management features with features like (planned) emailing, attendance, assignment and grade management, blog posting and even live chatting. And more that we thought or haven't thought about. This can be great used for a whole district, individual school, individual teacher or just home-school parents can choose this website. This is a fully opensource project and is built upon Flask.

## Installing
To install this repository, first clone the repository by execute following commands in your terminal/command prompt:

```
git clone https://github.com/boyuan12/A-Simple-Gradebook.git
cd A-Simple-Gradebook
```

## Usage
Then you need to make sure Python is installed, You can go to [https://python.org](https://python.org) to download the most current/stable version for your computer. Then make sure you have pip installed. Next, execute following commands in your terminal/command prompt:

```
pip install -r requirements.txt
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run
```

Now you should be able to go to [http://127.0.0.1:5000](http://127.0.0.1:5000) to see the homepage.

