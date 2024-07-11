from pydantic import BaseModel


class LambdaResponseBase(BaseModel):
    status_code: int
    message: str
