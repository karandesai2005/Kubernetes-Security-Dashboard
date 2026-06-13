"""
Falco gRPC / webhook event processor.
Consumes events and persists them as ThreatEvent records.

TODO:
  - Connect to Falco gRPC output endpoint
  - Parse and normalise alert payloads
  - Map Falco priority → internal severity enum
"""

class FalcoProcessor:
    async def start(self):
        raise NotImplementedError

    async def process_event(self, raw: dict):
        raise NotImplementedError
