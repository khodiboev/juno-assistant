import threading
from functools import lru_cache
from typing import Iterator

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

from app.core.config import get_settings

_generate_lock = threading.Lock()


def resolve_device(preference: str) -> str:
    if preference != "auto":
        return preference
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@lru_cache
def get_llm():
    settings = get_settings()
    device = resolve_device(settings.llm_device)
    dtype = torch.float32 if device == "cpu" else torch.float16

    tokenizer = AutoTokenizer.from_pretrained(settings.llm_model)
    model = AutoModelForCausalLM.from_pretrained(settings.llm_model, dtype=dtype)
    model.generation_config.max_length = None
    model = model.to(device).eval()
    return tokenizer, model, device


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


def generate(messages: list[dict]) -> str:
    tokenizer, model, _ = get_llm()
    kwargs = _generation_kwargs(messages)

    with _generate_lock, torch.no_grad():
        output = model.generate(**kwargs)

    new_tokens = output[0][kwargs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()


def stream_generate(messages: list[dict]) -> Iterator[str]:
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
