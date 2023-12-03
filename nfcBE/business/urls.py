from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from business import views as business_views

router = routers.DefaultRouter()

router.register(r"business", business_views.BusinessProfileViewSet, basename="business")
router.register(r"business-member", business_views.BusinessMemberViewSet, basename="business-member")

urlpatterns = [
    
]

urlpatterns += router.urls
