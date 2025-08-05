import paramiko
from types_ocr.sftp_account import sftp_account  # pyright: ignore

# load_dotenv()

# hostname = str(
#     os.getenv("HOSTNAME_SSH", "103.82.23.137")
# )  # Default to localhost if not set
# port = int(os.getenv("PORT_SSH", "22"))  # Default port is 22 if not set
# username = str(os.getenv("USERNAME_SSH", "sshlogin"))  # Default username if not set
# password = str(
#     os.getenv("PASSWORD_SSH", "SSH@#server@123")
# )  # Default password if not set


# remote_path = (
#     "C:/Nga/PHAN-MEM/DKBaoDam/" + file_path.split("/")[-1]
# )  # Remote path where the file will be uploaded


def push_file_to_remote(file_path: str, remote_path: str, account: sftp_account):
    """
    Function to upload a file to a remote server using SFTP.
    # Path to the file to be uploaded
    # NOTE: This should be the path where the file is saved after processing
    # For example, after converting PDF to JSON
    """
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(
            account.hostname, account.port, account.username, account.password
        )
        sftp_client = ssh_client.open_sftp()
        print("Connected to the server successfully.")
        sftp_client.put(file_path, remote_path)
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
