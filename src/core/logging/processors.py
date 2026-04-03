from structlog.typing import EventDict, WrappedLogger


def drop_color_message_key(
    _: WrappedLogger, __: str, event_dict: EventDict
) -> EventDict:
    event_dict.pop("color_message", None)
    return event_dict
