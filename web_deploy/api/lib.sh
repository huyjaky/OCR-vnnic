conda activate OCR 
uv pip install -U vllm --torch-backend=cu128 
uv pip install unsloth unsloth_zoo bitsandbytes
uv pip install -U xformers --index-url https://download.pytorch.org/whl/cu128
uv pip install -U triton==3.3.1
uv pip install -r api/requirements.txt
