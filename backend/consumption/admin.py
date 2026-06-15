# consumption/admin.py
from django.contrib import admin
from .models import Store, Transaction

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter  = ['category']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ['user', 'description', 'amount', 'category', 'transaction_type', 'transacted_at']
    list_filter   = ['category', 'transaction_type', 'is_fixed', 'is_settle_target']
    search_fields = ['description']