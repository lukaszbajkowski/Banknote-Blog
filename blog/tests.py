from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from blog.models import NewsletterUser
from blog.views import INVALID_EMAIL_MESSAGE, UNSUBSCRIBE_SUCCESS_MESSAGE


class NewsletterViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.signup_url = reverse('newsletter_signup')
        cls.unsubscribe_url = reverse('newsletter_unsubscribe')

    def assertTemplateAndStatus(self, response, template_name, status_code):
        self.assertEqual(response.status_code, status_code)
        self.assertTemplateUsed(response, template_name)

    def test_newsletter_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html', 200)

    def test_newsletter_signup_view_post_valid_data(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.signup_url, data)
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html', 200)

    def test_newsletter_signup_view_post_invalid_data(self):
        data = {'email': 'invalid_email'}
        response = self.client.post(self.signup_url, data)
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html', 200)

    def test_newsletter_unsubscribe_view_post_valid_email(self):
        email = 'test@example.com'
        NewsletterUser.objects.create(email=email)

        response = self.client.post(self.unsubscribe_url, {'email': email})
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html', 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), UNSUBSCRIBE_SUCCESS_MESSAGE)

    def test_newsletter_unsubscribe_view_post_invalid_email(self):
        email = 'nonexistent@example.com'

        response = self.client.post(self.unsubscribe_url, {'email': email})
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html', 200)

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), INVALID_EMAIL_MESSAGE)

    def test_newsletter_unsubscribe_view_get(self):
        response = self.client.get(self.unsubscribe_url)
        self.assertTemplateAndStatus(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html', 200)
