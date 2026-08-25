"""Asynchronous Background Task Manager for Long-Running Sourcing & Import Jobs."""

from __future__ import annotations

import concurrent.futures
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("async_task_service")


class AsyncTaskManager:
    """Thread-safe background task manager for ATS dashboard operations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AsyncTaskManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._futures: Dict[str, concurrent.futures.Future] = {}

    def submit_task(
        self,
        task_name: str,
        fn: Callable,
        *args,
        **kwargs,
    ) -> str:
        """Submit a function to run in a background thread without blocking the UI."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task_info = {
            "task_id": task_id,
            "name": task_name,
            "status": "RUNNING",
            "progress": 0,
            "result": None,
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }
        self._tasks[task_id] = task_info

        def _wrapper():
            try:
                res = fn(*args, *kwargs)
                self._tasks[task_id]["status"] = "COMPLETED"
                self._tasks[task_id]["progress"] = 100
                self._tasks[task_id]["result"] = res
            except Exception as e:
                logger.error(f"Background task {task_id} failed: {e}")
                self._tasks[task_id]["status"] = "FAILED"
                self._tasks[task_id]["error"] = str(e)
            finally:
                self._tasks[task_id]["completed_at"] = datetime.now(timezone.utc).isoformat()

        future = self._executor.submit(_wrapper)
        self._futures[task_id] = future
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a background task."""
        return self._tasks.get(task_id)

    def list_tasks(self, limit: int = 20) -> List[Dict[str, Any]]:
        """List recent tasks newest first."""
        all_tasks = list(self._tasks.values())
        return list(reversed(all_tasks))[:limit]


DEFAULT_TASK_MANAGER = AsyncTaskManager()
