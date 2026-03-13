from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .services import send_activation_email
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .utils import validate_activation_token


# Create your views here.


class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_activation_email(user)

            return Response({
                "message": "Registration successful. Please check your email to activate your account."
            }, status=status.HTTP_201_CREATED)

        return Response({
            "message": "Registration failed",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            response = Response({
                "message": "Login successful",
                "access_token": str(refresh.access_token)
            }, status=status.HTTP_200_OK)

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
    def post(self, request):
        email = request.data.get("email")
        try:
            user = CustomUser.objects.get(email=email)
            if not user.is_active:
                send_activation_email(user)
                return Response({
                    "message": "Activation email resent"
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Account already activated"
            }, status=status.HTTP_400_BAD_REQUEST)

        except CustomUser.DoesNotExist:
            return Response({
                "message": "If an account exists, an email was sent"
            }, status=status.HTTP_200_OK)

        except:
            return Response({
                "message": "Something went wrong"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CookieTokenRefreshView(TokenRefreshView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            request.data["refresh"] = refresh_token

        response = super().post(request, *args, **kwargs)

        if response.status_code == 200 and "refresh" in response.data:
            new_refresh_token = response.data.pop(
                "refresh")  # Lo togliamo dal JSON

            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=False,
                samesite="Lax",
                path="/",
            )

        return response


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.COOKIES.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            response = Response({
                "message": "Logout successful"
            }, status=status.HTTP_200_OK)

            response.delete_cookie("refresh_token")

            return response

        except Exception:
            response = Response({
                "message": "Something went wrong"
            }, status=status.HTTP_200_OK)

            response.delete_cookie("refresh_token")

            return response


class ActivateAccountView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, uid, token):
        user = validate_activation_token(uid, token)

        if user:
            if user.is_active:
                return Response({
                    "message": "Account already activated"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.is_active = True
            user.save()

            return Response({
                "message": "Account activated successfully"
            }, status=status.HTTP_200_OK)

        return Response({
            "message": "Link is invalid or has expired"
        }, status=status.HTTP_400_BAD_REQUEST)
