from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


def rupee(value):
    """Format a Decimal/number as Indian Rupees.

    Whole numbers show without decimals (6,000); non-whole show two
    decimals (24.50). Quantizing first kills float artefacts like 5999.999.
    Returns the number WITHOUT the ₹ symbol (put ₹ in your markup).
    """
    if value is None:
        value = Decimal('0')
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    value = value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if value == value.to_integral_value():
        return f"{int(value):,}"
    return f"{value:,.2f}"


class ExpenseCategory(models.Model):
    """Expense category - Shopping, Food & Drink, Transport, Housing, Tech, Dining, etc."""
    CATEGORY_ICONS = [
        ('bag', 'Shopping bag'),
        ('utensils', 'Utensils'),
        ('car', 'Car'),
        ('home', 'Home'),
        ('cart', 'Cart'),
        ('cash', 'Cash'),
        ('coffee', 'Coffee'),
        ('star', 'Star'),
    ]
    CATEGORY_COLORS = [
        ('beige', 'Beige'),
        ('green', 'Green'),
        ('peach', 'Peach'),
        ('cream', 'Cream'),
        ('mint', 'Mint'),
        ('sage', 'Sage'),
    ]

    name = models.CharField(max_length=50, unique=True)
    icon = models.CharField(max_length=20, choices=CATEGORY_ICONS, default='bag')
    color = models.CharField(max_length=20, choices=CATEGORY_COLORS, default='beige')
    monthly_budget = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name_plural = 'Expense Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Transaction(models.Model):
    """Transaction = income OR expense OR friend lending/savings."""
    TYPE_CHOICES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('lent_to_friend', 'Lent to Friend'),
        ('friend_savings_deposit', 'Friend Savings Deposit'),
        ('friend_savings_withdraw', 'Friend Savings Withdraw'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='expense')
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)

    # Custom category for "Others"
    custom_category = models.CharField(max_length=100, blank=True, help_text='Custom category name when "Others" is selected')

    date = models.DateField(default=timezone.now)
    time = models.TimeField(null=True, blank=True, default=timezone.now)

    # Income-specific: who sent money
    source = models.CharField(max_length=100, blank=True, help_text='Person/company who sent money (for income)')

    # Friend lending/savings: friend name
    friend_name = models.CharField(max_length=100, blank=True, help_text='Friend name (for lending/savings)')

    # Reason for money given to a friend (lending)
    reason = models.CharField(max_length=200, blank=True, help_text='Reason for money given to friend')

    # Has this lent money been paid back?
    paid_back = models.BooleanField(default=False, help_text='Whether lent money was returned')

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time', '-created_at']

    def __str__(self):
        sign = '+' if self.transaction_type in ('income', 'friend_savings_deposit') else '-'
        return f"{sign}₹{self.amount} - {self.title}"

    @property
    def signed_amount(self):
        if self.transaction_type == 'income':
            return self.amount
        elif self.transaction_type == 'expense':
            return -self.amount
        elif self.transaction_type == 'lent_to_friend':
            return -self.amount
        elif self.transaction_type == 'friend_savings_deposit':
            return self.amount
        elif self.transaction_type == 'friend_savings_withdraw':
            return -self.amount
        return Decimal('0')

    @property
    def amount_display(self):
        """Plain rupee number without sign, e.g. '6,000' or '24.50'."""
        return rupee(self.amount)

    @property
    def display_amount(self):
        """Returns formatted string with sign and rupee symbol."""
        if self.transaction_type in ('income', 'friend_savings_deposit'):
            return f"+₹{rupee(self.amount)}"
        return f"-₹{rupee(self.amount)}"

    @property
    def display_category(self):
        """Returns custom category if set, otherwise the category name."""
        if self.custom_category:
            return self.custom_category
        return self.category.name if self.category else 'Uncategorized'


class FriendLedger(models.Model):
    """Track lending relationships with friends (money I gave to friends)."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('partial', 'Partially Returned'),
        ('returned', 'Fully Returned'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_ledgers')
    friend_name = models.CharField(max_length=100)
    total_lent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_returned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'friend_name')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.friend_name} - ₹{self.outstanding_amount}"

    @property
    def outstanding_amount(self):
        """Amount still owed by friend."""
        return self.total_lent - self.total_returned

    @property
    def is_settled(self):
        return self.outstanding_amount <= 0


class FriendSavings(models.Model):
    """Track savings held on behalf of friends (money physically in my account)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friend_savings')
    friend_name = models.CharField(max_length=100)
    current_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deposited = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_withdrawn = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'friend_name')
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.friend_name} - ₹{self.current_balance}"

    @property
    def has_balance(self):
        return self.current_balance > 0