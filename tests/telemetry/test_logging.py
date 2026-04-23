import logging

import pytest

from src.telemetry.logging import clear_logger_handler, drop_color_message_key


@pytest.mark.parametrize(
    ("event_dict", "expected_dict"),
    [
        ({"color_message": "colored_message"}, {}),
        ({"test": "test"}, {"test": "test"}),
    ],
    ids=[
        "dict_without_color_message_key_when_correct_dict",
        "original_dict_when_incorrect_dict",
    ],
)
def test_drop_color_message_key_return_expected_dict(
    event_dict: dict[str, str], expected_dict: dict | None
) -> None:
    result = drop_color_message_key(None, "", event_dict)
    assert result == expected_dict


def test_clear_logger_handler_clear_handler_and_set_propagate() -> None:
    handler = logging.StreamHandler()
    test_logger = logging.getLogger("test")
    test_logger.addHandler(handler)
    clear_logger_handler(["test"])
    assert len(test_logger.handlers) == 0
    assert test_logger.propagate
