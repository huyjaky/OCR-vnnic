from fastapi import FastAPI
from load_models.major_model import load_model_and_tokenizer, gen_json


model, tokenizer = load_model_and_tokenizer()

app = FastAPI()

@app.get("/extracted", response_model=dict)
def insert_tieu_chi():
    print("Generating JSON from Markdown...")
    generated_output = gen_json(model, tokenizer)
    print("-"*60)
    return {"response": generated_output}
