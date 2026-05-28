from django.urls import path
from . import views

app_name = 'routines'

urlpatterns = [
    path('', views.routine_list, name='list'),
    path('add/', views.routine_create, name='create'),
    path('<int:pk>/edit/', views.routine_edit, name='edit'),
    path('<int:pk>/delete/', views.routine_delete, name='delete'),
    path('<int:pk>/toggle/', views.toggle_complete, name='toggle'),
    path('mood/', views.update_mood, name='update_mood'),
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.category_create, name='category_create'),
]
