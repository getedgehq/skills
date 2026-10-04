"""One reply generator for both backends, with the fixed decoding settings used everywhere.

backend "hf":  transformers + optional PEFT adapter (Linux/Windows, CPU or NVIDIA)
backend "mlx": mlx-lm + optional adapter folder (Apple Silicon Mac)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_hf, messages  # noqa: E402

DECODING = {"temperature": 0.7, "top_p": 0.9, "max_new_tokens": 300}


class Generator:
    def __init__(self, model, adapter=None, revision=None, backend="hf", device="cpu"):
        self.backend = backend
        if backend == "mlx":
            from mlx_lm import load
            self.model, self.tok = load(model, adapter_path=adapter)
        else:
            self.model, self.tok = load_hf(model, adapter=adapter, revision=revision, device=device)
            self.model.eval()
        self.device = device

    def reply(self, system, prompt, seed=42):
        msgs = messages(system, prompt)
        if self.backend == "mlx":
            import mlx.core as mx
            from mlx_lm import generate
            from mlx_lm.sample_utils import make_sampler
            mx.random.seed(seed)
            text = self.tok.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
            return generate(self.model, self.tok, prompt=text, max_tokens=DECODING["max_new_tokens"],
                            sampler=make_sampler(temp=DECODING["temperature"], top_p=DECODING["top_p"])).strip()
        import torch
        torch.manual_seed(seed)
        ids = self.tok.apply_chat_template(msgs, add_generation_prompt=True, return_tensors="pt", return_dict=True)
        ids = {k: v.to(self.device) for k, v in ids.items()}
        with torch.no_grad():
            out = self.model.generate(**ids, do_sample=True, temperature=DECODING["temperature"], top_p=DECODING["top_p"],
                                      max_new_tokens=DECODING["max_new_tokens"],
                                      pad_token_id=self.tok.pad_token_id or self.tok.eos_token_id)
        return self.tok.decode(out[0][ids["input_ids"].shape[1]:], skip_special_tokens=True).strip()
