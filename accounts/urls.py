# accounts.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


from . import views

router = DefaultRouter()
router.register('', views.UserViewset, basename='auth')

urlpatterns = [    
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls)),
]

