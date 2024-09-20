from unittest import TestCase

from models import db, User
from app import app

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

img = "https://pngimg.com/uploads/simpsons/simpsons_PNG20.png"


class UserViewsTestCase(TestCase):
    """Tests view functions for User."""

    def setUp(self):

        User.query.delete()

        user = User(first_name="John", last_name="Doe", image_url=img)
        db.session.add(user)
        db.session.commit()

        self.user = user

    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()

    def test_list_users(self):
        with app.test_client() as client:
            resp = client.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('John Doe', html)

    def test_show_create_form(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Enter a first name', html)

    def test_create_user(self):
        with app.test_client() as client:
            d = {"first_name": "Jane", "last_name": "Doe", "img_url": ""}
            resp = client.post('/users/new', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Jane Doe", html)

    def test_show_user(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>User Detail</h1>', html)
            self.assertIn('John Doe', html)

    def test_show_user_detail(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit a user</h1>', html)
            self.assertIn('value="John"', html)
            self.assertIn('value="Doe"', html)

    def test_save_edit_user_detail(self):
        with app.test_client() as client:
            d = d = {"first_name": "John2", "last_name": "Doe2", "img_url": ""}
            resp = client.post(
                f"/users/{self.user.id}/edit", data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>User Detail</h1>', html)
            self.assertIn('John2 Doe2', html)

    def test_delete_user(self):
        with app.test_client() as client:
            resp = client.post(
                f"/users/{self.user.id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertNotIn('John Doe', html)
