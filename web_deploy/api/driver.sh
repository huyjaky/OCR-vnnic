# uv pip install -U vllm --torch-backend=cu128 
pip install uv 
uv pip install unsloth unsloth_zoo bitsandbytes "fastapi[standard]"
# uv pip install -U xformers --index-url https://download.pytorch.org/whl/cu128
# uv pip install -U triton==3.3.1
# cd api 
uv pip install -r requirements.txt

curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main" | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools
sudo apt-get install -y unixodbc-dev

