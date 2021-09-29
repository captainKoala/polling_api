from django.urls import include, path
from rest_framework.authtoken import views as auth_views
from rest_framework.routers import DefaultRouter

from . import views

api_router = DefaultRouter()
api_router.register('questions', views.QuestionViewSet, basename='questions')
api_router.register('pollings', views.PollingViewSet, basename='pollings')

urlpatterns = [
    path('auth-token/', auth_views.obtain_auth_token, name='auth_token'),
    path('pollings/active/',
         views.ActivePollingViewSet.as_view({'get': 'list'})),
    path('', include(api_router.urls)),
    path('answers/<int:user_id>/', views.user_stat),
    path('answers/', views.post_answers),
]
