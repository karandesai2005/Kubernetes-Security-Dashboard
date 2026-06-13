"""Structured logging setup using structlog."""
import structlog

# TODO: configure processors, add request-id middleware
logger = structlog.get_logger()
