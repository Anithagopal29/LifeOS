from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Dashboard & Transactions
    path('', views.tracker_view, name='tracker'),
    path('transactions/', views.transaction_list, name='list'),
    path('add/', views.transaction_create, name='create'),
    path('<int:pk>/edit/', views.transaction_edit, name='edit'),
    path('<int:pk>/delete/', views.transaction_delete, name='delete'),
    
    # Categories
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.category_create, name='category_create'),
    
    # Friend Ledger (Lending)
    path('friends/lending/', views.friend_ledger_list, name='friend_ledger_list'),
    path('friends/lending/<int:pk>/', views.friend_ledger_detail, name='friend_ledger_detail'),
    path('friends/lending/<int:pk>/update/', views.friend_ledger_update_status, name='friend_ledger_update'),
    
    # Friend Savings
    path('friends/savings/', views.friend_savings_list, name='friend_savings_list'),
    path('friends/savings/<int:pk>/', views.friend_savings_detail, name='friend_savings_detail'),
    path('friends/savings/<int:pk>/update/', views.friend_savings_update, name='friend_savings_update'),
]