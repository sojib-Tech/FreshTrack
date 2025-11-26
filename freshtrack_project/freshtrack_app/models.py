from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    rating = models.FloatField(default=0)
    total_sales = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.company_name

class Product(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    manufacturing_date = models.DateTimeField()
    expiry_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def remaining_hours(self):
        now = timezone.now()
        if now >= self.expiry_datetime:
            return 0
        delta = self.expiry_datetime - now
        return max(0, int(delta.total_seconds() / 3600))

    def countdown_timer(self):
        """Returns countdown in seconds only format"""
        now = timezone.now()
        if now >= self.expiry_datetime:
            return "EXPIRED"
        delta = self.expiry_datetime - now
        total_seconds = int(delta.total_seconds())
        
        return f"{total_seconds}s"

    def alert_level(self):
        hours = self.remaining_hours()
        if hours <= 0:
            return 'expired'
        elif hours < 1:
            return 'last_chance'
        elif hours < 6:
            return 'urgent'
        elif hours < 24:
            return 'soon'
        elif hours < 48:
            return 'warning'
        return 'normal'

    def __str__(self):
        return self.name

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.product.name}"

class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('seller', 'Seller Alert'),
        ('buyer', 'Buyer Alert'),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPE_CHOICES)
    alert_level = models.CharField(max_length=20)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} - {self.alert_level}"

class UserRole(models.Model):
    ROLE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('admin', 'Admin'),
    ]
    
    APPROVAL_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    is_approved = models.CharField(max_length=20, choices=APPROVAL_STATUS, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    product_name = models.CharField(max_length=255)
    seller_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer.username} - {self.product_name}"
