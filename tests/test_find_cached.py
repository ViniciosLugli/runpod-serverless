import os
import tempfile
import unittest

from find_cached import find_model_path


class FindCachedTests(unittest.TestCase):
    def test_returns_existing_file_from_latest_snapshot(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            base = os.path.join(
                cache_dir,
                "models--owner--model",
                "snapshots",
            )
            older = os.path.join(base, "111")
            newer = os.path.join(base, "222")
            os.makedirs(older)
            os.makedirs(newer)
            open(os.path.join(older, "model.gguf"), "w").close()
            expected = os.path.join(newer, "model.gguf")
            open(expected, "w").close()

            self.assertEqual(
                find_model_path("owner/model", "model.gguf", cache_dir),
                expected,
            )

    def test_returns_none_for_missing_file(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            os.makedirs(
                os.path.join(
                    cache_dir,
                    "models--owner--model",
                    "snapshots",
                    "111",
                )
            )

            self.assertIsNone(
                find_model_path("owner/model", "missing.gguf", cache_dir)
            )


if __name__ == "__main__":
    unittest.main()
