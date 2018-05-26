from django.test import TestCase


class HomePageTest(TestCase):
    
    def test_uses_template(self):
        """Test that the correct template is used."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')
