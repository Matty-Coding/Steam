from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from django.core import mail
from django.core.cache import cache
from re import search
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

# recover user model
User = get_user_model()


class RegisterTest(TestCase):

    # set up user (called before each test)
    def setUp(self):

        # set register url path
        self.register_url = reverse("register")

        # set resend activation email path
        self.resend_activation_url = reverse("resend-activation")

        self.email = "test@register.com"
        self.password = "Django.12345"

    def test_register_success(self):
        """
        Testing register successfull
        """

        data = {
            "email": self.email,
            "password": self.password,
            "confirm_password": self.password
        }

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


class ThrottleEmailSendTest(TestCase):

    # set up user (called before each test)
    def setUp(self):
        cache.clear()
        self.email = "test@throttle.com"
        self.password = "Django.12345"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        # save changes
        self.user.save()

        # set resend activation email path
        self.resend_activation_url = reverse("resend-activation")

    def test_throttle_email_send(self):
        """
        Testing throttle email send
        """

        # simulate throttling
        THROTTLE_LIMIT = 5
        for i in range(THROTTLE_LIMIT + 1):
            response = self.client.post(
                self.resend_activation_url, {"email": self.email}, content_type="application/json"
            )

            # valid throttling
            if i < THROTTLE_LIMIT:
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                    f"Attempt {i + 1}"
                )

            # throttling
            else:
                self.assertEqual(
                    response.status_code,
                    status.HTTP_429_TOO_MANY_REQUESTS
                )


class InvalidationActivationLink(TestCase):
    # set up user (called before each test)
    def setUp(self):
        cache.clear()
        self.email = "test@invalidate.com"
        self.password = "Django.12345"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password
        )

        self.resend_email = reverse("resend-activation")

    def test_invalid_activation_link(self):
        """
        Testing invalid activation link
        """

        response = self.client.post(
            self.resend_email, {"email": self.email}, content_type="application/json"
        )

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert token_value is incremented
        self.assertEqual(User.objects.get(email=self.email).token_value, 2)

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
        first_activate_url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token}
        )

        resend_email = self.client.post(
            self.resend_email, {"email": self.email}, content_type="application/json"
        )

        # assert status code is 200
        self.assertEqual(resend_email.status_code, status.HTTP_200_OK)

        self.assertEqual(User.objects.get(email=self.email).token_value, 3)

        # assert activation email is sent
        self.assertEqual(len(mail.outbox), 2)

        # recover activation email
        email_sent = mail.outbox[1]

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
        second_activate_url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token}
        )

        first_get_activate = self.client.get(first_activate_url)

        # assert status code is 400
        self.assertEqual(
            first_get_activate.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        second_get_activate = self.client.get(second_activate_url)

        # assert status code is 200
        self.assertEqual(second_get_activate.status_code, status.HTTP_200_OK)

        # assert user is active after activation clicking the link
        self.assertTrue(User.objects.get(email=self.email).is_active)


class LoginTest(TestCase):

    # set up user (called before each test)
    def setUp(self):
        self.email = "test@login.com"
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

        # set resend activation email path
        self.resend_activation_url = reverse("resend-activation")

        # set refresh token url path
        self.refresh_token_url = reverse("refresh-token")

    def test_login_success(self):
        """
        Testing login successfull
        """

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

    def test_refresh_token(self):
        """
        Testing refresh token (silent refresh UX)
        """

        # login user
        self.client.post(
            self.login_url, {"email": self.email, "password": self.password}, content_type="application/json"
        )

        # get refresh token from cookies
        old_refresh_token = self.client.cookies["refreshToken"].value

        # simulate post request with refresh token
        response = self.client.post(self.refresh_token_url)

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert response contains access token in data
        self.assertIn("accessToken", response.data)

        # assert response contains refresh token in cookies
        self.assertIn("refreshToken", response.cookies)

        # recover refresh token from response cookies
        new_refresh_token = response.cookies["refreshToken"].value

        self.assertNotEqual(old_refresh_token, new_refresh_token)

        # assert refresh token is httponly
        self.assertTrue(response.cookies["refreshToken"]["httponly"])

        # assert refresh token is secure
        self.assertEqual(response.cookies["refreshToken"]["samesite"], "Lax")

    def test_login_invalid_credentials(self):
        """
        Testing login with invalid credentials
        """

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

    def test_valid_credentials_inactive_user(self):
        """
        Testing login with valid credentials and inactive user
        """

        # settings is_active to False
        setattr(self.user, "is_active", False)

        # save changes
        self.user.save()

        response = self.client.post(
            self.resend_activation_url, {"email": self.email}, content_type="application/json"
        )

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert token value is 2
        self.assertEqual(User.objects.get(email=self.email).token_value, 2)

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
        first_activate_url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token}
        )

        resend_email = self.client.post(
            self.resend_activation_url, {"email": self.email}, content_type="application/json"
        )

        # assert status code is 200
        self.assertEqual(resend_email.status_code, status.HTTP_200_OK)

        self.assertEqual(User.objects.get(email=self.email).token_value, 3)

        # assert activation email is sent
        self.assertEqual(len(mail.outbox), 2)

        # recover activation email
        email_sent = mail.outbox[1]

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
        second_activate_url = reverse(
            "activate",
            kwargs={"uidb64": uidb64, "token": token}
        )

        first_get_activate = self.client.get(first_activate_url)

        # assert status code is 400
        self.assertEqual(
            first_get_activate.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        second_get_activate = self.client.get(second_activate_url)

        # assert status code is 200
        self.assertEqual(second_get_activate.status_code, status.HTTP_200_OK)

        data = {"email": self.email, "password": self.password}

        # settings is_active to False
        setattr(self.user, "is_active", False)

        # save changes
        self.user.save()

        response = self.client.post(
            self.login_url, data, content_type="application/json"
        )

        # assert status code is 401
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # assert response does not contain access token in data
        self.assertNotIn("accessToken", response.data)

        # assert response does not contain refresh token in cookies
        self.assertNotIn("refreshToken", response.cookies)

    def test_logout(self):
        """
        Testing logout
        """

        self.client.post(
            self.login_url, {"email": self.email, "password": self.password}, content_type="application/json"
        )

        refresh_token = self.client.cookies["refreshToken"].value

        response = self.client.post(reverse("logout"))

        # assert status code is 200
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # assert response does not contain access token in data
        self.assertNotIn("accessToken", response.data)

        # assert response does not contain refresh token in cookies
        self.assertEqual(response.cookies["refreshToken"].value, "")

        # assert response does not contain csrf token in cookies
        self.assertEqual(response.cookies["csrftoken"].value, "")

        # assert refresh token is blacklisted
        is_blacklistes = BlacklistedToken.objects.filter(
            token__token=refresh_token).exists()

        self.assertTrue(is_blacklistes)
