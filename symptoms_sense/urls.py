# stutern_health_guidance.urls


from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.documentation import include_docs_urls
from django.conf import settings

from . import views


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path("", views.index_view, name="index"),
    path("api/UsersAuths/", include("accounts.urls")),
    path("api/", include("symptoms_chat.urls")),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='Health schema'),
    path('api/docs/', include_docs_urls(title='Health API')),

    # Optional UI:
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='Health schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='Health schema'), name='redoc'),
    
    re_path(r'^media/(?P<path>.*)$', serve,{'document_root':settings.MEDIA_ROOT}), 
]
