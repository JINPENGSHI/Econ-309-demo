from dataclasses import dataclass, field
from typing import Any
from tools import get_unemployment_data, calculate_change, summarize_period

ALLOWED_TOOLS = {'get_unemployment_data', 'calculate_change', 'summarize_period'}

@dataclass
class Harness:
    max_calls: int = 6
    calls: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)

    def execute(self, tool: str, **kwargs):
        self.calls += 1
        if self.calls > self.max_calls:
            self.events.append({'kind':'blocked','tool':tool,'message':'Tool-call budget exceeded'})
            return None
        if tool not in ALLOWED_TOOLS:
            self.events.append({'kind':'blocked','tool':tool,'message':'Tool not on allowlist'})
            return None
        try:
            result = globals()[tool](**kwargs)
            self.events.append({'kind':'success','tool':tool,'arguments':kwargs,
                                'message':f'Executed successfully (call {self.calls}/{self.max_calls})'})
            return result
        except (ValueError, TypeError, KeyError) as exc:
            self.events.append({'kind':'error','tool':tool,'arguments':kwargs,'message':str(exc)})
            return None
