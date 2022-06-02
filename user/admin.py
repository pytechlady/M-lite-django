from django.contrib import admin
from .models import User

# Register your models here.

class UserAmin(admin.ModelAdmin):
    list_display = ('id', 'business_name', 'phone_number')
    list_filter = ('fullname', 'username', 'phone_number', 'business_name', 'country', 'state', 'industry_name')
    search_fields = ('id', 'fullname', 'username', 'phone_number', 'business_name')
    
admin.site.register(User, UserAmin)