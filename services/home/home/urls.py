"""
URL configuration for home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from core.views import UserViewSet, GroupViewSet, LocationViewSet
from lights.views import LightViewSet
from devices.views import DeviceViewSet, DeviceTypeViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"lights", LightViewSet)
router.register(r"devices", DeviceViewSet)
router.register(r"device_types", DeviceTypeViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest-framework")),
    path("api-token-auth/", views.obtain_auth_token),
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls")),
]
