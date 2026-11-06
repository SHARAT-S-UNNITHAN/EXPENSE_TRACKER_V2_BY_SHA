from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class LogoutSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='logout-user', password='test-password-123')

    def test_logout_rejects_get_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_works_with_post(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
