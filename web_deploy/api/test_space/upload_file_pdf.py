from dotenv import load_dotenv
import paramiko
import os
from tqdm import tqdm

load_dotenv()


hostname = str(
    os.getenv("HOSTNAME_SSH", "103.82.23.137")
)  # Default to localhost if not set
port = int(os.getenv("PORT_SSH", "22"))  # Default port is 22 if not set
username = str(os.getenv("USERNAME_SSH", "sshlogin"))  # Default username if not set
password = str(
    os.getenv("PASSWORD_SSH", "SSH@#server@123")
)  # Default password if not set

file_path = "./cache/pdf_cached.pdf"
rm_path = "C:/Nga/PHAN-MEM/DKBaoDam/"
lc_path = "/home/duckq1u/Documents/pdf_ocr_for_testing/pdf_cache/"

remote_path = (
    rm_path + file_path.split("/")[-1]
)  # Remote path where the file will be uploaded
try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(hostname, port, username, password)
    sftp_client = ssh_client.open_sftp()

    # /mnt/SSD-playing games/Workspace/obsidian_aio/Notebook/Dự án/OCR/fine-tunning
    for pdf_file in tqdm(os.listdir(lc_path)):
        # if list(pdf_file.strip())[0] != "2":
        #     continue

        if pdf_file.endswith(".pdf"):
            file_path = os.path.join(
                lc_path,
                pdf_file,
            )
            remote_path = os.path.join(rm_path, pdf_file)
            sftp_client.put(file_path, remote_path)
            print(f"File {pdf_file} uploaded successfully.")


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
