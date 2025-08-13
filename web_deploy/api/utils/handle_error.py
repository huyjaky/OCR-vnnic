from .sftp_serve.push_file_to_remote_when_error import push_file_to_remote_when_error
from querys.insert_2_dtb import insert_records_from_error


def handle_error(
    folder_local_path: str,
    file_name: str,
    account,
    folder_remote_path_when_error: str,
    folder_local_path_when_error: str,
    e: Exception,
    index: int,
    generated_output: dict | None,
):
    push_file_to_remote_when_error(
        local_save_path=folder_local_path,
        file_name=file_name,
        account=account,
        error_remote_path=folder_remote_path_when_error,
        error_local_path=folder_local_path_when_error,
        error_message=f"{e}",
        model_index=index,
        generated_output=generated_output,
    )

    insert_records_from_error(
        error_str=e,
        file_name=file_name,
        is_check=False,
    )
