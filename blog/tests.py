from django.contrib.messages import get_messages
from django.test import TestCase, Client
from django.urls import reverse

from blog.models import NewsletterUser
from blog.views import INVALID_EMAIL_MESSAGE, UNSUBSCRIBE_SUCCESS_MESSAGE


class StaticPageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.terms_conditions_url = reverse('terms_and_conditions')
        self.privacy_policy_url = reverse('privacy_policy')
        self.about_page_url = reverse('about_page')

    def test_terms_conditions_view(self):
        response = self.client.get(self.terms_conditions_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/TermsConditions/TermsConditions.html')

    def test_privacy_policy_view(self):
        response = self.client.get(self.privacy_policy_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/PrivacyPolicy/PrivacyPolicy.html')

    def test_about_page_view(self):
        response = self.client.get(self.about_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/About/About.html')


class NewsletterViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = Client()
        cls.signup_url = reverse('newsletter_signup')
        cls.unsubscribe_url = reverse('newsletter_unsubscribe')

    def test_newsletter_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html')

    def test_newsletter_signup_view_post_valid_data(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html')

    def test_newsletter_signup_view_post_invalid_data(self):
        data = {'email': 'invalid_email'}
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterRegister/NewsletterSingUp.html')

    def test_newsletter_unsubscribe_view_post_valid_email(self):
        email = 'test@example.com'
        NewsletterUser.objects.create(email=email)

        response = self.client.post(self.unsubscribe_url, {'email': email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), UNSUBSCRIBE_SUCCESS_MESSAGE)

    def test_newsletter_unsubscribe_view_post_invalid_email(self):
        email = 'nonexistent@example.com'

        response = self.client.post(self.unsubscribe_url, {'email': email})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), INVALID_EMAIL_MESSAGE)

    def test_newsletter_unsubscribe_view_get(self):
        response = self.client.get(self.unsubscribe_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/NewsletterDelete/NewsletterDelete.html')
