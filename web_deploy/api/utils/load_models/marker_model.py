from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered
import os
import torch
from dotenv import load_dotenv

load_dotenv()

torch.set_num_threads(3)  # Hoặc số luồng bạn muốn
torch.set_num_interop_threads(3)

# load marker for convert pdf to markdown
config = {
    "output_format": "markdown",
    "use_llm": False,
}

config_parser = ConfigParser(config)


def load_marker_model():
    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    return converter


path = str(os.getenv("CACHE_PATH"))


def get_text_from_pdf(converter, folder_local_path: str, file_name: str) -> dict:
    """Convert PDF to Markdown and save the text content."""
    rendered = converter(str(os.path.join(folder_local_path, file_name)))
    text, _, images = text_from_rendered(rendered)
    with open(
        os.path.join(folder_local_path, "md_cached.txt"),
        "w",
        encoding="utf-8",
    ) as f:
        f.write(text)
    return {"response": True}
