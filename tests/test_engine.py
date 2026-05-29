import unittest
from unittest.mock import patch

from engine import ensure_model, normalize_route


class EngineTests(unittest.TestCase):
    def test_normalizes_openai_routes(self):
        cases = {
            "/v1/models": "/models",
            "v1/chat/completions": "/chat/completions",
            "/openai/v1/chat/completions": "/chat/completions",
            "/v1/completions": "/completions",
        }

        for route, expected in cases.items():
            with self.subTest(route=route):
                self.assertEqual(normalize_route(route), expected)

    def test_ensure_model_does_not_query_when_model_is_present(self):
        payload = {"model": "provided-model"}

        with patch("engine.default_model_id") as default_model_id:
            ensure_model(payload)

        default_model_id.assert_not_called()
        self.assertEqual(payload["model"], "provided-model")


if __name__ == "__main__":
    unittest.main()
