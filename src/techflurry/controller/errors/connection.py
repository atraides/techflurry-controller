# -*- coding: utf-8 -*-

"""Library of error classes used with the connection management."""

# MIT License (see LICENSE)
# Author: Dániel Hagyárossy <d.hagyarossy@sapstar.eu>
# Author: László Béres <laszloberes@hotmail.hu>


from typing import Any, List


class TFConnectionFailed(Exception):
    """TFConnectionFailed class is used to raise connection failed errors.

    Methods:
       __init__(self, error)

    """

    def __init__(self, rc: int, *args: List[Any]):
        """Construct the TFConnectionFailed class.

        Args:
            rc: Return code of the connection failure
            *args: Other exception arguments

        """
        super().__init__(*args)
        self.rc = rc

    def __repr__(self) -> str:
        """Return text representation of the module.

        Returns:
            Text representation of the exception object.

        """
        return (
            f"<{self.__class__.__name__}: "
            f"Error occurred during connection to the server."
            f" ReturnCode = {self.rc}>"
        )

    __str__ = __repr__
