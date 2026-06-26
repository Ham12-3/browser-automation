from app.schemas import ExtensionMessage


def route_message(message: ExtensionMessage) -> dict[str, object]:
    return {
        "request_id": message.request_id,
        "accepted": True,
        "action_type": message.action_type,
    }

