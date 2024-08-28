from django.contrib import admin
from .models import Order, Cart

# class CartInline(admin.TabularInline):
#     model = Cart
#     extra = 1  # Number of extra forms to display
#
# class OrderAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'Email', 'Phone', 'Address', 'Totalprice')  # Add fields to list display
#     inlines = [CartInline]  # Add Cart items inline editing in Order admin
#     search_fields = ('user__email', 'Email', 'Phone', 'Address')  # Enable searching by user email or other fields
#
# admin.site.register(Order, OrderAdmin)
