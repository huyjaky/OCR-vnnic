import paramiko
from types_ocr.sftp_account import SftpAccount
import os
import json


def push_file_to_remote_when_error(
    local_save_path: str,
    account: SftpAccount,
    file_name: str,
    error_remote_path: str,
    error_local_path: str,
    error_message: str,
    model_index: int,
    generated_output: dict | None,
):
    """
    Function to upload a file to a remote server using SFTP.
    :param local_save_path: Local path where the file is saved.
    :param folder_remote_save_path: Remote path where the file will be uploaded.
    :param account: SFTP account details containing hostname, port, username, and password.
    :param file_name: Name of the file to be uploaded.
    """
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            account.hostname, account.port, account.username, account.password
        )
        sftp_client = ssh_client.open_sftp()
        print("Connected to the server successfully.")

        # NOTE: Put original file to remote server
        sftp_client.put(
            localpath=os.path.join(local_save_path, file_name + ".pdf"),
            remotepath=os.path.join(error_remote_path, "pdf", file_name + ".pdf"),
        )  # Upload the file

        # NOTE: Put log file to remote server
        # Write the error message to a log file on the remote server
        with open(
            os.path.join(
                error_local_path,
                f"model_{model_index}_{file_name + '.log'}",
            ),
            "w",
        ) as error_file:
            error_file.write(
                f"Error in model: {model_index}\n File name: {file_name}\n JSON: \n{json.dumps(generated_output, indent=4, ensure_ascii=False)} \n\n\n ERROR: \n {error_message}\n"
            )

        sftp_client.put(
            localpath=os.path.join(
                error_local_path,
                f"model_{model_index}_{file_name + '.log'}",
            ),
            remotepath=os.path.join(
                error_remote_path,
                "log",
                f"model_{model_index}_{file_name + '.log'}",
            ),
        )  # Upload the error log file

        print("File error uploaded successfully.")

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
