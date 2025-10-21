import os
import sys
import unittest
from unittest.mock import patch

# Ensure package root is on sys.path so tests can import the application modules
# Add both the package folder and the project root so absolute imports used in app modules work
pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
for p in (pkg_root, project_root):
    if p not in sys.path:
        sys.path.insert(0, p)

from common.ai_client import AIClient, get_client


class TestAIClient(unittest.TestCase):
    def test_unknown_provider_raises(self):
        with self.assertRaises(Exception):
            AIClient('nonexistent')

    @patch('OnlineJudgeSystem.common.ai_client.requests.post')
    def test_ask_success(self, mock_post):
        mock_resp = mock_post.return_value
        mock_resp.status_code = 200
        mock_resp.json.return_value = {'answer': 'hello from provider'}

        client = AIClient('kimi')
        success, resp = client.ask('hi')
        self.assertTrue(success)
        self.assertIn('answer', resp)
        self.assertEqual(resp['answer'], 'hello from provider')

    @patch('OnlineJudgeSystem.common.ai_client.requests.post')
    def test_ask_network_error(self, mock_post):
        mock_post.side_effect = Exception('network down')
        client = AIClient('kimi')
        success, resp = client.ask('hi')
        self.assertFalse(success)
        self.assertIn('error', resp)


if __name__ == '__main__':
    unittest.main()
