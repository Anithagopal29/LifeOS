from django import forms
from .models import Transaction, ExpenseCategory, FriendLedger, FriendSavings


class TransactionForm(forms.ModelForm):
    """
    Single category dropdown that includes an "Others" option.
    When "Others" is chosen, one inline text input (other_category_name)
    appears for a custom name. No separate hidden custom_category widget.
    """
    OTHERS = '__others__'

    category_choice = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-control-lifeos',
            'id': 'id_category_choice',
        })
    )
    other_category_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lifeos',
            'id': 'id_other_category_name',
            'placeholder': 'Enter category name',
        })
    )

    class Meta:
        model = Transaction
        fields = ['transaction_type', 'title', 'amount', 'date', 'time',
                  'source', 'friend_name', 'reason', 'notes']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-select form-control-lifeos', 'id': 'id_transaction_type'}),
            'title': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'e.g. Salary from TechCorp'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '1', 'placeholder': '0'}),
            'date': forms.DateInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control form-control-lifeos', 'type': 'time'}),
            'source': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'Who sent the money (income only)'}),
            'friend_name': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'Friend name'}),
            'reason': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': 'Reason (e.g. bought food)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-lifeos', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Build dropdown from existing categories + an "Others" entry
        choices = [('', '— Select category —')]
        for cat in ExpenseCategory.objects.all():
            choices.append((str(cat.pk), cat.name))
        choices.append((self.OTHERS, 'Others'))
        self.fields['category_choice'].choices = choices

        # Pre-select existing value when editing
        inst = self.instance
        if inst and inst.pk:
            if inst.category_id:
                self.fields['category_choice'].initial = str(inst.category_id)
            elif inst.custom_category:
                self.fields['category_choice'].initial = self.OTHERS
                self.fields['other_category_name'].initial = inst.custom_category

    def clean(self):
        cleaned = super().clean()
        ttype = cleaned.get('transaction_type')
        choice = cleaned.get('category_choice')
        other_name = (cleaned.get('other_category_name') or '').strip()

        self._resolved_category = None
        self._resolved_custom = ''

        if ttype == 'expense':
            if not choice:
                raise forms.ValidationError('Please select a category.')
            if choice == self.OTHERS:
                if not other_name:
                    raise forms.ValidationError('Please enter a category name for "Others".')
                self._resolved_custom = other_name
            else:
                try:
                    self._resolved_category = ExpenseCategory.objects.get(pk=int(choice))
                except (ExpenseCategory.DoesNotExist, ValueError):
                    raise forms.ValidationError('Invalid category selected.')

        if ttype in ('lent_to_friend', 'friend_savings_deposit', 'friend_savings_withdraw'):
            if not cleaned.get('friend_name'):
                raise forms.ValidationError('Please enter a friend name.')

        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.category = getattr(self, '_resolved_category', None)
        obj.custom_category = getattr(self, '_resolved_custom', '')
        if commit:
            obj.save()
        return obj


class ExpenseCategoryForm(forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ['name', 'icon', 'color', 'monthly_budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'icon': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'color': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
            'monthly_budget': forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'step': '1'}),
        }


class FriendLedgerForm(forms.ModelForm):
    class Meta:
        model = FriendLedger
        fields = ['friend_name', 'status']
        widgets = {
            'friend_name': forms.TextInput(attrs={'class': 'form-control form-control-lifeos', 'readonly': True}),
            'status': forms.Select(attrs={'class': 'form-select form-control-lifeos'}),
        }


class FriendSavingsForm(forms.ModelForm):
    transaction_amount = forms.DecimalField(
        max_digits=10, decimal_places=2, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control form-control-lifeos', 'placeholder': '0', 'step': '1'})
    )
    transaction_type = forms.ChoiceField(
        choices=[('deposit', 'Deposit (Friend gives you money)'),
                 ('withdraw', 'Withdraw (You return money to friend)')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = FriendSavings
        fields = ['friend_name', 'notes']
        widgets = {
            'friend_name': forms.TextInput(attrs={'class': 'form-control form-control-lifeos'}),
            'notes': forms.Textarea(attrs={'class': 'form-control form-control-lifeos', 'rows': 2}),
        }