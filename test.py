import unittest

from app import app
import os

from time import sleep
import io
import random
import string


def random_string(digits=30):
    random_str = ""
    for i in range(digits):
        char = random.choice(string.ascii_letters)
        random_str += char

    return random_str


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    # Test homepage
    def test_home(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    # test database
    def test_database(self):
        try:
            os.remove("temp.sqlite3")
        except FileNotFoundError:
            pass
        f = open("temp.sqlite3", "w")
        f.close()
        tester = os.path.exists("temp.sqlite3")
        self.assertTrue(tester)

    def create_district(self, email, name, password, confirmation,
                        district_name, code, motto, address, city, state, zip):
        return self.app.post("/create-district",
                             data=dict(email=email,
                                       password=password,
                                       confirmation=confirmation,
                                       district_name=district_name,
                                       code=code,
                                       motto=motto,
                                       address=address,
                                       city=city,
                                       state=state,
                                       zip=zip,
                                       file=(io.BytesIO(b"abcdef"),
                                             'test.jpg'),
                                       follow_redirects=False,
                                       content_type='multipart/form-data'))

    def login(self, username, password):
        return self.app.post('/login',
                             data=dict(username=username, password=password),
                             follow_redirects=True)

    def test_login_messages(self):
        """Test login messages using helper functions."""
        # test whether login without password successful
        rv = self.login("fakeaccount@example.com", "")
        assert b'Please provide all required fields' in rv.data

        # test whether login without username successful
        rv = self.login("", "fakepassword")
        assert b'Please provide all required fields' in rv.data

        # test whether login successful WITHOUT correct credentials
        rv = self.login("fakeemail@example.com", "fakepassword")
        assert b"Wrong credentials, please register before use the service" in rv.data

        # test login WITH correct credentials
        rv = self.login("asg-demo@example.com", "ASGDemo")
        assert b"Demo" in rv.data

    def create_school(self, name, address, description, code):
        self.login("asg-demo@example.com", "ASGDemo")
        return self.app.post("/district-admin/ASGDemo/schools",
                             data=dict(name=name,
                                       address=address,
                                       description=description,
                                       code=code))

    def test_create_school(self):
        """Test for ability to successfully create school"""
        self.login("asg-demo@example.com", "ASGDemo")
        # try create school without provide name of the school
        rv = self.create_school(
            "", "somewhere", "somedescription", "code"
        )  # will create 400 eror because it will try to check excel file exist or not
        assert (rv.status_code == 400)

        # try create school without provide address of the school
        rv = self.create_school(
            "someschool", "", "somedescription", "code"
        )  # will create 400 eror because it will try to check excel file exist or not
        assert (rv.status_code == 400)

        # try create school without provide description of the school
        rv = self.create_school(
            "someschool", "schoolwhere", "", "code"
        )  # will create 400 eror because it will try to check excel file exist or not
        assert (rv.status_code == 400)

        # try create school without provide code of the school
        rv = self.create_school(
            "someschool", "someaddress", "somedescription", ""
        )  # will create 400 eror because it will try to check excel file exist or not
        assert (rv.status_code == 400)

        # try create school provide code of the school
        rv = self.create_school("someschool", "someaddress", "somedescription",
                                "")
        assert (rv.status_code == 400)

        # try successful create a school
        rv = self.create_school(random_string(digits=10),
                                random_string(digits=10),
                                random_string(digits=10), "")
        assert (rv.status_code == 200)


if __name__ == '__main__':
    unittest.main()