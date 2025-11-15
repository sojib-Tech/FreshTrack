from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('items/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('items/<int:item_id>/edit/', views.edit_item, name='edit_item'),
]
