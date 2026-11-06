from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from django.urls import reverse


class DatasetUpdateSecurityTests(APITestCase):
    def test_anonymous_user_cannot_update_training_dataset(self):
        response = self.client.post(
            reverse('update-dataset'),
            {'new_data': {'description': 'test expense', 'category': 'Other'}},
            format='json',
        )
        self.assertIn(response.status_code, (401, 403))

    def test_regular_user_cannot_update_training_dataset(self):
        user = User.objects.create_user(username='regular-user', password='test-password')
        self.client.force_authenticate(user=user)
        response = self.client.post(
            reverse('update-dataset'),
            {'new_data': {'description': 'test expense', 'category': 'Other'}},
            format='json',
        )
        self.assertEqual(response.status_code, 403)
