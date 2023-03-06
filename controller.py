"""The controller for the flask application.

The controller for the flask application, that is in charge of handling
the interaction with our database.

Typical usage example:
    my_controller = Controller(filename=my_file)
    my_controller.get(id=guest_id)
"""

import os
import logging
import pandas as pd

from dataclasses import dataclass, field
from os.path import exists
from typing import List
from pandas.errors import UndefinedVariableError
from guest import Guest


logger = logging.getLogger()
logger.setLevel(level=logging.DEBUG if os.getenv(f"DEBUG", False) else logging.INFO)


class ConflictError(Exception):
    def __init__(self, id: str):
        super().__init__(f"Guest with id {id} already exists")


class NotFoundError(Exception):
    def __init__(self, id: str):
        super().__init__(f"Guest with id {id} was not found")


@dataclass
class Controller:
    """The Controller for interacting with the database.

    The Controller class interacts with the database. It has methods for
    getting a single Guest, getting all the guests, and saving and deleting
    a Guest.

    Attributes:
        filename (str): Path to the file to be used for storing the database.
            This can be an absolute or a relative path.
    """

    filename: str
    _df: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        """Initializes the private pd.DataFrame of the instance"""
        if exists(self.filename):
            self._df = pd.read_csv(filepath_or_buffer=self.filename)
            return
        self._df = pd.DataFrame()

    def _commit(self) -> None:
        """Commits the DataFrame in the csv file"""
        self._df[["id", "name", "last_name", "plus_one"]].to_csv(
            self.filename, index=False
        )

    def get_all(self) -> List[Guest]:
        """Retrieve the full list of guests from the database

        Returns:
            List[Guest]: List of guests
        """
        return list(
            map(
                lambda record: Guest(
                    record.get("name", ""),
                    record.get("last_name", ""),
                    record.get("plus_one", False),
                ),
                self._df.to_dict("records"),
            )
        )

    def get(self, id: str) -> Guest:
        """Retrieve a single guest from the database

        Args:
            id (str): ID of the guest to be retrieved

        Raises:
            NotFoundError: Error when guest is not found

        Returns:
            Guest: Guest returned from the database
        """
        try:
            query_data = self._df.query("id == @id")
        except UndefinedVariableError:
            raise NotFoundError(id)
        if query_data.size <= 0:
            raise NotFoundError(id)
        data: dict = query_data.iloc[0].to_dict()
        return Guest(
            data.get("name", ""), data.get("last_name", ""), data.get("plus_one", False)
        )

    def save(self, guest: Guest) -> None:
        """Store a guest in the database

        Args:
            guest (Guest): The guest to store in the database
        """
        try:
            if self._df.query("id == @guest.id").size:
                raise ConflictError(guest.id)
        except UndefinedVariableError:
            pass
        self._df = pd.concat(
            [
                self._df,
                pd.DataFrame(
                    data=[
                        {
                            "id": guest.id,
                            "name": guest.name,
                            "last_name": guest.last_name,
                            "plus_one": guest.plus_one,
                        }
                    ]
                ),
            ]
        )
        self._commit()

    def delete(self, id: str) -> None:
        """Deletes the guest with id <id>

        Args:
            id (str): ID of the guest to be deleted
        """
        try:
            self._df = self._df[self._df["id"] != id]
        except KeyError:
            raise NotFoundError(id)
        self._commit()
