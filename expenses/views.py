from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal
from calendar import monthrange

from .models import Transaction, ExpenseCategory, FriendLedger, FriendSavings
from .forms import TransactionForm, ExpenseCategoryForm, FriendLedgerForm, FriendSavingsForm


def get_month_range(date):
    start = date.replace(day=1)
    end_day = monthrange(date.year, date.month)[1]
    end = date.replace(day=end_day)
    return start, end


@login_required
def tracker_view(request):
    """Expense Tracker dashboard with separated balances."""
    today = timezone.now().date()
    month_start, month_end = get_month_range(today)

    # --- MONTHLY income / expense (for the net-balance card) ---
    monthly_qs = Transaction.objects.filter(user=request.user, date__gte=month_start, date__lte=month_end)
    monthly_income = monthly_qs.filter(transaction_type='income').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    monthly_expense = monthly_qs.filter(transaction_type='expense').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

    # --- LIFETIME income / expense (for My Balance) ---
    all_qs = Transaction.objects.filter(user=request.user)
    total_income = all_qs.filter(transaction_type='income').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
    total_expense = all_qs.filter(transaction_type='expense').aggregate(t=Sum('amount'))['t'] or Decimal('0.00')

    # MY BALANCE = my income - my expenses (friend savings NOT counted)
    my_balance = total_income - total_expense

    # Monthly net balance = this month's personal income - expense ONLY
    net_balance = monthly_income - monthly_expense

    # --- FRIEND SAVINGS (money physically in my account, NOT my income) ---
    friend_savings_list = FriendSavings.objects.filter(user=request.user)
    friend_savings_balance = friend_savings_list.aggregate(t=Sum('current_balance'))['t'] or Decimal('0.00')
    active_savings_count = friend_savings_list.filter(current_balance__gt=0).count()

    # PERSONAL BALANCE = (my income + friend savings balance) - my expenses
    personal_balance = my_balance + friend_savings_balance

    # --- FRIEND LENDING (money I gave to friends) ---
    friend_ledgers = FriendLedger.objects.filter(user=request.user)
    total_lent_to_friends = friend_ledgers.aggregate(t=Sum('total_lent'))['t'] or Decimal('0.00')
    total_returned_by_friends = friend_ledgers.aggregate(t=Sum('total_returned'))['t'] or Decimal('0.00')
    outstanding_to_me = total_lent_to_friends - total_returned_by_friends

    # --- CATEGORY SPENDING SUMMARY ---
    profile = request.user
    monthly_budget_total = profile.monthly_budget or Decimal('1.00')
    budget_used_percent = int(min((monthly_expense / monthly_budget_total) * 100, 999)) if monthly_budget_total else 0

    category_summary = []
    for cat in ExpenseCategory.objects.all():
        cat_qs = monthly_qs.filter(transaction_type='expense', category=cat)
        spent = cat_qs.aggregate(t=Sum('amount'))['t'] or Decimal('0.00')
        if spent <= 0 and cat.monthly_budget <= 0:
            continue
        count = cat_qs.count()
        budget = cat.monthly_budget or Decimal('1.00')
        percent = int(min((spent / budget) * 100, 100)) if budget else 0
        category_summary.append({
            'category': cat, 'spent': spent, 'count': count,
            'budget': cat.monthly_budget, 'percent': percent,
        })
    category_summary.sort(key=lambda x: x['spent'], reverse=True)

    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date', '-time', '-created_at')[:10]

    context = {
        # Separated balances
        'personal_balance': personal_balance,
        'my_balance': my_balance,
        'friend_savings_balance': friend_savings_balance,
        'total_spending': total_expense,

        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'net_balance': net_balance,
        'monthly_budget': monthly_budget_total,
        'budget_used_percent': budget_used_percent,
        'category_summary': category_summary,

        # Friend lending
        'total_lent_to_friends': total_lent_to_friends,
        'outstanding_to_me': outstanding_to_me,
        'friend_ledgers_count': friend_ledgers.count(),

        # Friend savings
        'total_friend_savings': friend_savings_balance,
        'active_savings_count': active_savings_count,
        'friend_savings_list': friend_savings_list,

        'recent_transactions': recent_transactions,
        'current_month': today.strftime('%B %Y'),
    }
    return render(request, 'expenses/tracker.html', context)


@login_required
def transaction_list(request):
    qs = Transaction.objects.filter(user=request.user)
    type_filter = request.GET.get('type')
    if type_filter in ('income', 'expense', 'lent_to_friend', 'friend_savings_deposit', 'friend_savings_withdraw'):
        qs = qs.filter(transaction_type=type_filter)
    return render(request, 'expenses/transaction_list.html', {'transactions': qs, 'type_filter': type_filter})


@login_required
def transaction_create(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            tx = form.save(commit=False)
            tx.user = request.user

            if tx.transaction_type == 'lent_to_friend':
                ledger, _ = FriendLedger.objects.get_or_create(user=request.user, friend_name=tx.friend_name)
                ledger.total_lent += tx.amount
                ledger.status = 'pending' if ledger.outstanding_amount > 0 else 'returned'
                ledger.save()

            elif tx.transaction_type == 'friend_savings_deposit':
                savings, _ = FriendSavings.objects.get_or_create(user=request.user, friend_name=tx.friend_name)
                savings.total_deposited += tx.amount
                savings.current_balance += tx.amount
                savings.save()

            elif tx.transaction_type == 'friend_savings_withdraw':
                savings = get_object_or_404(FriendSavings, user=request.user, friend_name=tx.friend_name)
                if savings.current_balance >= tx.amount:
                    savings.total_withdrawn += tx.amount
                    savings.current_balance -= tx.amount
                    savings.save()
                else:
                    messages.error(request, f'Insufficient balance. Available: ₹{savings.current_balance}')
                    return render(request, 'expenses/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

            tx.save()
            messages.success(request, 'Transaction added.')
            return redirect('expenses:tracker')
    else:
        initial = {'date': timezone.now().date(), 'time': timezone.now().time()}
        if request.GET.get('type') in ('income', 'expense', 'lent_to_friend', 'friend_savings_deposit', 'friend_savings_withdraw'):
            initial['transaction_type'] = request.GET.get('type')
        if request.GET.get('friend'):
            initial['friend_name'] = request.GET.get('friend')
        form = TransactionForm(initial=initial)
    return render(request, 'expenses/transaction_form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def transaction_edit(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=tx)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated.')
            return redirect('expenses:tracker')
    else:
        form = TransactionForm(instance=tx)
    return render(request, 'expenses/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})


@login_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        if tx.transaction_type == 'lent_to_friend':
            ledger = FriendLedger.objects.filter(user=request.user, friend_name=tx.friend_name).first()
            if ledger:
                ledger.total_lent -= tx.amount
                if ledger.total_lent <= 0:
                    ledger.delete()
                else:
                    ledger.save()
        elif tx.transaction_type == 'friend_savings_deposit':
            savings = FriendSavings.objects.filter(user=request.user, friend_name=tx.friend_name).first()
            if savings:
                savings.total_deposited -= tx.amount
                savings.current_balance -= tx.amount
                if savings.current_balance <= 0 and savings.total_deposited <= 0:
                    savings.delete()
                else:
                    savings.save()
        elif tx.transaction_type == 'friend_savings_withdraw':
            savings = FriendSavings.objects.filter(user=request.user, friend_name=tx.friend_name).first()
            if savings:
                savings.total_withdrawn -= tx.amount
                savings.current_balance += tx.amount
                savings.save()
        tx.delete()
        messages.success(request, 'Transaction deleted.')
        return redirect('expenses:tracker')
    return render(request, 'expenses/transaction_confirm_delete.html', {'transaction': tx})


@login_required
def category_list(request):
    return render(request, 'expenses/category_list.html', {'categories': ExpenseCategory.objects.all()})


@login_required
def category_create(request):
    if request.method == 'POST':
        form = ExpenseCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added.')
            return redirect('expenses:categories')
    else:
        form = ExpenseCategoryForm()
    return render(request, 'expenses/category_form.html', {'form': form})


# --- FRIEND LEDGER VIEWS ---

@login_required
def friend_ledger_list(request):
    ledgers = FriendLedger.objects.filter(user=request.user)
    return render(request, 'expenses/friend_ledger_list.html', {'ledgers': ledgers})


@login_required
def friend_ledger_detail(request, pk):
    ledger = get_object_or_404(FriendLedger, pk=pk, user=request.user)
    transactions = Transaction.objects.filter(
        user=request.user, friend_name=ledger.friend_name, transaction_type='lent_to_friend'
    ).order_by('-date')
    return render(request, 'expenses/friend_ledger_detail.html', {'ledger': ledger, 'transactions': transactions})


@login_required
def friend_ledger_update_status(request, pk):
    ledger = get_object_or_404(FriendLedger, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FriendLedgerForm(request.POST, instance=ledger)
        if form.is_valid():
            form.save()
            messages.success(request, f"{ledger.friend_name}'s status updated.")
            return redirect('expenses:friend_ledger_list')
    else:
        form = FriendLedgerForm(instance=ledger)
    return render(request, 'expenses/friend_ledger_form.html', {'form': form, 'ledger': ledger})


# --- FRIEND SAVINGS VIEWS ---

@login_required
def friend_savings_list(request):
    savings_list = FriendSavings.objects.filter(user=request.user)
    total_friend_savings = savings_list.aggregate(t=Sum('current_balance'))['t'] or Decimal('0.00')
    active_savings_count = savings_list.filter(current_balance__gt=0).count()
    return render(request, 'expenses/friend_savings_list.html', {
        'savings_list': savings_list,
        'total_friend_savings': total_friend_savings,
        'active_savings_count': active_savings_count,
    })


@login_required
def friend_savings_detail(request, pk):
    savings = get_object_or_404(FriendSavings, pk=pk, user=request.user)
    transactions = Transaction.objects.filter(
        user=request.user, friend_name=savings.friend_name,
        transaction_type__in=('friend_savings_deposit', 'friend_savings_withdraw')
    ).order_by('-date')
    return render(request, 'expenses/friend_savings_detail.html', {'savings': savings, 'transactions': transactions})


@login_required
def friend_savings_update(request, pk):
    savings = get_object_or_404(FriendSavings, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FriendSavingsForm(request.POST, instance=savings)
        if form.is_valid():
            amount = form.cleaned_data.get('transaction_amount')
            trans_type = form.cleaned_data.get('transaction_type')
            if amount and amount > 0:
                if trans_type == 'deposit':
                    Transaction.objects.create(
                        user=request.user, transaction_type='friend_savings_deposit',
                        title=f'Received from {savings.friend_name}', amount=amount,
                        friend_name=savings.friend_name,
                        date=timezone.now().date(), time=timezone.now().time())
                    savings.total_deposited += amount
                    savings.current_balance += amount
                    messages.success(request, f'Deposit recorded: ₹{amount}')
                elif trans_type == 'withdraw':
                    if savings.current_balance >= amount:
                        Transaction.objects.create(
                            user=request.user, transaction_type='friend_savings_withdraw',
                            title=f'Returned to {savings.friend_name}', amount=amount,
                            friend_name=savings.friend_name,
                            date=timezone.now().date(), time=timezone.now().time())
                        savings.total_withdrawn += amount
                        savings.current_balance -= amount
                        messages.success(request, f'Withdrawal recorded: ₹{amount}')
                    else:
                        messages.error(request, f'Insufficient balance. Available: ₹{savings.current_balance}')
                        return render(request, 'expenses/friend_savings_form.html', {'form': form, 'savings': savings})
            savings.notes = form.cleaned_data.get('notes', savings.notes)
            savings.save()
            return redirect('expenses:friend_savings_list')
    else:
        form = FriendSavingsForm(instance=savings)
    return render(request, 'expenses/friend_savings_form.html', {'form': form, 'savings': savings})