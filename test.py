import unittest

from app import app
import os
import requests


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

    def create_district(
        self,
        email,
        name,
        password,
        confirmation,
    ):
        pass

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


if __name__ == '__main__':
    unittest.main()