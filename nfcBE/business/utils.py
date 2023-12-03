from django.db.models import Q
import random
import string
from business import models as business_models


def random_token_gen():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

class BusinessProfileUtils:

    def get_business_from_reference(self, reference):

        # reference = reference.upper()

        try:
            business_profile = business_models.BusinessProfile.objects.get(reference=reference)
            return True, business_profile
        except Exception as busines_profile_error:
            return False, "Oops! Unable to find business profile"
        
    def get_business_member_businesses(self, user):

        try:
            business_member_profiles = business_models.BusinessMember.objects.filter(user=user)
        except Exception as business_member_profile_error:
            return False, "Unable to find business member profile"
        
        user_business = [business_member.business for business_member in business_member_profiles ]

        return True, user_business
    
    def check_is_business_member(self, user, business_ref):

        try:
            business_member_profile = business_models.BusinessMember.objects.get( Q(user=user) & Q(business__reference=business_ref) )
        except Exception as e:
            return False, "Unable to find business member profile"
        
        return True, business_member_profile


