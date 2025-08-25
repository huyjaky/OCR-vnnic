from pydantic import BaseModel

class DtbAccount(BaseModel):
    server: str
    database: str
    uid: str
    password: str
