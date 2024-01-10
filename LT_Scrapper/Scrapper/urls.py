from django.urls import path, include
from . import views

urlpatterns = [
    # path('test/<str:influencer_id>/', views.test, name='test'),
    path('test/', views.test, name='test'),
    # path('testing/', views.testing, name='testing'),
]