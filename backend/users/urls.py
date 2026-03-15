from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("activate/<str:uidb64>/<str:token>/",
         views.ActivateAccountView.as_view(), name="activate"),
    path("resend-activation/", views.ResendActivationView.as_view(),
         name="resend-activation"),
    path("refresh-token/", views.CookieTokenRefreshView.as_view(),
         name="refresh-token"),
]
