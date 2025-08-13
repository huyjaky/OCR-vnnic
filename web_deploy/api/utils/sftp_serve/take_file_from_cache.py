import paramiko
import os
from tqdm import tqdm
from types_ocr.sftp_account import sftp_account
import pypdf


def take_file_from_cache(
    folder_remote_save_path: str,
    folder_local_path: str,
    account: sftp_account,
    folder_remote_path_when_error: str,
    folder_local_path_when_error: str,
    model_index: int,
) -> bool:
    """
    Function to take a file from server using SFTP after taking it from cache
    that file will be removed from cache
    :param folder_remote_save_path: Remote path where the file will be uploaded.
    :param folder_local_path: Local path where the file is saved.
    :param account: SFTP account details containing hostname, port, username, and password.
    :param folder_remote_save_path_when_error: Remote path where the file will be uploaded when
    an error occurs.
    """

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            account.hostname, account.port, account.username, account.password
        )
        sftp_client = ssh_client.open_sftp()
        print("Connected to the server successfully.")

        file_list = sftp_client.listdir(folder_remote_save_path)

        print("Starting get file from cache serve---")
        # NOTE: checking the folder have a new file after 5 minutes
        # set timer right here
        file_list = sftp_client.listdir(folder_remote_save_path)

        # prevent complile new progress bar when no new file
        processer_bar = tqdm(file_list, desc="Downloading files", position=0)

        if len(file_list) != 0:
            for file_name in file_list:
                if (
                    file_name.endswith(".pdf") and "error_" not in file_name
                ):  # ignore error files
                    processer_bar.set_description(f"Downloading {file_name}")

                    remote_file_path = os.path.join(folder_remote_save_path, file_name)
                    local_file_path = os.path.join(folder_local_path, file_name)

                    file_remote_path_when_error = os.path.join(
                        folder_remote_path_when_error, "pdf", file_name
                    )

                    # Download the file from the remote server to the local path
                    sftp_client.get(remote_file_path, local_file_path)

                    sftp_client.remove(
                        remote_file_path
                    )  # Remove the file from remote cache

                    # WARNING: Remove the PDF file if it has more than 7 pages
                    # as well as checking the file PDF file is not corrupted
                    reader = pypdf.PdfReader(local_file_path)
                    if len(reader.pages) > 5:
                        print(
                            f"File {file_name} has more than 7 pages, removing from cache."
                        )

                        sftp_client.put(
                            localpath=local_file_path,
                            remotepath=file_remote_path_when_error,
                        )

                        # NOTE: Put log file to remote server
                        # Write the error message to a log file on the remote server
                        with open(
                            os.path.join(
                                folder_local_path_when_error,
                                f"model_{model_index}_{file_name.replace('.pdf', '.log')}",
                            ),
                            "w",
                        ) as error_file:
                            error_file.write(
                                f"Error in model {model_index}:\n {file_name} \n Has more than 7 pages \n"
                            )

                        sftp_client.put(
                            localpath=os.path.join(
                                folder_local_path_when_error,
                                f"model_{model_index}_{file_name.replace('.pdf', '.log')}",
                            ),
                            remotepath=os.path.join(
                                folder_remote_path_when_error,
                                "log",
                                file_name.replace(".pdf", ".log"),
                            ),
                        )  # Upload the error log file

                        os.remove(local_file_path)

                    processer_bar.update()

                else:
                    print(
                        "No new files found in the remote folder. Retrying in 5 minutes..."
                    )
            print("Successfull")

    except pypdf.errors.PdfReadError:  # pyright: ignore
        os.remove(local_file_path)  # pyright: ignore
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
    return True


if __name__ == "__main__":
    # WARNING: This script is for testing purposes only.
    # python -m upload_file_pdf
    from dotenv import load_dotenv

    load_dotenv()
    # Example usage
    account = sftp_account(
        hostname=str(os.getenv("HOSTNAME_SSH")),
        port=int(os.getenv("PORT_SSH", "22")),
        username=str(os.getenv("USERNAME_SSH")),
        password=str(os.getenv("PASSWORD_SSH")),
    )
    timeout = int(os.getenv("TIMEOUT_SFTP", "5"))
    folder_remote_path = str(os.getenv("REMOTE_CACHE_PATH"))
    folder_local_path = str(os.getenv("LOCAL_CACHE_PATH"))
    take_file_from_cache(
        folder_remote_save_path=folder_remote_path,
        folder_local_path=folder_local_path,
        account=account,
    )
