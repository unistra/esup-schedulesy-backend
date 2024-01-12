from django.test import TestCase

from schedulesy.apps.ade_api.utils import (
    generate_color_from_name,
    get_pastel_colors,
    hex_to_rgb,
    pastelize,
    rgb_to_hex,
)


class UtilsTestCase(TestCase):
    def test_generate_color_from_name(self):
        self.assertEqual(generate_color_from_name('test'), '#45a113')

    def test_hex_to_rgb(self):
        self.assertEqual(hex_to_rgb('#45a113'), (69, 161, 19))

    def test_rgb_to_hex(self):
        self.assertEqual(rgb_to_hex(69, 161, 19), '#45a113')

    def test_pastelize_rgb(self):
        self.assertEqual(pastelize('#45a113', get_pastel_colors()), (120, 130, 164))

    def test_pastelize_hex(self):
        self.assertEqual(
            pastelize('#45a113', get_pastel_colors(), 'hex'), rgb_to_hex(120, 130, 164)
        )
