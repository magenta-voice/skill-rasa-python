import logging
from typing import Any, Dict, List, Text, Tuple
from skill_sdk.config import config
from skill_sdk.requests import CircuitBreakerSession, RequestException
from skill_sdk import Response, ask_freetext, skill, ssml, context
from skill_sdk.responses import Card

# This import is necessary to overwrite '/k8s/readiness' route
from skill_sdk.services.k8s import readiness


LOGGER = logging.getLogger(__name__)

# This is where we talk to Rasa server by default
DEFAULT_SERVER_URL = "http://localhost:5005"


# This intent is resolved by first invocation
@skill.intent_handler('RASA__HANDOVER')
def handle_invoke(stt: Text) -> Response:
    return handle_user_answer(stt)


# All consequent invocations use CVI_INTERNAL_ASK_FREETEXT, if ASK_FREETEXT type is set as Response
@skill.intent_handler('CVI_INTERNAL_ASK_FREETEXT')
def handle_user_answer(stt: Text) -> Response:
    """
    Send user response to Rasa server and speak out the output

    :param stt:     STT response
    :param zipcode: Device ZIP code
    :return:
    """
    LOGGER.debug('STT text: %s, intent: %s, session: %s', stt, context.intent_name, context.session.session_id)

    server_url = config.get('rasa', 'server_url', fallback=DEFAULT_SERVER_URL)
    response = send_message_receive_block(server_url, context.session.session_id, stt)
    LOGGER.debug('Response from Rasa: %s', repr(response))

    text, card = format_bot_output(response)
    LOGGER.debug('Formatted output: %s, with card: %s', repr(text), repr(card))

    return ask_freetext(text, card=card)


def format_bot_output(response: List[Dict[Text, Any]]) -> Tuple[Text, Card]:
    """
    Format output from Rasa server:
        - join strings if text
        - send card if image present

    :param response:
    :return:
    """
    speech = ssml.Speech()
    [speech.sentence(message['text']) for message in response if 'text' in message]

    images = [message['image'] for message in response if 'image' in message]

    return str(speech), Card("GENERIC_DEFAULT", icon_url=images[0]) if images else None


def send_message_receive_block(server_url, sender_id, message) -> List[Dict[Text, Any]]:
    """
    Send message to Rasa webhook

    :param server_url:
    :param sender_id:
    :param message:
    :return:
    """
    payload = {"sender": sender_id, "message": message}

    url = f"{server_url}/webhooks/rest/webhook"
    with CircuitBreakerSession() as session:
        with session.post(url, json=payload) as resp:
            return resp.json()


@skill.get('/k8s/startup')
@skill.get('/k8s/readiness')
def _pre_check():
    """
    Startup probe:
        check if Rasa is answering at `server_url` and return "OK"

    """
    server_url = config.get('rasa', 'server_url', fallback=DEFAULT_SERVER_URL)
    try:
        return CircuitBreakerSession().get(server_url).ok and 'ok'
    except RequestException:
        return skill.HTTPResponse('Not ready', 503)
