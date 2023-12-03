from rest_framework import serializers
from business import models as business_models
from userapp import models as user_models
from django.db.models import Q

class BusinessProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = business_models.BusinessProfile
        fields = ['user', 'name', 'email', 'reference', 'url', 'configuration']

    def create(self, validated_data):

        if validated_data.get('email', None) is not None:
            try:
                existing_business_profile_email = self.Meta.model.objects.get(email=validated_data.get('email'))
                return False, "Oops! A business with this email already exists"
            except Exception as existing_business_profile_email_error:
                pass
        else:
            pass

        if validated_data.get('url', None) is not None:
            try:
                existing_business_profile_url = self.Meta.model.objects.get(url=validated_data.get('url'))
                return False, "Oops! A business with this url already exists"
            except Exception as existing_business_profile_url_error:
                pass
        else:
            pass

        try:
            business_profile = self.Meta.model.objects.create(**validated_data)
            
        except Exception as business_profile_error:
            # print(business_profile_error)
            return False, "Oops! Unable to create business profile"
        
        # use business member serializer create

        try:
            business_member = business_models.BusinessMember.objects.create(
                user=business_profile.user,
                business=business_profile,
                is_owner=True
            )
        except Exception as business_member_error:
            return False, "Oops! Unable to create business member profile"
        
        return True, {
                "id": str(business_profile.id),
                "name": business_profile.name,
                "reference": business_profile.reference,
                "user": {
                    "id": str(business_profile.user.id),
                    "first_name": business_profile.user.first_name,
                    "last_name": business_profile.user.last_name,
                    "email": business_profile.user.email
                },
                "email": business_profile.email,
                "url": business_profile.url
            }


class BusinessLeadsConfigurationSerializer(serializers.Serializer):

    lead_type = serializers.CharField(required=True)
    lead_flow = serializers.JSONField(required=True)


    # lead flow
    # [
    #   {
    #       status: "",
    #        description: ""
    #        fields: [
    #                   {
    #                       key: "",
    #                       name: ""
    #                   }
    #                ]
    #   }
    # ]

class ConfigureBusinessLeadFields(serializers.Serializer):
    lead_type = serializers.CharField(required=True)
    lead_field = serializers.JSONField(required=True)


class BusinessMemberSerializer(serializers.ModelSerializer):

    user = serializers.EmailField(required=True)
    business = serializers.CharField(required=True)

    class Meta:
        model = business_models.BusinessMember
        fields = ['id', 'user', 'business', 'is_owner']

    def create(self, validated_data):

        try:
            user = user_models.CustomUser.objects.get(email=validated_data.get('user'))
        except Exception as no_user:
            return False, "Oops! User with this email does not exist"
        
        try:
            business = business_models.BusinessProfile.objects.get(reference=validated_data.get('business'))
        except Exception as no_business:
            return False, "Oops! Business with this reference does not exist"
        
        try:
            existing_business_member = self.Meta.model.objects.get( Q(user=user) & Q(business=business) )
            return False, "Oops! Business member with this profile already exists for this business"
        except Exception:
            pass


        try:
            business_member = self.Meta.model.objects.create(
                user=user,
                business=business
            )
        except Exception as business_member_error:
            return False, "Unable to create business member"
        
        return True, {
            "id": str(business_member.id),
            "user": {
                "id": str(user.id),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            },
            "business": {
                "id": str(business.id),
                "name": business.name,
                'business': business.reference
            }
        }
        
class ReadBusinessMemberSerializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()
    business = serializers.SerializerMethodField()

    class Meta:
        model = business_models.BusinessMember
        fields = ["id", "user", "business", "is_owner", "updated_on", "added_on"]

    def get_user(self, obj):

        try:
            return {
                "id": obj.user.id,
                "first_name": obj.user.first_name,
                "last_name": obj.user.last_name,
                "email": obj.user.email,
                # "phone": obj.user.phone
            }
        except Exception as e:
            return None
        
    
    def get_business(self, obj):

        try:
            return {
                "id": obj.business.id,
                "name": obj.business.name,
                "reference": obj.business.reference
            }
        except Exception:
            return None



