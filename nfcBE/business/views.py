from business import utils as business_utils
from business import models as business_models
from business import serializers as business_serializers
from business import utils as business_utils

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

from django.db.models import Q


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
# Create your views here.

class BusinessProfileViewSet(ModelViewSet):

    queryset = business_models.BusinessProfile.objects.all()
    serializer_class = business_serializers.BusinessProfileSerializer

    def get_queryset(self):

        # staff/admin
        if self.request.user.is_staff and 'admin' in self.request.headers:
            return self.queryset.all()
        
        if 'business' in self.request.headers:
            # get the business
            is_business, business_profile = business_utils.BusinessProfileUtils().get_business_from_reference(reference=self.request.headers.get('business'))
            if not is_business:
                return self.queryset.none()
            
            # check if the user is a business member
            is_business_member, business_member = business_utils.BusinessProfileUtils().check_is_business_member(user=self.request.user, business_ref=self.request.headers.get('business'))
            if not is_business_member:
                return self.queryset.none()
            
            return self.queryset.filter(reference=self.request.headers.get('business'))
        else:
            return self.queryset.none()

            
        # check if the user is the business owner
        # if self.request.user.is_business:
        #     return self.queryset.filter(user=self.request.user)
        # else:
        #     if self.request.user.is_business_member:
        #         # check if the nigga is a member of the business
        #         is_business_member , business_member_businesses = business_utils.BusinessProfileUtils().get_business_member_businesses(user=self.request.user)
        #         if not is_business_member:
        #             return self.queryset.none()
        #         return business_member_businesses
        #     else:
        #         return self.queryset.none()
        

    def list(self, request, *args, **kwargs):
        
        try:

            queryset = self.filter_queryset(self.get_queryset())

            serializer = self.serializer_class(queryset, many=True)

            data = {
                "message": "Successfully fetched businesses",
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
        
    def create(self, request, *args, **kwargs):

        # fill the serializer
        if request.data.get('user', None) is None:
            request.data['user'] = request.user.id
        if len(request.data.get('name')) < 3:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Business name must be more than 3 characters"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        request.data['reference'] = f"{request.data.get('name').upper()[0:3]}-{business_utils.random_token_gen()}"

        # validate the serializer
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_created, business_profile = serializer.create(validated_data=serializer.validated_data)
        if not is_created:
             return Response(
                data={
                    "status": "FAILED",
                    "message": business_profile,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Successfully created business",
                "status": "SUCCESS",
                "data": business_profile,
            }
        return Response(data)
    
    @action(methods=["post"], detail=False)
    def business_leads_configuration(self, request, pk=None):

        # validate the serializer
        serializer = business_serializers.BusinessLeadsConfigurationSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business_profile = self.queryset.get(reference=request.headers.get('business'))
        except Exception as business_profile_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Unable to find business profile",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_created, business_lead_config = business_profile.business_leads_configuration(validated_data=serializer.validated_data)
        if not is_created:
            return Response(
                data={
                    "status": "FAILED",
                    "message": business_lead_config,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Business lead configuration successful",
                "status": "SUCCESS",
                "data": business_lead_config,
            }
        return Response(data=data, status=status.HTTP_200_OK)
        
        
    @action(methods=["post"], detail=False)
    def configure_lead_fields(self, request, pk=None):

        # validate the serializer
        serializer = business_serializers.ConfigureBusinessLeadFields(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business_profile = self.queryset.get(reference=request.headers.get('business'))
        except Exception as business_profile_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Unable to find business profile",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_configured, configured_field = business_profile.configure_business_lead_fields(validated_data=serializer.validated_data, action="CREATE")
        if not is_configured:
            return Response(
                data={
                    "status": "FAILED",
                    "message": configured_field,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Business lead configuration successful",
                "status": "SUCCESS",
                "data": configured_field,
            }
        return Response(data=data, status=status.HTTP_200_OK)
        
    @action(methods=["post"], detail=False)
    def delete_lead_fields(self, request, pk=None):

        # validate the serializer
        serializer = business_serializers.ConfigureBusinessLeadFields(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business_profile = self.queryset.get(reference=request.headers.get('business'))
        except Exception as business_profile_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Unable to find business profile",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_configured, configured_field = business_profile.configure_business_lead_fields(validated_data=serializer.validated_data, action="DELETE")
        if not is_configured:
            return Response(
                data={
                    "status": "FAILED",
                    "message": configured_field,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Business lead configuration successful",
                "status": "SUCCESS",
                "data": configured_field,
            }
        return Response(data=data, status=status.HTTP_200_OK)



    @action(methods=["post"], detail=False)
    def configure_lead_flow(self, request, pk=None):

        # validate the serializer
        serializer = business_serializers.BusinessLeadsConfigurationSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business_profile = self.queryset.get(reference=request.headers.get('business'))
        except Exception as business_profile_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Unable to find business profile",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_configured, configured_field = business_profile.configure_business_lead_flow(validated_data=serializer.validated_data, action="CREATE")
        if not is_configured:
            return Response(
                data={
                    "status": "FAILED",
                    "message": configured_field,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Business lead configuration successful",
                "status": "SUCCESS",
                "data": configured_field,
            }
        return Response(data=data, status=status.HTTP_200_OK)


    @action(methods=["post"], detail=False)
    def delete_lead_flow(self, request, pk=None):

        # validate the serializer
        serializer = business_serializers.BusinessLeadsConfigurationSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Please check your fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            business_profile = self.queryset.get(reference=request.headers.get('business'))
        except Exception as business_profile_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Oops! Unable to find business profile",
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_configured, configured_field = business_profile.configure_business_lead_flow(validated_data=serializer.validated_data, action="DELETE")
        if not is_configured:
            return Response(
                data={
                    "status": "FAILED",
                    "message": configured_field,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Business lead configuration successful",
                "status": "SUCCESS",
                "data": configured_field,
            }
        return Response(data=data, status=status.HTTP_200_OK)





class BusinessMemberViewSet(ModelViewSet):

    queryset = business_models.BusinessMember.objects.all()
    serializer_class = business_serializers.BusinessMemberSerializer

    def get_queryset(self):

        # staff/admin
        if self.request.user.is_staff and 'admin' in self.request.headers:
            return self.queryset.all()
        
        if 'business' in self.request.headers:
            business_ref = self.request.headers.get('business').upper()
            
            # check if the user is the business owner
            if self.request.user.is_business:
                return self.queryset.filter(business__reference=business_ref)
            else:
                if self.request.user.is_business_member:
                    return self.queryset.filter( Q(business__reference=business_ref) & Q(user=self.request.user))
                else:
                    return self.queryset.none()
        else:
            return self.queryset.none()
        
    def list(self, request, *args, **kwargs):
        
        try:

            queryset = self.filter_queryset(self.get_queryset())

            serializer = business_serializers.ReadBusinessMemberSerializer(queryset, many=True)

            data = {
                "message": "Successfully fetched business members",
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
        
    def create(self, request, *args, **kwargs):

        # validate the serializer
        if request.headers.get('business', None) is None:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Please pass your business reference in the header",
                },
                status=status.HTTP_400_BAD_REQUEST
            ) 
        
        request.data['business'] = request.headers.get('business')

        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as serializer_error:
            return Response(
                data={
                    "status": "FAILED",
                    "message": "Please check fields and try again",
                    "data": serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        is_created, business_member = serializer.create(validated_data=serializer.validated_data)
        if not is_created:
            return Response(
                data={
                    "status": "FAILED",
                    "message": business_member,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = {
                "message": "Successfully created business member",
                "status": "SUCCESS",
                "data": business_member,
            }
        
        return Response(data=data, status=status.HTTP_201_CREATED)
        
        



            
        



        
         
        

