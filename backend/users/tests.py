from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status

# recover user model
User = get_user_model()

# inherit from TestCase


class LoginTest(TestCase):

    # set up user (called before each test)
    def setUp(self):
        self.email = "text@example.com"
        self.password = "Django.12345"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        # settings is_active to True
        setattr(self.user, "is_active", True)

        # save changes
        self.user.save()

        # set login url path
        self.login_url = reverse("login")

    # testing login successfull
    def test_login_success(self):
        data = {
            "email": self.email,
            "password": self.password
        }

        # simulate post request with right credentials
        response = self.client.post(
            self.login_url, data, content_type="application/json"
        )

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert response contains access token in data
        self.assertIn("accessToken", response.data)

        # assert response contains refresh token in cookies
        self.assertIn("refreshToken", response.cookies)

        # recover refresh token from response cookies
        refresh_cookie = response.cookies["refreshToken"]

        # assert refresh token is httponly
        self.assertTrue(refresh_cookie["httponly"])

        # assert refresh token is secure
        self.assertEqual(refresh_cookie["samesite"], "Lax")

    # testing login with invalid credentials
    def test_login_invalid_credentials(self):
        data = {"email": self.email, "password": "WrongPassword.123"}
        response = self.client.post(
            self.login_url, data, content_type="application/json"
        )

        # assert status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # assert response does not contain access token in data
        self.assertNotIn("accessToken", response.data)

        # assert response does not contain refresh token in cookies
        self.assertNotIn("refreshToken", response.cookies)
