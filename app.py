import os
import logging

from flask import Flask, request
from dataclasses import asdict
from controller import Controller, ConflictError, NotFoundError
from werkzeug.exceptions import BadRequest
from http import HTTPStatus
from guest import Guest

app = Flask(__name__)

API_VERSION = "/v1"

logging.basicConfig(level=logging.DEBUG if os.getenv(f"DEBUG", False) else logging.INFO)
logger = logging.getLogger(__name__)

controller = Controller(os.getenv("FILENAME", "./database.csv"))


@app.errorhandler(BadRequest)
def handle_bad_request(e: BadRequest) -> tuple:
    """_summary_

    Args:
        e (BadRequest): BadRequest exception

    Returns:
        tuple: A tuple of type <error_message>, <status_code>
    """
    return {
        "message": "bad request!",
        "status_code": HTTPStatus.BAD_REQUEST,
    }, HTTPStatus.BAD_REQUEST


@app.get(f"{API_VERSION}/guest")
def get_all() -> list:
    """Get all guests

    Returns:
        list: List of guests
    """
    return list(map(lambda guest: asdict(guest), controller.get_all()))


@app.get(f"{API_VERSION}/guest/<id>")
def get(id: str) -> dict:
    """Get a guest

    Args:
        id (str): The guest ID

    Returns:
        dict: The requested guest
    """
    try:
        data = asdict(controller.get(id))
    except NotFoundError as e:
        return {
            "message": str(e),
            "status_code": HTTPStatus.NOT_FOUND,
        }, HTTPStatus.NOT_FOUND
    return data


@app.post(f"{API_VERSION}/guest")
def create() -> None:
    """Create a new guest"""
    data: dict = request.get_json()
    guest: Guest = Guest(
        data.get("name", ""), data.get("last_name", ""), data.get("plus_one", False)
    )
    try:
        logger.debug("saving guest to database")
        controller.save(guest)
    except ConflictError as e:
        message: str = f"error saving guest to database: {e}"
        logger.error(message)
        return {
            "message": message,
            "status_code": HTTPStatus.CONFLICT,
        }, HTTPStatus.CONFLICT

    return {"message": "successfully saved guest", "status_code": HTTPStatus.OK}


@app.delete(f"{API_VERSION}/guest/<id>")
def delete(id: str) -> None:
    """Deletes a guest

    Args:
        id (str): ID of the guest to be deleted
    """
    try:
        logger.debug("deleting guest with id %s", id)
        controller.delete(id)
    except Exception as e:
        message: str = f"error deleting guest: {e}"
        logger.error(message)
        return {
            "message": message,
            "status_code": HTTPStatus.INTERNAL_SERVER_ERROR,
        }, HTTPStatus.INTERNAL_SERVER_ERROR
    return {
        "message": f"successfully deleted guest with id {id}",
        "status_code": HTTPStatus.OK,
    }
