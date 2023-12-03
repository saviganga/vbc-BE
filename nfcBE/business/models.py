from django.db import models
from userapp import models as usser_models

from business import enums as business_enums
import uuid

# Create your models here.

class BusinessProfile(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(usser_models.CustomUser, on_delete=models.CASCADE, related_name='business_profile')
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(max_length=254, null=False, blank=False, unique=True)
    reference = models.CharField(max_length=12, null=False, blank=False, unique=True)
    configuration = models.JSONField(default=dict)
    url = models.URLField(null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_on"]

    def business_leads_configuration(self, validated_data):

        # validate the validated_data
        if validated_data.get('lead_type', None) is None:
            return False, "Oops! Lead type cannot be blank"

        if validated_data.get('lead_flow', None) is None or len(validated_data.get('lead_flow')) < 1:
            return False, "Oops! Lead flow cannot be blank"
        
        # update the model
        if self.configuration.get('business_leads', None) is None or len(self.configuration.get('business_leads')) < 1:
            self.configuration['business_leads'] = [
                {
                    "type": validated_data.get('lead_type').upper(),
                    "workflow": validated_data.get('lead_flow'),
                    "fields": business_enums.BUSINESS_LEAD_FIELDS
                }
            ]
        else:
            if validated_data.get('lead_type').upper() in [lead.get('type').upper() for lead in self.configuration.get('business_leads')]:
                return False, "Oops! You cannot have duplicate lead types"

            self.configuration.get('business_leads').insert(
                0, {
                    "type": validated_data.get('lead_type').upper(),
                    "workflow": validated_data.get('lead_flow'),
                    "fields": business_enums.BUSINESS_LEAD_FIELDS
                }
            )
            # ) = {
            #     "type": validated_data.get('lead_type').upper(),
            #     "workflow": validated_data.get('lead_flow'),
            #     "fields": business_enums.BUSINESS_LEAD_FIELDS
            # }

        self.save()

        return True, self.configuration.get('business_leads')
    
    def configure_business_lead_fields(self, validated_data, action=None):

        if validated_data.get('lead_type', None) is None:
            return False, "Oops! 'lead_type' field cannot be blank"
        if validated_data.get('lead_field', None) is None:
            return False, "Oops! 'lead_field' field cannot be blank"
        if type(validated_data.get('lead_field')) != dict:
            return False, "Oops! Invalid lead_field format"
        if self.configuration.get('business_leads', None) is None or len(self.configuration.get('business_leads')) < 1:
            return False, "Oops!, No business lead configuration has been set"
        
        business_leads = self.configuration.get('business_leads')
        
        # check that the lead exists (validates type)
        business_lead = next((lead for lead in business_leads if lead.get('type') == validated_data.get('lead_type').upper()), None)
        if business_lead is not None:

            # get the fields
            business_lead_fields = business_lead.get('fields')

            # get the field with the key
            field = next((f for f in business_lead_fields if f.get('key') == validated_data.get('lead_field').get('key')), None)
            if field is not None:

                # check if default field
                if field.get('default'):
                    return False, "Oops! You cannot edit a default field"
                
                if action == "CREATE":
                # field['default'] = False
                    business_lead_fields.remove(field)
                    validated_data.get('lead_field')['default'] = False
                    business_lead_fields.insert(0, validated_data.get('lead_field'))
                    business_leads.remove(business_lead)
                    business_lead['fields'] = business_lead_fields
                    business_leads.insert(0, business_lead)
                    self.configuration['business_leads'] = business_leads
                    self.save()
                    return True, self.configuration.get('business_leads')
                elif action == 'DELETE':
                    business_lead_fields.remove(field)
                    business_leads.remove(business_lead)
                    business_lead['fields'] = business_lead_fields
                    business_leads.insert(0, business_lead)
                    self.configuration['business_leads'] = business_leads
                    self.save()
                    return True, self.configuration.get('business_leads')
                else:
                    pass

                

            
            else: # we are trying to add a new field

                validated_data.get('lead_field')['default'] = False
                validated_data.get('lead_field')['key'] = '_'.join(validated_data.get('lead_field').get('name').lower().split(' '))
                business_lead_fields.insert(0, validated_data.get('lead_field'))
                business_leads.remove(business_lead)
                business_lead['fields'] = business_lead_fields
                business_leads.insert(0, business_lead)
                self.configuration['business_leads'] = business_leads
                self.save()
                return True, self.configuration.get('business_leads')
        else:
            return False, "Oops! Invalid business lead type"
        
    def configure_business_lead_flow(self, validated_data, action=None):

        if validated_data.get('lead_type', None) is None:
            return False, "Oops! 'lead_type' field cannot be blank"
        if validated_data.get('lead_flow', None) is None:
            return False, "Oops! 'lead_flow' field cannot be blank"
        if type(validated_data.get('lead_flow')) != dict:
            return False, "Oops! Invalid lead_flow format"
        if self.configuration.get('business_leads', None) is None or len(self.configuration.get('business_leads')) < 1:
            return False, "Oops!, No business lead configuration has been set"
        
        business_leads = self.configuration.get('business_leads')
        
        # check that the lead exists (validates type)
        business_lead = next((lead for lead in business_leads if lead.get('type') == validated_data.get('lead_type').upper()), None)
        if business_lead is not None:

            # get the fields
            business_lead_workflow = business_lead.get('workflow')

            # get the field with the key
            field = next((f for f in business_lead_workflow if f.get('status').upper() == validated_data.get('lead_flow').get('status').upper()), None)
            if field is not None:

                # # check if default field
                # if field.get('default'):
                #     return False, "Oops! You cannot edit a default field"
                
                if action == "CREATE":
                # field['default'] = False
                    business_lead_workflow.remove(field)
                    # validated_data.get('lead_field')['default'] = False
                    business_lead_workflow.insert(0, validated_data.get('lead_flow'))
                    business_leads.remove(business_lead)
                    business_lead['workflow'] = business_lead_workflow
                    business_leads.insert(0, business_lead)
                    self.configuration['business_leads'] = business_leads
                    self.save()
                    return True, self.configuration.get('business_leads')
                elif action == 'DELETE':
                    business_lead_workflow.remove(field)
                    business_leads.remove(business_lead)
                    business_lead['workflow'] = business_lead_workflow
                    business_leads.insert(0, business_lead)
                    self.configuration['business_leads'] = business_leads
                    self.save()
                    return True, self.configuration.get('business_leads')
                else:
                    pass

                

            
            else: # we are trying to add a new field

                # validated_data.get('lead_field')['default'] = False
                # validated_data.get('lead_field')['key'] = '_'.join(validated_data.get('lead_field').get('name').lower().split(' '))
                business_lead_workflow.insert(0, validated_data.get('lead_flow'))
                business_leads.remove(business_lead)
                business_lead['workflow'] = business_lead_workflow
                business_leads.insert(0, business_lead)
                self.configuration['business_leads'] = business_leads
                self.save()
                return True, self.configuration.get('business_leads')
        else:
            return False, "Oops! Invalid business lead type"


            





                




        

        


class BusinessMember(models.Model):
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(usser_models.CustomUser, on_delete=models.CASCADE, related_name='business_member_profile')
    business = models.ForeignKey(BusinessProfile, on_delete=models.CASCADE, related_name='members')
    is_owner = models.BooleanField(default=False)
    updated_on = models.DateTimeField(auto_now=True)
    added_on = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ["-added_on"]
