import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


class FakeLogger:
    def error(self, _message):
        pass


class FakeServerless:
    def __init__(self):
        self.config = None

    def start(self, config):
        self.config = config


class FakeEngine:
    def __init__(self, batches):
        self.batches = batches

    async def generate(self, _job_input):
        for batch in self.batches:
            yield batch


def import_handler(mode=None):
    fake_serverless = FakeServerless()
    fake_runpod = types.SimpleNamespace(
        RunPodLogger=FakeLogger,
        serverless=fake_serverless,
    )
    env = {}
    if mode is not None:
        env["RUNPOD_HANDLER_MODE"] = mode

    module_name = "src_handler_under_test"
    handler_path = Path(__file__).resolve().parents[1] / "src" / "handler.py"
    spec = importlib.util.spec_from_file_location(module_name, handler_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules.pop(module_name, None)
    with patch.dict(sys.modules, {"runpod": fake_runpod}), patch.dict(
        "os.environ", env, clear=True
    ):
        spec.loader.exec_module(module)

    return module, fake_serverless


class HandlerTests(unittest.IsolatedAsyncioTestCase):
    async def test_one_shot_handler_returns_single_batch_without_stream_aggregation(self):
        module, serverless = import_handler()
        module.llama_engine = FakeEngine([{"ok": True}])

        result = await module.one_shot_handler({"input": {"prompt": "hi"}})

        self.assertEqual(result, {"ok": True})
        self.assertIs(serverless.config["handler"], module.one_shot_handler)
        self.assertNotIn("return_aggregate_stream", serverless.config)

    async def test_one_shot_handler_returns_multiple_batches_as_list(self):
        module, _serverless = import_handler()
        module.llama_engine = FakeEngine([{"a": 1}, {"b": 2}])

        result = await module.one_shot_handler({"input": {"prompt": "hi"}})

        self.assertEqual(result, [{"a": 1}, {"b": 2}])

    async def test_stream_mode_uses_aggregate_streaming_handler(self):
        module, serverless = import_handler("stream")
        module.llama_engine = FakeEngine([{"a": 1}, {"b": 2}])

        result = [
            batch async for batch in module.stream_handler({"input": {"prompt": "hi"}})
        ]

        self.assertEqual(result, [{"a": 1}, {"b": 2}])
        self.assertIs(serverless.config["handler"], module.stream_handler)
        self.assertTrue(serverless.config["return_aggregate_stream"])

    async def test_invalid_handler_mode_fails_fast(self):
        with self.assertRaisesRegex(RuntimeError, "RUNPOD_HANDLER_MODE"):
            import_handler("invalid")


if __name__ == "__main__":
    unittest.main()
