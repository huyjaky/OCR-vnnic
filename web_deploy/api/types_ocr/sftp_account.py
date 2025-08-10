from pydantic import BaseModel

class sftp_account(BaseModel):
    hostname: str
    port: int
    username: str
    password: str


