import threading
from functools import lru_cache

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

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


def generate(messages: list[dict]) -> str:
    settings = get_settings()
    tokenizer, model, device = get_llm()

    prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    do_sample = settings.llm_temperature > 0
    with _generate_lock, torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=settings.llm_max_new_tokens,
            do_sample=do_sample,
            temperature=settings.llm_temperature if do_sample else None,
            top_p=0.9 if do_sample else None,
            repetition_penalty=1.1,
            pad_token_id=tokenizer.eos_token_id,
        )

    new_tokens = output[0][inputs["input_ids"].shape[1]:]
    return tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
