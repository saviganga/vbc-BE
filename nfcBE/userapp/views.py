from ast import Try
from crypt import methods
from http.client import responses
from lib2to3.pgen2.pgen import DFAState
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.conf import settings


from xauth import utils as xauth_utils

from userapp import serializers as user_serializers
from userapp import models as user_models
from userapp.responses import u_responses

from drf_yasg.utils import swagger_auto_schema
import copy
import time
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from rest_framework import generics


from django_filters import rest_framework as filters
import random
import string
import hashlib
import os
import requests
import json



from   datetime import  datetime as dt, date
import pytz

# from opentelemetry import trace

# tracer = trace.get_tracer(__name__)




class UserViewSet(ModelViewSet):
   
    queryset = user_models.CustomUser.objects.all()
    read_serializer_class = user_serializers.ReadCustomUserSerializer
    write_serializer_class = user_serializers.RegisterCustomUserSerializer
    serializer_class = user_serializers.RegisterCustomUserSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            # queryset just for schema generation metadata
            return self.queryset.none()
        # if self.request.user.is_authenticated and self.request.query_params:
        #     return self.queryset.all()
        if self.request.user.is_staff and 'admin' in self.request.headers:
            return self.queryset.all()
        return self.queryset.filter(email=self.request.user.email)
        # return self.queryset.all()

    def list(self, request, *args, **kwargs):
    
        try:

            queryset = self.filter_queryset(self.get_queryset())

            serializer = self.read_serializer_class(queryset, many=True)

            data = {
                "message": "Successfully fetched users",
                "status": "SUCCESS",
                "data": serializer.data,
            }
            return Response(data)
        except Exception as e:
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Unauthenticated User"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

    def retrieve(self, request, *args, **kwargs):
        print(f"user jwt:\n {request.user}: {request.headers.get('authorization')}")
        inst = self.get_object()
        print(f"\ninst: {inst}\n")

        try:
            instance = self.get_object()
            serializer = self.read_serializer_class(instance)
            data = serializer.data

            context = {
                "status": "SUCCESS",
                "message": "Successfully fetched user",
                "data": data
            }

            return Response(context, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"get user error: {e}")
            print(e)
            return Response(
                data={
                    "status": "FAILED",
                    "message": "You do not have permission to perform this action"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=["post"], name="signup")
    @swagger_auto_schema(
        request_body=user_serializers.RegisterCustomUserSerializer,
        responses={
            201: user_serializers.RegisterUserResponseSerializer(many=False)},
    )
    def signup(self, request, *args, **kwargs):
        # req = self.write_serializer_class(data=request.data)
        # with tracer.start_as_current_span("signup-user"):
        try:
            req = user_serializers.RegisterCustomUserSerializer(data=request.data)
            req.is_valid(raise_exception=True)
            user = req.save()

            ## would need to make changes here
            access_token = xauth_utils.encode_jwt(user, hours=2, )

            return_serializer = user_serializers.RegisterUserResponseSerializer(
                data={"access": access_token}
            )
            return_serializer.is_valid(raise_exception=True)
            return Response(
                data=u_responses.user_created_success(return_serializer.data),
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            print(e)
            return Response(
                data=u_responses.create_user_error(req.errors),
                status=status.HTTP_400_BAD_REQUEST,
            )



