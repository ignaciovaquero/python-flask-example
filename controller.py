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
    filename: str
    df: pd.DataFrame = field(init=False)

    def __post_init__(self):
        if exists(self.filename):
            self.df = pd.read_csv(filepath_or_buffer=self.filename)
            return
        self.df = pd.DataFrame()

    def _commit(self) -> None:
        """Commits the DataFrame in the csv file"""
        self.df[["id", "name", "last_name", "plus_one"]].to_csv(
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
                self.df.to_dict("records"),
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
            query_data = self.df.query("id == @id")
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
            if self.df.query("id == @guest.id").size:
                raise ConflictError(guest.id)
        except UndefinedVariableError:
            pass
        self.df = pd.concat(
            [
                self.df,
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
        self.df = self.df[self.df["id"] != id]
        self._commit()
