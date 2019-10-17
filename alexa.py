import json
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any, Callable, Dict

@dataclass
class Request:
    """Request provides useful methods for getting data out of Alexa requests."""
    event: dict

    TYPE_INTENT = "IntentRequest"
    TYPE_LAUNCH = "LaunchRequest"
    TYPE_SESSION_END = "SessionEndedRequest"

    INTENT_HELP = "AMAZON.HelpIntent"
    INTENT_CANCEL = "AMAZON.CancelIntent"
    INTENT_STOP = "AMAZON.StopIntent"
    INTENT_YES = "AMAZON.YesIntent"
    INTENT_NO = "AMAZON.NoIntent"

    def request_type(self) -> str:
        return self.event["request"]["type"]

    def read_session_storage(self) -> Dict[Any, Any]:
        return self.event["sessionAttributes"]


@dataclass
class IntentRequest(Request):
    """IntentRequest provides useful methods for handling intent requests."""

    def intent_name(self) -> str:
        return self.event["request"]["intent"]["name"]

    def value_of_slot(self, slot_name) -> str:
        if slot_name in self.event["request"]["intent"]["slots"]:
            return self.event["request"]["intent"]["slots"][slot_name]["value"]
        return None

    def id_value_of_slot(self, slot_name) -> str:
        if slot_name not in self.event["request"]["intent"]["slots"]:
             return None
        
        slot = self.event["request"]["intent"]["slots"][slot_name]
        if "resolutions" in slot and "resolutionsPerAuthority" in slot["resolutions"]:
            all_resolutions = slot["resolutions"]["resolutionsPerAuthority"]

            for resolution in all_resolutions:
                for value in resolution["values"]:
                    value = value["value"]
                    if "id" in value:
                        return value["id"]

        return None


@dataclass
class Card:
    """Card holds data that will be presented to the user as a card via the Alexa app."""
    title: str = ""
    body: str = ""
    image_url: str = ""


@dataclass
class Response:
    """Response provides an easy interface for creating responses to Alexa requests."""
    speech: str = ""
    card: Card = None
    session_storage: Dict[Any, Any] = field(default_factory=defaultdict)
    end_session: bool = True

    def to_dict(self) -> dict:
        output = {
            "version": "1.0",
            "sessionAttributes": self.session_storage,
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": self.speech
                },
                "shouldEndSession": self.end_session
            }
        }

        if self.card is not None:
            output["card"] = {
                "type": "Standard",
                "title": self.card.title,
                "text": self.card.body,
                "image": {
                    "smallImageUrl": self.card.image_url,
                    "largeImageUrl": self.card.image_url
                }
            }
        
        return output


@dataclass
class Router:
    """Router helps route an Alexa request to the appropriate response generator."""

    request_handlers: Dict[str, Callable[[Request], Response]]
    intent_handlers: Dict[str, Callable[[IntentRequest], Response]]

    def handle_request(self, event, context) -> dict:
        request = Request(event)
        request_type = request.request_type()
        response = Response()

        if request_type == Request.TYPE_INTENT:
            intent_request = IntentRequest(request.event)
            intent_name = intent_request.intent_name()

            if intent_name in self.intent_handlers:
                handler = self.intent_handlers[intent_name]
                response = handler(intent_request)

        elif request_type in self.request_handlers:
            handler = self.request_handlers[request_type]
            response = handler(request)

        return response.to_dict()
        
