from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),

    # API endpoints used by SPA JavaScript
    path('api/needs/', views.api_needs, name='api_needs'),
    path('api/needs/<int:need_id>/', views.api_need_detail, name='api_need_detail'),
    path('api/needs/<int:need_id>/donate/', views.api_donate, name='api_donate'),
    path('api/needs/create/', views.api_create_need, name='api_create_need'),
]
