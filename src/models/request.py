"""Request"""

import pydantic


class Request(pydantic.BaseModel):
    user: str
    country: str
    language: str
