import paramiko
import os
from tqdm import tqdm
from types_ocr.sftp_account import sftp_account


def take_file_from_cache(
    folder_remote_path: str,
    folder_local_path: str,
    account: sftp_account,
) -> bool:
    """
    Function to take a file from server using SFTP after taking it from cache
    that file will be removed from cache
    :param folder_remote_path: Path to the remote folder on the server
    :param folder_local_path: Path to the local folder where the file will be saved
    """

    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            account.hostname, account.port, account.username, account.password
        )
        sftp_client = ssh_client.open_sftp()
        print("Connected to the server successfully.")

        file_list = sftp_client.listdir(folder_remote_path)

        print("Starting get file from cache serve---")
        file_list = sftp_client.listdir(folder_remote_path)

        # prevent complile new progress bar when no new file
        processer_bar = tqdm(file_list, desc="Downloading files", position=0)

        if len(file_list) != 0:
            for file_name in file_list:
                processer_bar.set_description(f"Downloading {file_name}")

                remote_file_path = os.path.join(folder_remote_path, file_name)
                local_file_path = os.path.join(folder_local_path, file_name)

                # Download the file from the remote server to the local path
                sftp_client.get(remote_file_path, local_file_path)

                # Remove the file from the remote server after downloading
                sftp_client.remove(remote_file_path)

                processer_bar.update()

        else:
            print("\nNo new files found in the remote folder. Retrying in 5 minutes...")

            # print("Waiting for new files to be added to the cache server...")

            # timeout_bar = tqdm(
            #     range(timeout * 60), desc="Waiting for new files", unit="seconds"
            # )
            # for _ in range(timeout * 60):
            #     timeout_bar.update(1)
            #     time.sleep(1)  # Sleep for 1 second in each iteration

        print("Successfull")

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
        folder_remote_path=folder_remote_path,
        folder_local_path=folder_local_path,
        account=account,
    )
