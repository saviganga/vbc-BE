from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers

from userapp import views as user_views

router = routers.DefaultRouter()

router.register(r"account", user_views.UserViewSet, basename="account")

urlpatterns = [
    
]

urlpatterns += router.urls
