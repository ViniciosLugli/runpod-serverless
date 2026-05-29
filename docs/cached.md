# Using Cached Models

RunPod model caching stores Hugging Face snapshots on local worker storage under:

```text
/runpod-volume/huggingface-cache/hub
```

The worker resolves cached files from that directory and passes local paths to `llama-server`. This prevents invalid launches such as `-m None` and avoids repeated model downloads during serverless startup.

## Main Model

Set the RunPod endpoint Model field to the Hugging Face model URL:

```text
https://huggingface.co/unsloth/gemma-3-270m-it-GGUF
```

Then set:

```text
LLAMA_CACHED_MODEL=unsloth/gemma-3-270m-it-GGUF
LLAMA_CACHED_GGUF_PATH=gemma-3-270m-it-Q8_0.gguf
```

Do not put `-m`, `--model`, `-hf`, or `--hf-repo` in `LLAMA_SERVER_CMD_ARGS` while cached model mode is enabled.

## Multimodal Projector

If the mmproj file is in the same cached Hugging Face repository, set:

```text
LLAMA_CACHED_MMPROJ_PATH=mmproj-file.gguf
```

If RunPod does not cache the mmproj file, use one of:

```text
LLAMA_MMPROJ_PATH=/runpod-volume/path/to/mmproj.gguf
LLAMA_MMPROJ_URL=https://huggingface.co/user/repo/resolve/main/mmproj.gguf
```

Set only one mmproj source. Do not also pass `--mmproj` or `--mmproj-url` in `LLAMA_SERVER_CMD_ARGS`.

## Helper

The cache helper can be used manually:

```bash
python3 src/find_cached.py HF_MODEL_ID PATH_IN_REPO
```

It exits non-zero if the file cannot be found.

## Startup Time

To reduce serverless startup time:

- use RunPod model caching
- keep the model and mmproj in the same Hugging Face repo when possible
- avoid `--mmproj-url` for large projectors if cache can be used
- configure active workers in RunPod when low first-token latency matters
- keep `MAX_CONCURRENCY=1` for large single-slot llama.cpp models unless `--parallel` is intentionally increased
