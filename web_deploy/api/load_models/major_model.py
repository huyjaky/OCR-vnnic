from unsloth import FastModel
from unsloth.chat_templates import get_chat_template
from transformers import TextStreamer
import os
from utils.prompt_cached import get_prompt
from dotenv import load_dotenv
from json_repair import json_repair
import torch

load_dotenv()


# cofigure PyTorch to use 3 threads for both main and interop
# torch.set_num_threads(3)
# torch.set_num_interop_threads(3)

# construct variables
MAX_SEQ_LENGTH = int(os.getenv("MAX_SEQ_LENGTH"))
MODEL_PATH = str(os.getenv("MODEL_PATH"))
CACHE_PATH = str(os.getenv("CACHE_PATH"))


def load_model_and_tokenizer():
    # load model and tokenizer
    model, tokenizer = FastModel.from_pretrained(
        model_name=MODEL_PATH,
        max_seq_length=MAX_SEQ_LENGTH,
        load_in_8bit=True,
        load_in_4bit=False,
    )
    torch.compile(model)
    return model, tokenizer


def read_txt(file_path: str) -> str:
    """Read the content of a text file .txt."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def gen_json(model, tokenizer):
    """Generate JSON from Markdown content using the model and tokenizer."""
    markdown_text = read_txt(os.path.join(CACHE_PATH, "md_cached.txt"))
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
        **tokenizer([prompt], return_tensors="pt").to("cuda"),
        max_new_tokens=MAX_SEQ_LENGTH,
        temperature=0.2,
        top_p=0.95,
        top_k=64,
        num_beams=1,
        do_sample=True,
        streamer=TextStreamer(tokenizer, skip_prompt=True),
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
        json_output["MoTaChungTaiSan"] = None

    return json_output
