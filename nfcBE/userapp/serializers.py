from dataclasses import field
from pyexpat import model
from rest_framework import serializers
# from truq import business

from userapp import models as user_models
from userapp.responses import u_responses

from django.db.models import Q
from django.utils.translation import gettext_lazy as _




class RegisterCustomUserSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(
        label=_("Repeat Password"),
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )


    class Meta:
        model = user_models.CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "user_name",
            "password",
            "re_password"
        ]
        read_only_fields = ("is_active", "is_staff")

        extra_kwargs = {

            "password": {
                "write_only": True
            },
            "error_messages": {
                "required": "The password field is required"
            },

            "last_name": {
                "error_messages": {
                    "required": "The last name field is required"
                }
            },

            "first_name": {
                "error_messages": {
                    "required": "The first name field is required"
                }
            },

            "email": {
                "error_messages": {
                    "required": "The email field is required"
                }
            },

            "user_name": {
                "error_messages": {
                    "required": "The username field is required"
                }
            }

        }

    def create(self, validated_data):

        # validate password from validated data
        password = validated_data.pop("password")
        re_password = validated_data.pop("re_password")

        if password != re_password:
            msg = u_responses.password_mismatch_error()
            raise serializers.ValidationError(msg, code="Password Mismatch")
        
        # create the user
        user = user_models.CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

class ReadCustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = user_models.CustomUser
        # fields = "__all__"
        read_only_fields = ("is_active", "is_staff")
        exclude = ('password',)



class RegisterUserResponseSerializer(serializers.Serializer):
    access = serializers.CharField()

    