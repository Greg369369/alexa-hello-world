import alexa
import random

sample_questions = [
    "When is the hackathon?",
    "What time is cup stacking?",
    "What time is judging?"
]

hackathon_events = {
    "OPEN_CEREMONY": 
        ("8:30 am", "Opening Ceremony"),
    "BEGIN_HACK": 
        ("9:00 am", "Hacking Begins"),
    "IDEA_JAM": 
        ("9:30 am", "Idea Jam"),
    "GITHUB_WORKSHOP": 
        ("10:30 am", "Intro to GitHub Workshop"),
    "LUNCH": 
        ("12:00 pm", "Lunch"),
    "CUP_STACK": 
        ("2:00 pm", "Cup Stacking"),
    "VR_DEMO": 
        ("3:30 pm", "VR Demo"),
    "END_HACK": 
        ("6:00 pm", "Hacking Ends"),
    "DINNER": 
        ("6:30 pm", "Dinner"),
    "JUDGE": 
        ("7:00 pm", "Judging and Demos"),
    "CLOSE_CEREMONY": 
        ("8:00 pm", "Closing Ceremony")
}


def handle_request_launch(request: alexa.Request) -> alexa.Response:
    response = alexa.Response()

    response.speech = "Hi there! You've successfully launched the Hello World demo skill. "
    response.speech += "You can ask me basic questions about the hackathon. What do you want to know?"

    response.end_session = False

    return response


def handle_intent_help(request: alexa.Request) -> alexa.Response:
    response = alexa.Response()

    response.speech = "You can ask me basic questions about the hackathon. For example, try asking: "
    response.speech += random.choice(sample_questions)

    return response


def handle_intent_what_day(request: alexa.Request) -> alexa.Response:
    response = alexa.Response()

    response.speech = "CU hack-it Hello World 2019 will take place on Saturday, October 19th, 2019."

    return response


def handle_intent_event_time(request: alexa.IntentRequest) -> alexa.Response:
    response = alexa.Response()

    event_id = request.id_value_of_slot("event_name")

    if event_id is None or event_id not in hackathon_events:
        response.speech = "Sorry, I don't have information about that event."
        return response
    
    event_details = hackathon_events[event_id]
    event_time = event_details[0]
    event_name = event_details[1]

    response.speech = "{} is at {}.".format(event_name, event_time)

    return response


def handle_intent_stop_cancel(request: alexa.Request) -> alexa.Response:
    response = alexa.Response()

    response.speech = "Goodbye."

    return response


request_handlers = {
    alexa.Request.TYPE_LAUNCH: handle_request_launch,
}

intent_handlers = {
    alexa.Request.INTENT_HELP: handle_intent_help,
    alexa.Request.INTENT_CANCEL: handle_intent_stop_cancel,
    alexa.Request.INTENT_STOP: handle_intent_stop_cancel,
    "what_day": handle_intent_what_day,
    "event_time": handle_intent_event_time
}

router = alexa.Router(request_handlers, intent_handlers)
lambda_handler = router.handle_request
