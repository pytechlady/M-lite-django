from xml.etree.ElementInclude import include
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

app_name = 'user'

router = DefaultRouter()

router.register('users', UserViewSet)
router.register('', LoginViewSet)


urlpatterns = [
    path('', include(router.urls)),
]