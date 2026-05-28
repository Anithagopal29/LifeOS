"""
Seed LifeOS with default categories and an optional demo user.

Usage:
    python manage.py seed_data                # categories only (safe, idempotent)
    python manage.py seed_data --demo         # also create demo user 'alex' with sample logs
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta, time
from decimal import Decimal

from accounts.models import User
from routines.models import Category, RoutineTask, MoodLog
from expenses.models import ExpenseCategory, Transaction
from health.models import BodyMeasurement, WaterLog, Meal, SleepLog


ROUTINE_CATEGORIES = [
    ('Personal', 'beige'),
    ('Work', 'green'),
    ('Study', 'brown'),
    ('Coding', 'sage'),
    ('Reading', 'brown'),
    ('Household', 'cream'),
    ('Health', 'green'),
]

EXPENSE_CATEGORIES = [
    ('Shopping', 'bag', 'beige', 1000),
    ('Food & Drink', 'utensils', 'green', 1000),
    ('Transport', 'car', 'peach', 750),
    ('Housing', 'home', 'peach', 1500),
    ('Tech', 'star', 'cream', 500),
    ('Dining', 'coffee', 'mint', 400),
]


class Command(BaseCommand):
    help = 'Seed default categories and (optionally) a demo user with sample data.'

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true', help='Create demo user + sample logs')

    def handle(self, *args, **opts):
        self.stdout.write('Seeding routine categories...')
        for name, color in ROUTINE_CATEGORIES:
            Category.objects.get_or_create(name=name, defaults={'color': color})

        self.stdout.write('Seeding expense categories...')
        for name, icon, color, budget in EXPENSE_CATEGORIES:
            ExpenseCategory.objects.get_or_create(
                name=name,
                defaults={'icon': icon, 'color': color, 'monthly_budget': Decimal(budget)},
            )

        if opts['demo']:
            self._seed_demo()

        self.stdout.write(self.style.SUCCESS('Done. Categories ready.'))

    def _seed_demo(self):
        self.stdout.write('Creating demo user "alex" (password: lifeos123)...')
        user, created = User.objects.get_or_create(
            username='alex',
            defaults={'full_name': 'Alex Rivera', 'email': 'alex@example.com'},
        )
        if created:
            user.set_password('lifeos123')
            user.bio = 'Living intentionally, one day at a time.'
            user.monthly_budget = Decimal('2500')
            user.save()

        today = timezone.now().date()
        work = Category.objects.filter(name='Work').first()
        study = Category.objects.filter(name='Study').first()
        personal = Category.objects.filter(name='Personal').first()
        health_cat = Category.objects.filter(name='Health').first()

        # Routine timeline for today
        routine_seed = [
            ('Wake up & Hydrate', personal, time(7, 0), time(7, 30), 'low', True, ''),
            ('Breakfast', health_cat, time(8, 0), time(8, 30), 'low', True, ''),
            ('Deep Work: Office', work, time(9, 0), time(17, 0), 'high', False, 'Finish project proposal'),
            ('Python Practice', study, time(19, 0), time(20, 0), 'medium', False, ''),
            ('Evening Reset', personal, time(20, 0), time(20, 30), 'low', False, ''),
            ("Reading 'The Creative Act'", None, time(21, 0), time(22, 0), 'low', False, ''),
            ('Sleep', personal, time(23, 0), None, 'low', False, ''),
        ]
        if not RoutineTask.objects.filter(user=user, date=today).exists():
            for title, cat, st, et, prio, done, notes in routine_seed:
                RoutineTask.objects.create(
                    user=user, title=title, category=cat, date=today,
                    start_time=st, end_time=et, priority=prio,
                    is_completed=done, notes=notes,
                )

        MoodLog.objects.get_or_create(user=user, date=today,
                                      defaults={'mood': 'happy', 'energy': 'mid'})

        # Expenses
        food = ExpenseCategory.objects.filter(name='Food & Drink').first()
        housing = ExpenseCategory.objects.filter(name='Housing').first()
        tech = ExpenseCategory.objects.filter(name='Tech').first()
        if not Transaction.objects.filter(user=user).exists():
            Transaction.objects.create(user=user, transaction_type='income',
                                       title='Salary from TechCorp', amount=Decimal('3500'),
                                       source='TechCorp', date=today)
            Transaction.objects.create(user=user, transaction_type='expense',
                                       title='Payment to Starbucks', amount=Decimal('24.50'),
                                       category=food, date=today)
            Transaction.objects.create(user=user, transaction_type='expense',
                                       title='Monthly Rent', amount=Decimal('1200'),
                                       category=housing, date=today - timedelta(days=1))
            Transaction.objects.create(user=user, transaction_type='expense',
                                       title='Apple Store', amount=Decimal('129'),
                                       category=tech, date=today - timedelta(days=3))

        # Health logs
        if not BodyMeasurement.objects.filter(user=user).exists():
            BodyMeasurement.objects.create(user=user, date=today,
                                           weight_kg=Decimal('62.5'), waist_cm=Decimal('68'))
            BodyMeasurement.objects.create(user=user, date=today - timedelta(days=7),
                                           weight_kg=Decimal('62.9'), waist_cm=Decimal('68'))
        SleepLog.objects.get_or_create(user=user, date=today,
                                       defaults={'hours': Decimal('7.33'), 'consistency': 'high'})
        WaterLog.objects.get_or_create(user=user, date=today, amount_liters=Decimal('1.8'))
        for mt in ['breakfast', 'lunch', 'dinner']:
            Meal.objects.get_or_create(user=user, date=today, meal_type=mt,
                                       defaults={'description': mt.title()})

        self.stdout.write(self.style.SUCCESS('Demo data seeded. Login: alex / lifeos123'))
