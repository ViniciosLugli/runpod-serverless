import os
import tempfile
import unittest
from unittest.mock import patch

import launcher


def cached_file(cache_dir, repo, snapshot, path):
    full_path = os.path.join(
        cache_dir,
        f"models--{repo.replace('/', '--').lower()}",
        "snapshots",
        snapshot,
        path,
    )
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    open(full_path, "w").close()
    return full_path


class LauncherTests(unittest.TestCase):
    def test_cached_model_and_mmproj_build_argv(self):
        with tempfile.TemporaryDirectory() as cache_dir:
            model_path = cached_file(cache_dir, "owner/model", "abc", "model.gguf")
            mmproj_path = cached_file(cache_dir, "owner/model", "abc", "mmproj.gguf")
            env = {
                "LLAMA_CACHE_DIR": cache_dir,
                "LLAMA_CACHED_MODEL": "owner/model",
                "LLAMA_CACHED_GGUF_PATH": "model.gguf",
                "LLAMA_CACHED_MMPROJ_PATH": "mmproj.gguf",
                "LLAMA_SERVER_CMD_ARGS": "--ctx-size 4096",
            }

            with patch.dict(os.environ, env, clear=True):
                argv = launcher.build_llama_args()

            self.assertIn("-m", argv)
            self.assertIn(model_path, argv)
            self.assertIn("--mmproj", argv)
            self.assertIn(mmproj_path, argv)
            self.assertIn("--host", argv)
            self.assertIn("0.0.0.0", argv)
            self.assertEqual(argv[-2:], ["--port", "3098"])

    def test_rejects_manual_model_flag_in_cached_mode(self):
        env = {
            "LLAMA_CACHED_MODEL": "owner/model",
            "LLAMA_CACHED_GGUF_PATH": "model.gguf",
            "LLAMA_SERVER_CMD_ARGS": "-m manual.gguf",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "model flags"):
                launcher.build_llama_args()

    def test_rejects_duplicate_mmproj_sources(self):
        env = {
            "LLAMA_SERVER_CMD_ARGS": "-hf owner/model:Q4_K_M",
            "LLAMA_MMPROJ_PATH": "/tmp/mmproj.gguf",
            "LLAMA_MMPROJ_URL": "https://example.com/mmproj.gguf",
        }

        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "only one"):
                launcher.build_llama_args()

    def test_rejects_port(self):
        env = {"LLAMA_SERVER_CMD_ARGS": "-hf owner/model:Q4_K_M --port 1234"}

        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesRegex(RuntimeError, "port"):
                launcher.build_llama_args()

    def test_preserves_explicit_host(self):
        env = {"LLAMA_SERVER_CMD_ARGS": "-hf owner/model:Q4_K_M --host 127.0.0.1"}

        with patch.dict(os.environ, env, clear=True):
            argv = launcher.build_llama_args()

        self.assertEqual(argv.count("--host"), 1)
        self.assertIn("127.0.0.1", argv)


if __name__ == "__main__":
    unittest.main()
