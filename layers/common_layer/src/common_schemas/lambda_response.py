from pydantic import BaseModel


class LambdaResponseBase(BaseModel):

    class Config:
        populate_by_name = True

    status_code: int
    message: str
