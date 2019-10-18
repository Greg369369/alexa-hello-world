# pyLambdaAlexa
# A small library for handling Amazon Alexa requests with Python.
# Copyright (C) 2019 Ben Godfrey
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from dataclasses import dataclass, field
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple
import logging

@dataclass
class Request:
    """Request provides useful methods for getting data out of Alexa requests."""
    event: dict

    TYPE_INTENT = "IntentRequest"
    TYPE_LAUNCH = "LaunchRequest"
    TYPE_SESSION_END = "SessionEndedRequest"

    INTENT_FALLBACK = "AMAZON.FallbackIntent"
    INTENT_HELP = "AMAZON.HelpIntent"
    INTENT_CANCEL = "AMAZON.CancelIntent"
    INTENT_STOP = "AMAZON.StopIntent"
    INTENT_YES = "AMAZON.YesIntent"
    INTENT_NO = "AMAZON.NoIntent"

    def request_type(self) -> str:
        return self.event["request"]["type"]

    def read_session_storage(self) -> Dict[Any, Any]:
        if "sessionAttributes" in self.event:
            return self.event["sessionAttributes"]
        return {}

    def request_id(self) -> str:
        return self.event["request"]["requestId"]


@dataclass
class IntentRequest(Request):
    """IntentRequest provides useful methods for handling intent requests."""

    def intent_name(self) -> str:
        return self.event["request"]["intent"]["name"]

    def has_slots(self) -> bool:
        return "slots" in self.event["request"]["intent"]

    def filled_slots(self) -> List[str]:
        if self.has_slots() and len(self.event["request"]["intent"]["slots"]) > 0:
            return self.event["request"]["intent"]["slots"].keys()
        return None

    def value_of_slot(self, slot_name) -> str:
        if self.has_slots() and slot_name in self.event["request"]["intent"]["slots"]:
            return self.event["request"]["intent"]["slots"][slot_name]["value"]
        return None

    def id_value_of_slot(self, slot_name) -> str:
        if not self.has_slots() or slot_name not in self.event["request"]["intent"]["slots"]:
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

    def full_slot_catalog(self) -> Dict[str, Tuple[str, str]]:
        catalog = {}

        for slot_name in self.filled_slots():
            catalog[slot_name] = (
                self.value_of_slot(slot_name), 
                self.id_value_of_slot(slot_name))

        return catalog


@dataclass
class Card:
    """Card holds data that will be presented to the user as a card via the Alexa app."""
    title: str = ""
    body: str = ""
    image_url: str = ""

    def to_dict(self) -> dict:
        return {
            "type": "Standard",
            "title": self.title,
            "text": self.body,
            "image": {
                "smallImageUrl": self.image_url,
                "largeImageUrl": self.image_url
            }
        }


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
            output["card"] = self.card.to_dict()
        
        return output


@dataclass
class Router:
    """Router helps route an Alexa request to the appropriate response generator."""

    request_handlers: Dict[str, Callable[[Request, logging.Logger], Response]]
    intent_handlers: Dict[str, Callable[[IntentRequest, logging.Logger], Response]]

    def handle_request(self, event, context) -> dict:
        request = Request(event)
        request_type = request.request_type()
        
        logger = logging.getLogger(request.request_id())
        logger.setLevel(logging.DEBUG)

        handler_found = False
        response = Response(speech="Sorry, I couldn't route this request. Try asking again.")
        
        logger.info("Request received. Type: '%s'", request_type)

        if request_type == Request.TYPE_INTENT:
            intent_request = IntentRequest(request.event)
            intent_name = intent_request.intent_name()

            logger.info("Invoking intent. Name: '%s'", intent_name)
            if intent_request.has_slots():
                logger.debug("Found %d slot(s): %s", 
                    len(intent_request.filled_slots()), 
                    str(intent_request.full_slot_catalog()))
            else:
                logger.debug("No slots found.")

            if intent_name in self.intent_handlers:
                handler_found = True
                handler = self.intent_handlers[intent_name]
                
                try:
                    response = handler(intent_request, logger)
                except:
                    response = Response(speech="Sorry, I encountered an error. Try asking again.")
                    logger.exception("Intent handler threw exception! RECOVERING.")

        elif request_type in self.request_handlers:
            handler_found = True
            handler = self.request_handlers[request_type]
            
            try:
                response = handler(request, logger)
            except:
                response = Response(speech="Sorry, I encountered an error. Try asking again.")
                logger.exception("Request handler threw exception! RECOVERING.")

        if not handler_found:
            logger.warning("NO HANDLER FOUND for this request!")

        logger.debug("RESPONSE: '%s'", response.speech)
        if response.card is not None:
            logger.debug("CARD: title: '%s', body: '%s', image_url: '%s'",
                response.card.title, response.card.body, response.card.image_url)
        logger.debug("END SESSION: %r", response.end_session)

        return response.to_dict()
        
