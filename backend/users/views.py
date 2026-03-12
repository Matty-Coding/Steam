from django.shortcuts import render
from .serializers import RegisterSerializer, LoginSerializer
from .models import CustomUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

# Create your views here.
