import json
import os
from datetime import datetime

from transformers import set_seed

from tqdm import tqdm

import torch

from transformers import AutoTokenizer, AutoModelForCausalLM

from utils import list_files_in_directory, create_message, parse_classification_response


# -----

SEED = 1111

MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"

HUGGINGFACE_TOKEN = "..."

# -----
# -----

INSTRUCTION = """
You are a classifier. Given a Comment, classify it into one of the following categories:

- Gratitude: A comment expressing gratitude, relief, or similar emotions.
- Action: A comment that includes awareness, a report, an urgent action, or similar prompts.
- Abuse: A comment indicating that scammers are engaging in hateful, abusive, fearful, or concerning activities.
- Anger: A comment showing that the user is frustrated or angry because they believe YouTube is not taking serious steps to block scam accounts.

Please provide the category name and a brief explanation for your classification in the following format:

Category: "..."
Explanation: "..."

Examples:

Comment: "Thank you so much for addressing this issue! I was really worried."
Category: "Gratitude"
Explanation: "The comment expresses gratitude and relief for addressing the issue."

Comment: "Everyone needs to report these scammers immediately!"
Category: "Action"
Explanation: "The comment is a call to action, urging others to report scammers
"""


# -----
# -----

current_date = datetime.now()
formatted_date = current_date.strftime("%Y-%m-%d_%H-%M-%S")

# -----
# -----

DIR_JSON_PATH = "datasets/youtube"

RES_PATH = f"./results/{formatted_date}/{DIR_JSON_PATH}"
if not os.path.exists(RES_PATH):
    os.makedirs(RES_PATH)

# -----
# -----

def load_model(model_id, hf_token=None):
    tokenizer = AutoTokenizer.from_pretrained(model_id, token=HUGGINGFACE_TOKEN)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        token = hf_token
    )

    return model, tokenizer


def do_analysis(model, instruction, tokenizer, dir_json_path, res_path):
    files = list_files_in_directory(dir_json_path)

    for file in tqdm(files, desc="Processing files"):
        filename = file.split("/")[-1]
        commented_results = []

        with open(file, 'r') as file:
            data = json.load(file)

        for comment_dict in tqdm(data, desc=f"Processing {filename}", leave=False):
            author_name = comment_dict["author_name"]
            author_comment = comment_dict["author_comment"]

            messages = create_message(instruction, author_comment)

            input_ids = tokenizer.apply_chat_template(
                messages,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(model.device)

            terminators = [
                tokenizer.eos_token_id,
                tokenizer.convert_tokens_to_ids("<|eot_id|>")
            ]

            outputs = model.generate(
                input_ids,
                max_new_tokens=256,
                eos_token_id=terminators,
                do_sample=False,
                temperature=1.0,
                top_p=0.9,
            )

            response = outputs[0][input_ids.shape[-1]:]

            decoded_response = tokenizer.decode(response, skip_special_tokens=True)

            result = parse_classification_response(decoded_response)

            commented_results.append({
                "author_name": author_name,
                "author_comment": author_comment,
                "result": result,
                "respose": decoded_response
            })
        
        output_filename = f"{res_path}/results-{filename}"
        with open(output_filename, "w") as f:
            json.dump(commented_results, f)


def main():

    set_seed(SEED)

    model, tokenizer = load_model(MODEL_ID, HUGGINGFACE_TOKEN)
    do_analysis(model, INSTRUCTION, tokenizer, DIR_JSON_PATH, RES_PATH)

if __name__ == "__main__":
    main()

# llama3
# CUDA_VISIBLE_DEVICES=0 python llama_analyzer.py