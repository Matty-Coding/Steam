from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.core import mail
from re import search

# recover user model
User = get_user_model()


class RegisterTest(TestCase):

    # set up user (called before each test)
    def setUp(self):

        # set register url path
        self.register_url = reverse("register")

        # set resend activation email path
        self.resend_activation_url = reverse("resend-activation")

        self.email = "text@example.com"
        self.password = "Django.12345"

    # testing register successfull
    def test_register_success(self):
        data = {
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password
        }

        # simulate throttling
        for i in range(4):
            response = self.client.post(
                self.resend_activation_url, {}, content_type="application/json"
            )

            # valid throttling
            if i < 3:
                self.assertNotEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"attempt - {i + 1}"
                )

            # throttling
            else:
                self.assertEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    f"attempt - {i + 1}"
                )

        # simulate post request with right credentials
        response = self.client.post(
            self.register_url, data, content_type="application/json"
        )

        # assert status code is 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert user is not active after registration
        self.assertFalse(User.objects.get(email=self.email).is_active)

        # assert activation email is sent
        self.assertEqual(len(mail.outbox), 1)

        # recover activation email
        email_sent = mail.outbox[0]

        # assert activation email is sent to user
        self.assertIn(self.email, email_sent.to)

        # recover activation link
        activation_link = search(r"http://[^\s]+", email_sent.body).group(0)

        # split activation link to get uidb64 and token
        sections = activation_link.strip("/").split("/")

        # recover uidb64 and token
        uidb64 = sections[-2]
        token = sections[-1]

        # set activate url
        activate_url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token}
        )

        # simulate get request with activation link
        response = self.client.get(
            activate_url, {"uidb64": uidb64, "token": token}
        )

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert user is active after activation clicking the link
        self.assertTrue(User.objects.get(email=self.email).is_active)


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


class ThrottlingTest(TestCase):

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
