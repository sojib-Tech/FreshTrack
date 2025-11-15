from django.contrib import admin
from .models import Item

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'user', 'category', 'expiry_date', 'get_status')
    list_filter = ('category', 'created_at')
    search_fields = ('item_name', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Item Info', {
            'fields': ('user', 'item_name', 'category', 'quantity')
        }),
        ('Dates', {
            'fields': ('expiry_date', 'created_at', 'updated_at')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
