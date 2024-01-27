from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from blog.forms.contact_form import ContactForm
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


class HomeViewTests(TestCase):
    def setUp(self):
        self.home_url = reverse('home')

    def test_home_view_get(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'UserTemplates/Home/Home.html')

    def test_home_view_post_newsletter_signup_valid_data(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.home_url, data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json().get('success'), True)

    def test_home_view_post_newsletter_signup_invalid_data(self):
        data = {'email': 'invalid_email'}
        response = self.client.post(self.home_url, data)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.json().get('success'), False)

    def test_home_view_authenticated_user_redirect_to_edit_profile(self):
        User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')

        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('edit_profile'))


class ContactViewTests(TestCase):
    def test_contact_view_function_exists(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_view_uses_correct_template(self):
        response = self.client.get(reverse('contact'))
        self.assertTemplateUsed(response, 'Contact/ContactPage.html')

    def test_contact_view_contains_contact_form(self):
        response = self.client.get(reverse('contact'))
        self.assertIsInstance(response.context['form'], ContactForm)

    def test_contact_view_post_valid_data(self):
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        response = self.client.post(reverse('contact'), valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
        self.assertFalse(response.json()['success'])

    def test_contact_view_post_invalid_data(self):
        invalid_data = {
            'name': '',
            'email': 'invalid_email',
            'message': ''
        }
        response = self.client.post(reverse('contact'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
        self.assertFalse(response.json()['success'])

    def test_contact_view_csrf_token(self):
        response = self.client.get(reverse('contact'))
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contact_view_max_length_exceeded(self):
        invalid_data = {
            'name': 'a' * 129,
            'email': 'john@example.com',
            'message': 'Test message'
        }
        response = self.client.post(reverse('contact'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json())
        self.assertFalse(response.json()['success'])

    def test_contact_view_additional_logic(self):
        valid_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'message': 'Test message'
        }
        response = self.client.post(reverse('contact'), valid_data)
