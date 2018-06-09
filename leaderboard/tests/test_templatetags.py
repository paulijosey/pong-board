from django.test import TestCase

from leaderboard.templatetags.leaderboard_extras import percentage


class TemplateTagsTest(TestCase):

    def test_percentage_default(self):
        """Test converts to default percentage with no decimals."""
        self.assertEqual(percentage(0.5234), '52%')

    def test_percentage_decimal_place(self):
        """Test converts to percentage with specified decimal places."""
        self.assertEqual(percentage(0.5234, 1), '52.3%')
