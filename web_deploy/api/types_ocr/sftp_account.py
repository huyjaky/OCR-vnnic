from pydantic import BaseModel


class SftpAccount(BaseModel):
    hostname: str
    port: int
    username: str
    password: str
    timeout: int
    banner_timeout: int
