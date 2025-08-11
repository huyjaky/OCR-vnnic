import paramiko
from types_ocr.sftp_account import sftp_account  # pyright: ignore
from datetime import datetime
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


def push_file_to_remote_save_path(
    local_save_path: str,
    # folder_remote_get_path: str,
    folder_remote_save_path: str,
    account: sftp_account,
    datetime_folder: str,
    file_name: str,
):
    """
    Function to upload a file to a remote server using SFTP.
    :param local_save_path: Local path where the file is saved.
    :param folder_remote_save_path: Remote path where the file will be saved.
    :param account: SFTP account details.
    :param datetime_folder: Date and time folder to organize files on the remote server.
    :param file_name: Name of the file to be uploaded.
    """
    try:
        file_name = f"{file_name}.pdf"
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            account.hostname, account.port, account.username, account.password
        )
        sftp_client = ssh_client.open_sftp()
        print("Connected to the server successfully.")

        # NOTE: Ensure the file_path is absolute and save as datetime levels
        dt = datetime.fromisoformat(
            datetime_folder
        )  # Convert string to datetime object

        list_dir = [str(dt.year), str(dt.month), str(dt.day)]

        remote_save_path = ensure_remote_dir_exists(
            sftp_client, list_dir, folder_remote_save_path
        )  # Ensure the remote directory exists

        sftp_client.put(
            localpath=os.path.join(local_save_path, file_name),
            remotepath=os.path.join(remote_save_path, file_name),
        )  # Upload the file

        # sftp_client.remove(
        #     os.path.join(folder_remote_get_path, file_name.replace(".txt", ".pdf"))
        # )  # Remove the file from the remote server after uploading
        print("File uploaded successfully.")

    except paramiko.AuthenticationException:
        print("Authentication failed. Check your username and password or keys.")
    except paramiko.SSHException as e:
        print(f"SSH connection error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the SFTP and SSH connections
        if "sftp_client" in locals() and sftp_client:  # pyright: ignore
            sftp_client.close()
        if "ssh_client" in locals() and ssh_client:  # pyright: ignore
            ssh_client.close()
