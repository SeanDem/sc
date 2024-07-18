from bot.sc_services.setup_service import SetupService
from bot.sc_types import *
import pytest


class TestOrderDistribution:
    def setup_method(self):
        self.generator = SetupService()

    def test_even_distribution(self):
        result = self.generator.generate_order_distribution(1.0, 5.0, 5)
        expected = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"

    def test_single_value(self):
        result = self.generator.generate_order_distribution(2.0, 2.0, 1)
        expected = [2.0]
        assert result == expected, f"Expected {expected} but got {result}"

    def test_negative_range(self):
        # Test with a negative range
        result = self.generator.generate_order_distribution(-1.0, -5.0, 5)
        expected = [-1.0, -2.0, -3.0, -4.0, -5.0]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"

    def test_non_integer_steps(self):
        # Test with non-integer steps
        result = self.generator.generate_order_distribution(1.0, 2.0, 3)
        expected = [1.0, 1.5, 2.0]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"

    def test_with_skew_end(self):
        # Test with skew towards the end
        skew = Skew(SkewDirection.END, 2)
        result = self.generator.generate_order_distribution(0.0, 1.0, 5, skew)
        expected = [0.0, 0.5, 0.70710678, 0.8660254, 1.0]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"

    def test_with_skew_start(self):
        # Test with skew towards the start
        skew = Skew(SkewDirection.START, 2)
        result = self.generator.generate_order_distribution(0.0, 1.0, 5, skew)
        expected = [0, 0.1339746, 0.29289322, 0.5, 1]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"

    def test_with_skew_mid(self):
        # Test with skew towards the middle
        skew = Skew(SkewDirection.MID, 2)
        result = self.generator.generate_order_distribution(0.0, 1.0, 6, skew)
        expected = [0, 0.0954915, 0.3454915, 0.6545085, 0.9045085, 1]
        assert all(
            [a == pytest.approx(b) for a, b in zip(result, expected)]
        ), f"Expected {expected} but got {result}"
