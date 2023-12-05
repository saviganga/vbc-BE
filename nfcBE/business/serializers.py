from rest_framework import serializers
from business import models as business_models
from userapp import models as user_models
from django.db.models import Q
from django.utils import timezone

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


class BusinessLeadsSerializer(serializers.ModelSerializer):

    business = serializers.CharField(required=True)
    fields = serializers.JSONField(required=True)

    class Meta:
        model = business_models.BusinessLeads
        fields = ['id', 'business', 'lead_type', 'fields', 'journey', 'assignee', "added_on", 'updated_on']

    def create(self, validated_data):

        print(validated_data)

        # get the business
        try:
            business_profile = business_models.BusinessProfile.objects.get(reference=validated_data.get('business'))
        except Exception as business_profile_error:
            return False, 'Oops! Business profile with this reference not found'

        # check that lead type is from the business
        business_leads_config = next((lead_config for lead_config in business_profile.configuration.get('business_leads') if lead_config.get('type').upper() == validated_data.get('lead_type').upper() ), None)
        if business_leads_config is None:
            return False, "Oops! 'lead_type' not found"
        
        # handle the fields
        if type(validated_data.get('fields')) != dict:
            return False, "Invalid fields format"
        
        for field_key in list(validated_data.get('fields').keys()):
            if field_key not in [k.get('key') for k in business_leads_config.get('fields')]:
                validated_data.get('fields').pop(field_key)
            else:
                continue

        if len(list(validated_data.get('fields').keys())) < 1:
            return False, "Please fill in the lead fields"

        lead_journey = [
            {
                "status": "INITIATED",
                "business_member": "",
                "time": str(timezone.now()),
                "comment": ""
            }
        ]

        validated_data['journey'] = lead_journey
        validated_data.pop('business')

        try:
            business_lead = self.Meta.model.objects.create(**validated_data, business=business_profile)
        except Exception as business_lead_error:
            print(business_lead_error)
            return False, "Unable to create business lead"
        
        return True, {
            "id": str(business_lead.id),
            "business": {
                "id": str(business_lead.business.id),
                "name": business_lead.business.name,
                "reference": business_lead.business.reference
            },
            "assignee": business_lead.assignee,
            "fields": business_lead.fields,
            "journey": business_lead.journey,
            "added_on": str(business_lead.added_on),
            "updated_on": str(business_lead.updated_on)
        }
    

class ReadBusinessLeadsSerializer(serializers.ModelSerializer):

    business = serializers.SerializerMethodField()
    assignee = serializers.SerializerMethodField()

    class Meta:
        model = business_models.BusinessLeads
        fields = ['id', 'business', 'lead_type', 'fields', 'journey', 'assignee', "added_on", 'updated_on']

    def get_business(self, obj):

        return {
            "id": str(obj.business.id),
            "name": obj.business.name,
            "reference": obj.business.reference
        }

    def get_assignee(self, obj):

        if obj.assignee:
            return {
                "id": str(obj.assignee.id),
                "user": {
                    "id": str(obj.assignee.user.id),
                    "first_name": obj.assignee.user.first_name,
                    "last_name": obj.assignee.user.last_name,
                    "email": obj.assignee.user.email
                }
            }
