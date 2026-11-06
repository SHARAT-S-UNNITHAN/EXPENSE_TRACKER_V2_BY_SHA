from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Expense


class ExpenseOwnershipSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='test-password-1')
        self.other_user = User.objects.create_user(username='other', password='test-password-2')
        self.expense = Expense.objects.create(
            owner=self.owner,
            amount=125.0,
            date=date(2026, 1, 10),
            description='Private expense',
            category='Food',
        )
        self.client.force_login(self.other_user)

    def test_other_user_cannot_open_expense_edit_page(self):
        response = self.client.get(reverse('expense-edit', args=[self.expense.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_expense(self):
        response = self.client.post(reverse('expense-delete', args=[self.expense.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Expense.objects.filter(pk=self.expense.pk).exists())

    def test_delete_endpoint_rejects_get(self):
        response = self.client.get(reverse('expense-delete', args=[self.expense.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Expense.objects.filter(pk=self.expense.pk).exists())
