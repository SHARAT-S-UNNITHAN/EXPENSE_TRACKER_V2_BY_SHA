from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import UserIncome


class IncomeOwnershipSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='income-owner', password='test-password-1')
        self.other_user = User.objects.create_user(username='income-other', password='test-password-2')
        self.income = UserIncome.objects.create(
            owner=self.owner,
            amount=900.0,
            date=date(2026, 1, 10),
            description='Private salary record',
            source='Salary',
        )
        self.client.force_login(self.other_user)

    def test_other_user_cannot_open_income_edit_page(self):
        response = self.client.get(reverse('income-edit', args=[self.income.pk]))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_income(self):
        response = self.client.post(reverse('income-delete', args=[self.income.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(UserIncome.objects.filter(pk=self.income.pk).exists())

    def test_export_requires_authentication(self):
        self.client.logout()
        response = self.client.get(
            reverse('export_csv'),
            {'start_date': '2026-01-01', 'end_date': '2026-01-31'},
        )
        self.assertEqual(response.status_code, 302)

    def test_csv_export_contains_only_requesting_users_records(self):
        response = self.client.get(
            reverse('export_csv'),
            {'start_date': '2026-01-01', 'end_date': '2026-01-31'},
        )
        self.assertEqual(response.status_code, 200)
        csv_text = response.content.decode('utf-8')
        self.assertNotIn('Private salary record', csv_text)
        self.assertNotIn('900.0', csv_text)
