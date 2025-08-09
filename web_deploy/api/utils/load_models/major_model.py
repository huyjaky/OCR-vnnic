from unsloth import FastModel
from unsloth.chat_templates import get_chat_template
import os
from utils.prompt_cached import get_prompt
from dotenv import load_dotenv
from json_repair import json_repair
import torch

load_dotenv()

# cofigure PyTorch to use 3 threads for both main and interop
# torch.set_num_threads(3)
# torch.set_num_interop_threads(3)


def load_model_and_tokenizer(model_path: str, max_seq_length: int, cuda_index: int = 0):
    # load model and tokenizer
    model, tokenizer = FastModel.from_pretrained(
        model_name=model_path,
        max_seq_length=max_seq_length,
        load_in_4bit=False,
        load_in_8bit=False,
        device_map=f"cuda:{cuda_index}",
        use_cache=True,
    )

    model = torch.compile(
        model,
        mode="max-autotune",
        dynamic=False,
        backend="inductor",
    )

    return model, tokenizer


def read_txt(file_path: str) -> str:
    """Read the content of a text file .txt."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def gen_json(
    model,
    tokenizer,
    file_local_path: str,
    max_seq_length: int = 2048,
    cuda_index: int = 0,
) -> dict:
    """Generate JSON from Markdown content using the model and tokenizer."""
    markdown_text = read_txt(os.path.join(file_local_path))
    messages = [
        {"role": "system", "content": get_prompt()},
        {"role": "user", "content": f"\n**TÀI LIỆU MARKDOWN**:\n{markdown_text}"},
    ]
    tokenizer = get_chat_template(
        tokenizer,
        chat_template="llama-3.1",
    )

    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    outputs = model.generate(
        **tokenizer([prompt], return_tensors="pt").to(f"cuda:{cuda_index}"),
        max_new_tokens=max_seq_length,
        temperature=0.2,
        top_p=0.95,
        top_k=64,
        num_beams=1,
        do_sample=True,
        # streamer=TextStreamer(tokenizer, skip_prompt=True),
    )
    generated_output = tokenizer.batch_decode(outputs)[0]

    # Tách phần content từ assistant
    raw_text = (
        generated_output.strip()
        .split("<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n")[-1]
        .replace("\n<|eot_id|>", "")
    )

    # Parse JSON
    json_output = json_repair.repair_json(
        raw_text, ensure_ascii=False, return_objects=True
    )

    if "mô tả" and "tài sản" in markdown_text.lower():
        json_output["MoTaChungTaiSan"] = None  # pyright: ignore

    return json_output # pyright: ignore
