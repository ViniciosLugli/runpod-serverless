<p align="center">
    <img src="https://raw.githubusercontent.com/ggml-org/llama.cpp/master/media/llama1-icon-transparent.png" alt="llama.cpp logo" width="128">
</p>

# Serverless llama.cpp inference worker for RunPod

[![Runpod](https://api.runpod.io/badge/ViniciosLugli/runpod-serverless)](https://console.runpod.io/hub/ViniciosLugli/runpod-serverless)

This repository contains a serverless inference worker for running llama.cpp models on RunPod. It starts `llama-server` locally and forwards RunPod jobs to the OpenAI-compatible llama.cpp API.

Supported local llama.cpp routes:

- `v1/models`
- `v1/chat/completions`
- `v1/completions`

One-shot responses are the default. Streaming responses are supported by setting
`RUNPOD_HANDLER_MODE=stream`.

**Credits:** this project is based on [Jacob-ML/inference-worker](https://github.com/Jacob-ML/inference-worker), which is a fork of [SvenBrnn's `runpod-worker-ollama`](https://github.com/SvenBrnn/runpod-worker-ollama).

## Setup

Use RunPod cached models when the Hugging Face repository is small enough to cache as a whole. RunPod currently caches an entire repository, so multi-quant GGUF repos can be too large. See [cached models](./docs/cached.md).

For low-latency serverless endpoints, configure active workers and model caching in RunPod. The worker code cannot prevent platform scale-to-zero cold starts by itself.

RunPod Hub indexes GitHub releases, not only commits. After changing this template, create a new release so the Hub can build and test the latest version.

## Configuration

- `LLAMA_SERVER_CMD_ARGS`: command line arguments for `llama-server`. Do not define `--port`. If cached model mode is enabled, do not define `-hf` or `-m` here.
- `LLAMA_CACHED_MODEL`: Hugging Face repo id for RunPod cached model mode.
- `LLAMA_CACHED_GGUF_PATH`: GGUF path inside the Hugging Face repo.
- `LLAMA_CACHED_MMPROJ_PATH`: optional mmproj path inside the same cached Hugging Face repo.
- `LLAMA_MMPROJ_PATH`: optional local or network-volume mmproj path.
- `LLAMA_MMPROJ_URL`: optional mmproj URL passed to `llama-server --mmproj-url`.
- `LLAMA_DEFAULT_MODEL`: optional model id used when requests omit `model`.
- `LLAMA_OPENAI_BASE_URL`: optional local OpenAI base URL. Defaults to `http://localhost:3098/v1/`.
- `LLAMA_OPENAI_API_KEY`: optional API key for the local OpenAI client. Defaults to `unused`.
- `LLAMA_SERVER_HOST`: optional bind host. Defaults to `0.0.0.0`.
- `LLAMA_CACHE_DIR`: Hugging Face cache directory. Defaults to `/runpod-volume/huggingface-cache/hub`.
- `LLAMA_STARTUP_TIMEOUT_SECONDS`: startup wait timeout. Defaults to `120`.
- `MAX_CONCURRENCY`: maximum concurrent RunPod jobs. Default is `1`.
- `RUNPOD_HANDLER_MODE`: `one-shot` or `stream`. Default is `one-shot`.

Only set one mmproj source at a time. If any mmproj env var is set, do not also define `--mmproj` or `--mmproj-url` in `LLAMA_SERVER_CMD_ARGS`.

## Request Formats

RunPod queue requests use the standard wrapper:

```json
{
  "input": {
    "messages": [
      {"role": "user", "content": "Hello"}
    ],
    "temperature": 0,
    "max_tokens": 128
  }
}
```

Vision messages pass through to llama.cpp unchanged:

```json
{
  "input": {
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "Describe this image."},
          {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
        ]
      }
    ],
    "max_tokens": 128
  }
}
```

You can also proxy raw OpenAI-compatible routes:

```json
{
  "input": {
    "openai_route": "/v1/chat/completions",
    "openai_input": {
      "messages": [{"role": "user", "content": "Hello"}],
      "temperature": 0
    }
  }
}
```

For direct OpenAI SDK `base_url` usage, expose a RunPod Pod or load-balanced service to `llama-server` and point the SDK at its `/v1` URL. Queue-based serverless endpoints still require `/run` or `/runsync` with the `input` wrapper.

## Qwen3.6 Vision Example

Set the RunPod endpoint Model field to:

```text
https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF
```

This public repo contains many GGUF quantizations. RunPod model caching may fail because it tries to cache the full repository, not only `Q4_K_M`. For this model, leave the RunPod Model field empty and let llama.cpp download only the selected quantization:

```text
LLAMA_SERVER_CMD_ARGS=-hf llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF:Q4_K_M --ctx-size 8192 --cache-type-k f16 --cache-type-v f16 --flash-attn on -ngl 999 --image-min-tokens 1024 --image-max-tokens 1024 --batch-size 512 --ubatch-size 128 --parallel 1 --spec-type none --metrics --jinja --no-mmap
LLAMA_CACHED_MODEL=
LLAMA_CACHED_GGUF_PATH=
LLAMA_CACHED_MMPROJ_PATH=
LLAMA_MMPROJ_URL=https://huggingface.co/llmfan46/Qwen3.6-35B-A3B-uncensored-heretic-GGUF/resolve/main/Qwen3.6-35B-A3B-uncensored-heretic-mmproj-BF16.gguf
MAX_CONCURRENCY=1
```

If you mirror only the selected GGUF and mmproj into a small Hugging Face repository, cache mode is safe:

```text
LLAMA_CACHED_MODEL=your-user/your-single-quant-repo
LLAMA_CACHED_GGUF_PATH=Qwen3.6-35B-A3B-uncensored-heretic-Q4_K_M.gguf
LLAMA_CACHED_MMPROJ_PATH=Qwen3.6-35B-A3B-uncensored-heretic-mmproj-BF16.gguf
```

## License

Please see [LICENSE](./LICENSE).
