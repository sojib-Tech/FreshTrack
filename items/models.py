from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class Item(models.Model):
    """Model for tracking food items and their expiry dates"""
    CATEGORY_CHOICES = [
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('dairy', 'Dairy'),
        ('meat', 'Meat'),
        ('grains', 'Grains'),
        ('others', 'Others'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='others')
    expiry_date = models.DateField()
    quantity = models.IntegerField(default=1)
    notes = models.TextField(blank=True, null=True)
    alert_enabled = models.BooleanField(default=True)
    alert_days_before = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['expiry_date']

    def __str__(self):
        return f"{self.item_name} - {self.user.username}"

    def days_left(self):
        """Calculate days until expiry"""
        today = datetime.now().date()
        delta = self.expiry_date - today
        return delta.days

    def get_status(self):
        """Return status: expired, soon, or safe"""
        days = self.days_left()
        if days < 0:
            return 'expired'
        elif days <= 3:
            return 'soon'
        else:
            return 'safe'

    def get_status_color(self):
        """Return CSS class for color coding"""
        status = self.get_status()
        if status == 'expired':
            return 'status-expired'
        elif status == 'soon':
            return 'status-soon'
        else:
            return 'status-safe'

    def should_alert(self):
        """Check if alert should be shown - only for items not yet expired"""
        if not self.alert_enabled:
            return False
        days = self.days_left()
        return 0 <= days <= self.alert_days_before

    def get_alert_message(self):
        """Get alert message"""
        days = self.days_left()
        if days < 0:
            return f"{self.item_name} is EXPIRED {abs(days)} day(s) ago!"
        elif days == 0:
            return f"{self.item_name} expires TODAY!"
        else:
            return f"{self.item_name} expires in {days} day(s)!"

    def get_countdown(self):
        """Get detailed countdown showing hours and days left"""
        from datetime import datetime, timedelta
        now = datetime.now()
        today = now.date()
        
        # Calculate time difference
        if self.expiry_date == today:
            return "Expires today"
        elif self.expiry_date < today:
            days_expired = abs((self.expiry_date - today).days)
            return f"Expired {days_expired}d ago"
        else:
            days_left = (self.expiry_date - today).days
            hours_left = 24 - now.hour if now.hour > 0 else 24
            
            if days_left == 0:
                return f"Today - {hours_left}h left"
            elif days_left == 1:
                return f"1d {hours_left}h left"
            else:
                return f"{days_left}d left"
