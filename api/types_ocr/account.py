from pydantic import BaseModel
from .dtb_account import DtbAccount
from .sftp_account import SftpAccount

class Account(BaseModel):
    sftp_account: SftpAccount
    dtb_account: DtbAccount
