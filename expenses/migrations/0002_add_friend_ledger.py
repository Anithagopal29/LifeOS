# Generated migration - copy content to expenses/migrations/

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('expenses', '0001_initial'),  # Update this to match your last migration
    ]

    operations = [
        # Add new fields to Transaction
        migrations.AddField(
            model_name='transaction',
            name='custom_category',
            field=models.CharField(blank=True, help_text='Custom category name when "Others" is selected', max_length=100),
        ),
        migrations.AddField(
            model_name='transaction',
            name='friend_name',
            field=models.CharField(blank=True, help_text='Friend name (for lending/savings)', max_length=100),
        ),
        
        # Update transaction_type field choices
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(
                choices=[
                    ('expense', 'Expense'),
                    ('income', 'Income'),
                    ('lent_to_friend', 'Lent to Friend'),
                    ('friend_savings_deposit', 'Friend Savings Deposit'),
                    ('friend_savings_withdraw', 'Friend Savings Withdraw'),
                ],
                default='expense',
                max_length=30
            ),
        ),
        
        # Create FriendLedger model
        migrations.CreateModel(
            name='FriendLedger',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend_name', models.CharField(max_length=100)),
                ('total_lent', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_returned', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pending'),
                        ('partial', 'Partially Returned'),
                        ('returned', 'Fully Returned'),
                    ],
                    default='pending',
                    max_length=20
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_ledgers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        
        # Create FriendSavings model
        migrations.CreateModel(
            name='FriendSavings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('friend_name', models.CharField(max_length=100)),
                ('current_balance', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_deposited', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_withdrawn', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='friend_savings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        
        # Add unique constraints
        migrations.AddConstraint(
            model_name='friendledger',
            constraint=models.UniqueConstraint(fields=['user', 'friend_name'], name='unique_friend_ledger'),
        ),
        migrations.AddConstraint(
            model_name='friendsavings',
            constraint=models.UniqueConstraint(fields=['user', 'friend_name'], name='unique_friend_savings'),
        ),
    ]