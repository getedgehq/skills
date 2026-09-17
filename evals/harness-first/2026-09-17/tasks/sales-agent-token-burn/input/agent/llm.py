"""Thin wrapper around the model API."""
import json
import os
from dataclasses import dataclass, field

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.json")


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class Response:
    content: list
    text: str
    tool_calls: list
    input_tokens: int
    output_tokens: int
    cost_usd: float
    stop_reason: str = ""
    model: str = ""
    extra: dict = field(default_factory=dict)


class Client:
    def __init__(self, model, max_tokens, price_in, price_out):
        self.model = model
        self.max_tokens = max_tokens
        self.price_in = price_in
        self.price_out = price_out

    @classmethod
    def from_config(cls):
        cfg = json.load(open(CONFIG_PATH))
        return cls(cfg["model"], cfg["max_tokens"], cfg["price_per_mtok_in"], cfg["price_per_mtok_out"])

    def complete(self, system, messages, tools):
        import anthropic  # lazy

        client = anthropic.Anthropic()
        msg = client.messages.create(model=self.model, max_tokens=self.max_tokens, system=system,
                                     messages=messages, tools=tools)
        calls = [ToolCall(b.id, b.name, b.input) for b in msg.content if b.type == "tool_use"]
        text = "".join(b.text for b in msg.content if b.type == "text")
        cost = msg.usage.input_tokens / 1e6 * self.price_in + msg.usage.output_tokens / 1e6 * self.price_out
        return Response([b.model_dump() for b in msg.content], text, calls, msg.usage.input_tokens,
                        msg.usage.output_tokens, round(cost, 6), msg.stop_reason, self.model)
