from django.urls import path
from . import views

urlpatterns = [
    path('', views.health_check, name='health-check'),
    path('detailed/', views.detailed_health, name='detailed-health'),
]
