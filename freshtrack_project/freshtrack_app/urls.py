from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('buyer/', views.buyer_dashboard, name='buyer_dashboard'),
    path('buyer/history/', views.buyer_history, name='buyer_history'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/buy/', views.buy_product, name='buy_product'),
    
    path('seller/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add-product/', views.add_product, name='add_product'),
    path('seller/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('seller/alerts/', views.seller_alerts, name='seller_alerts'),
    path('alert/<int:alert_id>/read/', views.mark_alert_read, name='mark_alert_read'),
    
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/approve/<int:product_id>/', views.approve_product, name='approve_product'),
    path('admin/reject/<int:product_id>/', views.reject_product, name='reject_product'),
    path('admin/approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('admin/reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
]
