# Hello World 2019 Alexa Skill
# Provides information about the CUhackit Hello World '19 hackathon event.
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

import alexa
import random
import logging
import API

sample_questions = [
    "Is there anything due today?",
    "What is my grade in math?"
]

def handle_request_launch(request: alexa.Request, logger: logging.Logger) -> alexa.Response:
    response = alexa.Response()

    response.speech = "Hi there! You've successfully launched the Canvas skill. "
    response.speech += "You can ask me questions about your grades, classes, or homework assignments on Canvas. What do you want to know?"

    response.end_session = False

    return response


def handle_intent_help(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
    response = alexa.Response()

    response.speech = "You can ask me questions about your classes. For example, try asking: "
    response.speech += random.choice(sample_questions)

    return response


# def handle_intent_what_day(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
#     response = alexa.Response()

#     response.speech = "CU hack-it Hello World 2019 will take place on Saturday, October 19th, 2019."

#     return response


# def handle_intent_event_time(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
#     response = alexa.Response()

#     event_id = request.id_value_of_slot("event_name")

#     if event_id is None or event_id not in hackathon_events:
#         response.speech = "Sorry, I don't have information about that event."
#         return response
    
#     event_details = hackathon_events[event_id]
#     event_time = event_details[0]
#     event_name = event_details[1]

#     response.speech = "{} is at {}.".format(event_name, event_time)

#     return response

def handle_intent_current_classes(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
    response = alexa.Response()

    courses = API.get_courses().values

    sentence =  ", ".join(courses[:-1])
    sentence = sentence+", and".join(courses[-1])

    response.speech = sentence

    return response

def handle_intent_stop_cancel(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
    response = alexa.Response()

    response.speech = "Goodbye."

    return response
    
def handle_intent_assignment_due(request: alexa.IntentRequest, logger: logging.Logger) -> alexa.Response:
    response = alexa.Response()

    response.speech = "Your upcoming assignments are"

    uassignments = API.get_assignments({"bucket": "upcoming"}) 

    for item in uassignments
        name=item["name"]
        response.speech += name + " "

    return response


request_handlers = {
    alexa.Request.TYPE_LAUNCH: handle_request_launch,
}

intent_handlers = {
    alexa.Request.INTENT_FALLBACK: handle_intent_help,
    alexa.Request.INTENT_HELP: handle_intent_help,
    alexa.Request.INTENT_CANCEL: handle_intent_stop_cancel,
    alexa.Request.INTENT_STOP: handle_intent_stop_cancel,
    "CURRENT_CLASSES": handle_intent_current_classes,
    "ASSIGNMENT_DUE": handle_intent_assignment_due
}
 
router = alexa.Router(request_handlers, intent_handlers)
lambda_handler = router.handle_request
