# %%
from unsloth import FastModel

model, tokenizer = FastModel.from_pretrained(
    model_name="unsloth/gemma-3-4b-it",
    max_seq_length=8096,  # Choose any for long context!
    load_in_4bit=True,  # 4 bit quantization to reduce memory
    load_in_8bit=False,  # [NEW!] A bit more accurate, uses 2x memory
    full_finetuning=False,  # [NEW!] We have full finetuning now!
    # token = "hf_...", # use one if using gated models
)

# %%

# %% [markdown]
# ### Fine-tunning Optionals

# %%
model = FastModel.get_peft_model(
    model,
    finetune_vision_layers=False,  # Turn off for just text!
    finetune_language_layers=True,  # Should leave on!
    finetune_attention_modules=True,  # Attention good for GRPO
    finetune_mlp_modules=True,  # SHould leave on always!
    r=8,  # Larger = higher accuracy, but might overfit
    lora_alpha=8,  # Recommended alpha == r at least
    lora_dropout=0,
    bias="none",
    random_state=3407,
)

# %% [markdown]
# ## Form maker

# %%
from unsloth.chat_templates import get_chat_template

tokenizer = get_chat_template(
    tokenizer,
    chat_template="gemma-3",
)

# %% [markdown]
# #### Load dataset

# %%

import os
import json
from datasets import Dataset
# Loop on folder for read folders


def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


def read_json(file_path: str, is_schema=False) -> dict:
    if is_schema:
        with open(file_path, "r", encoding="utf-8") as file:
            content = json.load(file)
            content = json.dumps(content, ensure_ascii=False, indent=2)
        return content

    with open(file_path, "r", encoding="utf-8") as file:
        content = json.load(file)
        content = json.dumps(content[0]["output"], ensure_ascii=False, indent=2)
    return content


# follow this format schema below:\n <schema>{str(read_json(schema_path))}\n</schema> </requirement>
def load_dataset() -> list:
    dataset = []
    path = "/home/duckq1u/Downloads/FIL/dataset/Training"
    schema_path = "/home/duckq1u/Downloads/FIL/dataset/schema.json"

    for folder_name in os.listdir(path):
        for file_name in os.listdir(os.path.join(path, folder_name)):
            file_path = os.path.join(path, folder_name, file_name.split(".")[0])

            conversation = {
                "conversations": [
                    {
                        "from": "user",
                        "content": f"<context>{str(read_txt(file_path=file_path + '.txt'))}</context>\n<requirement>\n Return information extracted from Markdown as JSON for me </requirement>\n\n\n",
                        "role": "user",
                    },
                    {
                        "content": f"{str(read_json(file_path=file_path + '.json'))}\n",
                        "role": "assistant",
                    },
                ]
            }
            # print(type(read_json(file_path=file_path+'.json')))
            # break
            dataset.append(conversation)
    return dataset


def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [
        tokenizer.apply_chat_template(
            convo, tokenize=False, add_generation_prompt=False
        ).removeprefix("<bos>")
        for convo in convos
    ]
    return {
        "text": texts,
    }


ds = Dataset.from_list(load_dataset()).train_test_split(test_size=0.1)
dataset = ds["train"].map(formatting_prompts_func, batched=True)
test_dataset = ds["test"].map(formatting_prompts_func, batched=True)

# %% [markdown]
# ## Config trainer

# %%
from trl import SFTTrainer, SFTConfig

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    eval_dataset=test_dataset,  # Can set up evaluation!
    args=SFTConfig(
        dataset_text_field="text",
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,  # Use GA to mimic batch size!
        warmup_steps=5,
        num_train_epochs=3,
        # max_steps = 30,
        learning_rate=2e-4,  # Reduce to 2e-5 for long training runs
        logging_steps=1,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="linear",
        seed=3407,
        report_to="wandb",  # Use this for WandB etc
        eval_strategy="steps",
        save_steps=20,
        eval_steps=1,
        save_total_limit=1,  # Save only the last checkpoint
    ),
)

# %% [markdown]
#  Unsloth's train_on_completions method to only train on the assistant outputs and ignore the loss on the user's inputs. This helps increase accuracy of finetunes!

# %%
from unsloth.chat_templates import train_on_responses_only

trainer = train_on_responses_only(
    trainer,
    instruction_part="<start_of_turn>user\n",
    response_part="<start_of_turn>model\n",
)

# %% [markdown]
# test decoder

# %%
print(tokenizer.decode(trainer.train_dataset[100]["input_ids"]))

# %% [markdown]
# Result from batch

# %%
print(
    tokenizer.decode(
        [
            tokenizer.pad_token_id if x == -100 else x
            for x in trainer.train_dataset[100]["labels"]
        ]
    ).replace(tokenizer.pad_token, " ")
)

# %%
trainer_stats = trainer.train()

# %%
model.save_pretrained("gemma-3-Markdown2Json-ver3")  # Local saving
tokenizer.save_pretrained("gemma-3-Markdown2Json-ver3")  # Local saving

model.push_to_hub(
    "Duckq/gemma-3-Markdown2Json-ver3", token="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"
)  # Online saving
tokenizer.push_to_hub(
    "Duckq/gemma-3-Markdown2Json-ver3", token="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"
)  # Online saving
dataset.push_to_hub(
    "Duckq/OCR_dataset", token="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"
)  # Online saving

# %% [markdown]
# ## Inference model

# %%
if True:
    from unsloth import FastModel

    model, tokenizer = FastModel.from_pretrained(
        model_name="/home/duckq1u/Documents/obsidian_aio/Notebook/Dự án/OCR anh hiếu/OCR/gemma-3-Markdown2Json-ver2",  # YOUR MODEL YOU USED FOR TRAINING
        max_seq_length=4096,
        load_in_8bit=True,
        load_in_4bit=False,
    )


# %%
def read_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content


md = read_txt(
    "/home/duckq1u/Documents/obsidian_aio/Notebook/Dự án/OCR anh hiếu/OCR/1597891480.txt"
)

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"<context>{str(md)}</context>\nReturn information extracted from Markdown as JSON",
            }
        ],
    }
]


text = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,  # Must add for generation
)

from transformers import TextStreamer

_ = model.generate(
    **tokenizer([text], return_tensors="pt").to("cuda"),
    max_new_tokens=5069,  # Increase for longer outputs!
    # Recommended Gemma-3 settings!
    temperature=0.4,
    top_p=0.95,
    top_k=64,
    streamer=TextStreamer(tokenizer, skip_prompt=True),
)
