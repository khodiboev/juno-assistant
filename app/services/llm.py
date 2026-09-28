import threading
from functools import lru_cache
from typing import Iterator

from app.core.config import get_settings

_generate_lock = threading.Lock()


def model_label() -> str:
    settings = get_settings()
    if settings.llm_backend == "llama_cpp":
        return settings.llm_gguf_file
    return settings.llm_model


def resolve_device(preference: str) -> str:
    import torch

    if preference != "auto":
        return preference
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@lru_cache
def get_llm():
    """Returns (tokenizer, model, device). For llama.cpp the tokenizer is built into the model."""
    settings = get_settings()

    if settings.llm_backend == "llama_cpp":
        from llama_cpp import Llama

        model = Llama.from_pretrained(
            repo_id=settings.llm_gguf_repo,
            filename=settings.llm_gguf_file,
            n_ctx=settings.llm_context,
            n_threads=settings.llm_threads,
            n_gpu_layers=settings.llm_gpu_layers,
            verbose=False,
        )
        return None, model, "llama.cpp"

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    device = resolve_device(settings.llm_device)
    dtype = torch.float32 if device == "cpu" else torch.float16

    tokenizer = AutoTokenizer.from_pretrained(settings.llm_model)
    model = AutoModelForCausalLM.from_pretrained(settings.llm_model, dtype=dtype)
    model.generation_config.max_length = None
    model = model.to(device).eval()
    return tokenizer, model, device


# ---------- llama.cpp backend ----------

def _llama_completion(messages: list[dict], stream: bool):
    settings = get_settings()
    _, model, _ = get_llm()
    return model.create_chat_completion(
        messages=messages,
        max_tokens=settings.llm_max_new_tokens,
        temperature=settings.llm_temperature,
        repeat_penalty=1.1,
        stream=stream,
    )


# ---------- transformers backend ----------

def _generation_kwargs(messages: list[dict]) -> dict:
    settings = get_settings()
    tokenizer, _, device = get_llm()

    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    do_sample = settings.llm_temperature > 0
    return dict(
        **inputs,
        max_new_tokens=settings.llm_max_new_tokens,
        do_sample=do_sample,
        temperature=settings.llm_temperature if do_sample else None,
        top_p=0.9 if do_sample else None,
        repetition_penalty=1.1,
        pad_token_id=tokenizer.eos_token_id,
    )


# ---------- public API ----------

def generate(messages: list[dict]) -> str:
    settings = get_settings()

    if settings.llm_backend == "llama_cpp":
        with _generate_lock:
            result = _llama_completion(messages, stream=False)
        return (result["choices"][0]["message"]["content"] or "").strip()

    import torch

    tokenizer, model, _ = get_llm()
    kwargs = _generation_kwargs(messages)
    with _generate_lock, torch.no_grad():
        output = model.generate(**kwargs)
    new_tokens = output[0][kwargs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def stream_generate(messages: list[dict]) -> Iterator[str]:
    settings = get_settings()

    if settings.llm_backend == "llama_cpp":
        with _generate_lock:
            for chunk in _llama_completion(messages, stream=True):
                text = chunk["choices"][0]["delta"].get("content")
                if text:
                    yield text
        return

    import torch
    from transformers import TextIteratorStreamer

    tokenizer, model, _ = get_llm()
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)
    kwargs = _generation_kwargs(messages)
    kwargs["streamer"] = streamer

    def run() -> None:
        try:
            with _generate_lock, torch.no_grad():
                model.generate(**kwargs)
        except Exception:
            streamer.end()
            raise

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    for text in streamer:
        if text:
            yield text
    thread.join()
