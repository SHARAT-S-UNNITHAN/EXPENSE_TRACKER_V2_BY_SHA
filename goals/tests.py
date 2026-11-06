from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Goal


class GoalOwnershipSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='goal-owner', password='test-password-1')
        self.other_user = User.objects.create_user(username='goal-other', password='test-password-2')
        self.goal = Goal.objects.create(
            owner=self.owner,
            name='Private savings goal',
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
            amount_to_save=Decimal('1000.00'),
            current_saved_amount=Decimal('100.00'),
        )
        self.client.force_login(self.other_user)

    def test_other_user_cannot_add_money_to_goal(self):
        response = self.client.post(
            reverse('add_amount', args=[self.goal.pk]),
            {'additional_amount': '50.00'},
        )
        self.assertEqual(response.status_code, 404)
        self.goal.refresh_from_db()
        self.assertEqual(self.goal.current_saved_amount, Decimal('100.00'))

    def test_other_user_cannot_delete_goal(self):
        response = self.client.post(reverse('delete_goal', args=[self.goal.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Goal.objects.filter(pk=self.goal.pk).exists())
