import time
import unittest.mock
import requests_mock
import requests

from skill_sdk.test_helpers import FunctionalTest, set_translations, test_context
from impl.skill import skill

K8S_READINESS = 'http://localhost:4242/k8s/readiness'
RASA_WEBHOOK = "http://localhost:5005/webhooks/rest/webhook"
RASA_RESPONSE = '[{"text":"Hello"}]'


@requests_mock.mock()
class TestSkill(unittest.TestCase):

    def test_dialog_handover(self, req_mock):
        req_mock.post(RASA_WEBHOOK, text=RASA_RESPONSE)
        self.assertEqual('<speak><lang xml:lang="de"><s>Hello</s></lang></speak>',
                         skill.test_intent('DIALOG__HANDOVER', stt='Hello').text)

    def test_handle(self, req_mock):
        req_mock.post(RASA_WEBHOOK, text=RASA_RESPONSE)
        self.assertEqual('<speak><lang xml:lang="de"><s>Hello</s></lang></speak>',
                         skill.test_intent('CVI_INTERNAL_ASK_FREETEXT', stt='Hello').text)


class TestRunner(FunctionalTest):

    @classmethod
    def setUpClass(cls) -> None:
        """
        Add time.sleep to let bottle thread start

        :return:
        """
        super().setUpClass()
        time.sleep(0.1)

    def test_k8s_readiness_not_ready(self):
        """ Respond 503 if Rasa server unavailable """
        response = requests.get(K8S_READINESS)
        self.assertEqual(response.status_code, 503)

    def test_k8s_readiness_ready(self):
        """ Respond 'ok' if Rasa server running """
        with requests_mock.Mocker(real_http=True) as req_mock:
            req_mock.register_uri('GET', "http://localhost:5005", text='ok')
            response = requests.get(K8S_READINESS)
            self.assertTrue(response.ok)
            self.assertEqual('ok', response.text)
