from django.contrib import admin
from .models import Transaction, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'monthly_budget')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'transaction_type', 'amount', 'category', 'date')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('title', 'source')
