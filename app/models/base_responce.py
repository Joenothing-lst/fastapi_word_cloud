from typing import Union, Any

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    code: int = 0
    msg: str = 'success'
    data: Union[str, Any] = {}