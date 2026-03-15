from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .services import send_activation_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .utils import validate_activation_token
from django.middleware.csrf import get_token
from .throttles import RateThrottling


class RegisterView(APIView):
    """
    Manages user registration with activation email sending
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # post method for creating user
    def post(self, request):

        # load serializer with request data
        serializer = RegisterSerializer(data=request.data)

        # check if serializer is valid
        if serializer.is_valid():

            # save user
            user = serializer.save()

            # send activation email with unique token
            send_activation_email(user)

            # register successful
            return Response({
                "message": "Registration successful. Please check your email to activate your account."
            }, status=status.HTTP_201_CREATED)

        # register failed
        return Response({
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Manages user login and throttle

    Creating and setting refresh token with csrf token in cookies,
    return access token in response
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # assign throttling to rate limit login api 5/min
    throttle_classes = [RateThrottling]
    RateThrottling.scope = "login"

    # post method for user login
    def post(self, request):

        # load serializer with request data
        serializer = LoginSerializer(data=request.data)

        # check if serializer is valid
        if serializer.is_valid(raise_exception=True):

            # get user from validated data
            user = serializer.validated_data["user"]

            # generate refresh token JWT
            refresh = RefreshToken.for_user(user)

            # get csrf token and automatic set in cookie
            get_token(request)

            # login successful
            response = Response({
                "message": "Login successful",
                # return access token in response
                "access_token": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

            # set refresh token in cookie
            response.set_cookie(
                key="refresh_token",
                value=str(refresh),
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
            )

            return response


class ResendActivationView(APIView):
    """
    Manages resend activation email and throttle
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # assign throttling to rate limit login api 3/h
    throttle_classes = [RateThrottling]
    RateThrottling.scope = "resend_email"

    # post method for resending activation email
    def post(self, request):

        # get email from request
        email = request.data.get("email")

        try:
            # check if user exists
            user = CustomUser.objects.get(email=email)

            # check if account is active
            if not user.is_active:

                # increment token_value
                # toinvalidate existing activation token
                setattr(user, "token_value", user.token_value + 1)

                # save changes
                user.save()

                # resend activation email
                send_activation_email(user)

                # resend successful
                return Response({
                    "message": "Activation email resent"
                }, status=status.HTTP_200_OK)

            # account already activated
            return Response({
                "message": "Account already activated"
            }, status=status.HTTP_400_BAD_REQUEST)

        # user does not exist with generic message for more security
        except CustomUser.DoesNotExist:
            return Response({
                "message": "If an account exists, an email was sent"
            }, status=status.HTTP_200_OK)

        # catch any other exception
        except Exception:
            return Response({
                "message": "Something went wrong"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CookieTokenRefreshView(TokenRefreshView):
    """
    Manage silent token refresh to improve UI
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # post method for silent token refresh
    def post(self, request, *args, **kwargs):

        # get refresh token from cookies
        refresh_token = request.COOKIES.get("refresh_token")

        # check if refresh token exists
        if refresh_token:

            # copy refresh token to data
            data = request.data.copy()

            # add refresh token
            data["refresh"] = refresh_token

            # assign copy to request
            request._full_data = data

        try:
            # call parent method
            response = super().post(request, *args, **kwargs)

        # catch any exception
        except Exception:
            response = Response({
                "detail": "Invalid refresh token"
            }, status=status.HTTP_401_UNAUTHORIZED)

            # delete refresh token from cookies
            response.delete_cookie("refresh_token")
            return response

        if response.status_code == 200:
            # check if refresh token exists
            if "refresh" in response.data:

                # get new refresh token while removing it
                new_refresh_token = response.data.pop("refresh")

                # set new refresh token in cookies
                response.set_cookie(
                    key="refresh_token",
                    value=new_refresh_token,
                    httponly=True,
                    secure=False,
                    samesite="Lax",
                    path="/",
                )

            # check if status code is higher or equal to 400 (errors)
            elif response.status_code >= 400:

                # delete refresh token
                response.delete_cookie("refresh_token")

        return response


class LogoutView(APIView):
    """
    Manages user logout and delete refresh token from cookies
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # post method for logout
    def post(self, request):
        try:
            # get refresh token from cookies
            refresh_token = request.COOKIES.get("refresh_token")

            # check if refresh token exists
            if refresh_token:

                # blacklist refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()

            # logout successful
            response = Response({
                "message": "Logout successful"
            }, status=status.HTTP_200_OK)

        # catch any exception
        except Exception:
            response = Response({
                "message": "Logout successful (token already invalid)"
            }, status=status.HTTP_200_OK)

        # delete refresh token and csrf token
        response.delete_cookie("refresh_token")
        response.delete_cookie("csrftoken")

        return response


class ActivateAccountView(APIView):
    """
    Manages account activation
    """

    # specify permission to all
    permission_classes = (AllowAny,)

    # get method for account activation
    def get(self, request, uidb64, token):

        # validate activation token
        user = validate_activation_token(uidb64, token)

        # check if user exists (valid token)
        if user:

            # check if account is already activated
            if user.is_active:

                # account already activated
                return Response({
                    "message": "Account already activated"
                }, status=status.HTTP_400_BAD_REQUEST)

            # otherwise activate account
            user.is_active = True

            # save changes
            user.save()

            # activate account successful
            return Response({
                "message": "Account activated successfully"
            }, status=status.HTTP_200_OK)

        # invalid or expired link
        return Response({
            "message": "Link is invalid or has expired"
        }, status=status.HTTP_400_BAD_REQUEST)
