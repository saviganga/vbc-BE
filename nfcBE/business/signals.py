import datetime
from django.db.models.signals import post_save, pre_save

from django.dispatch import receiver
from django.db.models import signals

from business import models as business_models



@receiver(signals.post_save, sender=business_models.BusinessProfile)
def set_user_is_business_true(sender, instance, created, **kwargs):
    if created:
        instance.user.is_business = True
        instance.user.save()


@receiver(signals.post_save, sender=business_models.BusinessMember)
def set_user_is_business_member_true(sender, instance, created, **kwargs):
    if created:
        instance.user.is_business_member = True
        instance.user.save()