from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls'), name='api'),
    path('schema/', get_schema_view(
        title='Polling API',
        description=u'API для проведения опросов пользователей',
    ), name='openapi-schema'),
    path('redoc/', TemplateView.as_view(
            template_name='redoc.html',
            extra_context={'schema_url': 'openapi-schema'}
        ), name='redoc'),
]
