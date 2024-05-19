from bot.sc_services.setup_service import SetupService


def test_generate_order_distribution():
    generator = SetupService({}, {}, {}, {})

    # Test with a standard range and amount
    result = generator.generate_order_distribution(1.0, 5.0, 5)
    expected = ["1.0000", "2.0000", "3.0000", "4.0000", "5.0000"]
    assert result == expected, f"Expected {expected} but got {result}"

    # Test with zero range
    result = generator.generate_order_distribution(2.0, 2.0, 1)
    expected = ["2.0000"]
    assert result == expected, f"Expected {expected} but got {result}"

    # Test with a negative range
    result = generator.generate_order_distribution(-1.0, -5.0, 5)
    expected = ["-1.0000", "-2.0000", "-3.0000", "-4.0000", "-5.0000"]
    assert result == expected, f"Expected {expected} but got {result}"

    # Test with non-integer steps
    result = generator.generate_order_distribution(1.0, 2.0, 3)
    expected = ["1.0000", "1.5000", "2.0000"]
    assert result == expected, f"Expected {expected} but got {result}"
