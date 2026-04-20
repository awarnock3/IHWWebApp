"""
URL configuration for search app
"""
from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('results/', views.SearchResultsView.as_view(), name='results'),
    path('observation/<int:pk>/', views.ObservationDetailView.as_view(), name='observation-detail'),
]
