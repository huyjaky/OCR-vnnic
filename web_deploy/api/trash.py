
import paramiko

hostname = "103.82.23.137"
port = 22
username = "sshlogin"
password = "SSH@#server@123"

remote_path = "C:/Nga/PHAN-MEM/DKBaoDam"

try:
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh_client.connect(hostname, port, username, password)

    sftp_client = ssh_client.open_sftp()
    print("Connected to the server successfully.")
    sftp_client.put("./trash.json", remote_path + "/trash.json")
    print("File uploaded successfully.")
except paramiko.AuthenticationException:
    print("Authentication failed. Check your username and password or keys.")
except paramiko.SSHException as e:
    print(f"SSH connection error: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Close the SFTP and SSH connections
    if "sftp_client" in locals() and sftp_client: # pyright: ignore
        sftp_client.close()
    if "ssh_client" in locals() and ssh_client: # pyright: ignore
        ssh_client.close()
