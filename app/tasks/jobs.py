import time
import logging
import json
from typing import Any, Dict, Optional
from rq import get_current_job

# Configure structured logging
logger = logging.getLogger(__name__)

def _update_job_state(status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> None:
    """
    Updates the job status, result, and error keys in Redis.
    Uses the Redis connection attached to the current RQ job context.
    """
    job = get_current_job()
    if not job:
        logger.warning("No RQ job context found. Cannot update state.")
        return

    redis_conn = job.connection
    job_id = job.id

    redis_conn.set(f"job:{job_id}:status", status)

    if result is not None:
        redis_conn.set(f"job:{job_id}:result", json.dumps(result))

    if error is not None:
        redis_conn.set(f"job:{job_id}:error", error)


def process_task(payload: dict[str, Any]) -> dict[str, Any]:
    """Generic task processing simulation."""
    _update_job_state("running")
    try:
        logger.info(f"Starting process_task with payload: {payload}")
        time.sleep(5)
        logger.info("Finished process_task")
        
        result = {"status": "success", "task": "process_task", "processed_data": payload}
        _update_job_state("done", result=result)
        return result
    except Exception as e:
        _update_job_state("failed", error=str(e))
        raise

def send_email_mock(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulates an IO-bound email sending task."""
    _update_job_state("running")
    try:
        target_email = payload.get("to", "unknown@example.com")
        logger.info(f"Starting send_email_mock for recipient: {target_email}")
        time.sleep(2)
        logger.info(f"Finished send_email_mock for recipient: {target_email}")
        
        result = {"status": "success", "task": "send_email", "delivered_to": target_email}
        _update_job_state("done", result=result)
        return result
    except Exception as e:
        _update_job_state("failed", error=str(e))
        raise

def resize_image_mock(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulates a CPU/IO-bound image resizing task."""
    _update_job_state("running")
    try:
        dimensions = payload.get("dimensions", "800x600")
        logger.info(f"Starting resize_image_mock to target dimensions: {dimensions}")
        time.sleep(3)
        logger.info(f"Finished resize_image_mock to target dimensions: {dimensions}")
        
        result = {"status": "success", "task": "resize_image", "dimensions": dimensions}
        _update_job_state("done", result=result)
        return result
    except Exception as e:
        _update_job_state("failed", error=str(e))
        raise
TASK_ROUTER = {
    "generic": process_task,
    "send_email": send_email_mock,
    "resize_image": resize_image_mock,
}