from typing import Dict, Any, Tuple
import logging

from flask import jsonify, current_app, request

from app.api import api_bp
from app.tasks.jobs import TASK_ROUTER


logger = logging.getLogger(__name__)




@api_bp.route("/ping", methods=["GET"])
def ping() -> Tuple[Dict[str, Any], int]:
    """
    Health check endpoint to verify the API is running.
    """
    return jsonify({
        "status": "success",
        "message": "pong"
    }), 200


@api_bp.route("/tasks", methods=["POST"])
def create_task() -> Tuple[Dict[str, Any], int]:
    """
    Enqueues a background task based on the provided task_type.
    """
    payload = request.get_json(silent=True) or {}
    task_type = payload.get("task_type", "generic")

    # Validate task type
    if task_type not in TASK_ROUTER:
        return jsonify({
            "error": "Invalid task_type.",
            "allowed_types": list(TASK_ROUTER.keys())
        }), 400

    # Get shared queue from app extensions
    task_queue = current_app.extensions.get("rq_queue")
    if task_queue is None:
        logger.error("RQ queue not initialized.")
        return jsonify({
            "error": "RQ queue not initialized."
        }), 500

    task_func = TASK_ROUTER[task_type]

    try:
        job = task_queue.enqueue(task_func, payload)

        # Initialize status tracking in Redis
        redis_conn = task_queue.connection
        redis_conn.set(f"job:{job.id}:status", "pending")

        logger.info(
            "Enqueued job %s of type '%s'",
            job.id,
            task_type,
        )

        return jsonify({
            "job_id": job.id,
            "status": "pending",
            "task_type": task_type,
            "message": "Task successfully enqueued."
        }), 202

    except Exception:
        logger.exception("Failed to enqueue task.")

        return jsonify({
            "error": "Internal server error while enqueueing task."
        }), 500