import os


def ensure_remote_dir_exists(sftp_client, list_dir: list[str], remote_directory: str):
    """
    Ensure that a remote directory exists on the SFTP server.
    """
    current_path = remote_directory
    for dir_name in list_dir:
        current_path = os.path.join(current_path, dir_name)
        try:
            sftp_client.stat(current_path)  # kiểm tra xem thư mục có tồn tại không
        except FileNotFoundError:
            sftp_client.mkdir(current_path)
    return current_path
