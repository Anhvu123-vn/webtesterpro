"""
SSE (Server-Sent Events) manager cho real-time progress updates.

Sử dụng Redis pub/sub hoặc in-memory event emitter để broadcast events.
"""

import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)

# In-memory event emitter (đơn giản, hoạt động cho single-instance)
# Để production nên dùng Redis pub/sub
class EventEmitter:
    """Simple in-memory event emitter for SSE broadcasting."""
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._subscribers: dict[int, list[Callable]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def subscribe(self, report_id: int, callback: Callable) -> None:
        """Subscribe to events for a specific report."""
        async with self._lock:
            self._subscribers[report_id].append(callback)
    
    async def unsubscribe(self, report_id: int, callback: Callable) -> None:
        """Unsubscribe from report events."""
        async with self._lock:
            if report_id in self._subscribers:
                self._subscribers[report_id] = [
                    cb for cb in self._subscribers[report_id] if cb != callback
                ]
    
    async def emit(self, report_id: int, event_type: str, data: dict[str, Any]) -> None:
        """Emit an event to all subscribers of a report."""
        message = json.dumps({
            "type": event_type,
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        })
        
        async with self._lock:
            subscribers = self._subscribers.get(report_id, []).copy()
        
        for callback in subscribers:
            try:
                await callback(message)
            except Exception as exc:
                logger.error(f"Error in SSE callback: {exc}")
    
    def get_subscriber_count(self, report_id: int) -> int:
        """Get number of active subscribers for a report."""
        return len(self._subscribers.get(report_id, []))


# Global event emitter instance
event_emitter = EventEmitter()


# Background task để emit events từ sync code (test_runner.py)
_emit_queue: asyncio.Queue = asyncio.Queue()
_emit_task: asyncio.Task | None = None


async def _emit_worker():
    """Worker that processes emit requests from sync code."""
    while True:
        try:
            report_id, event_type, data = await _emit_queue.get()
            await event_emitter.emit(report_id, event_type, data)
            _emit_queue.task_done()
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error(f"Emit worker error: {exc}")


def start_emit_worker():
    """Start the emit worker (call once at startup)."""
    global _emit_task
    if _emit_task is None or _emit_task.done():
        _emit_task = asyncio.create_task(_emit_worker())


def queue_emit(report_id: int, event_type: str, data: dict[str, Any]) -> None:
    """Queue an emit from sync code (non-blocking)."""
    try:
        _emit_queue.put_nowait((report_id, event_type, data))
    except asyncio.QueueFull:
        logger.warning(f"Emit queue full for report {report_id}")


# Helper functions cho test_runner.py gọi
def emit_test_progress(report_id: int, progress: int, current_module: str, status: str) -> None:
    """Queue test progress update (non-blocking)."""
    queue_emit(report_id, "progress", {
        "progress": progress,
        "current_module": current_module,
        "status": status,
    })


def emit_test_complete(report_id: int, score: int, url: str) -> None:
    """Queue test completion event."""
    queue_emit(report_id, "complete", {
        "score": score,
        "url": url,
        "message": "Test hoàn thành!",
    })


def emit_test_error(report_id: int, error: str) -> None:
    """Queue test error event."""
    queue_emit(report_id, "error", {
        "error": error,
    })
