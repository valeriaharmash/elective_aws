from pydantic import BaseModel


class DbCredential(BaseModel):
    host: str
    port: int
    password: str
    username: str
    database: str

    def get_db_url(self, dbms: str, dbms_driver: str) -> str:
        return f"{dbms}+{dbms_driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"


class TopicArnCredential(BaseModel):
    arn: str
