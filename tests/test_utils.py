import unittest

from utils import JobInput


class JobInputTests(unittest.TestCase):
    def test_preserves_openai_chat_payload_with_images_and_params(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": "data:image/png;base64,AAAA",
                        },
                    },
                ],
            }
        ]
        job_input = JobInput(
            {
                "messages": messages,
                "temperature": 0,
                "max_tokens": 64,
                "stream": True,
            }
        )

        self.assertEqual(job_input.openai_input["messages"], messages)
        self.assertEqual(job_input.openai_input["temperature"], 0)
        self.assertEqual(job_input.openai_input["max_tokens"], 64)
        self.assertTrue(job_input.openai_input["stream"])


if __name__ == "__main__":
    unittest.main()
