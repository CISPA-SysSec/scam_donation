import os
import glob

def list_files_in_directory(directory_path):
    files = glob.glob(f"{directory_path}/*")
    return [file for file in files if os.path.isfile(file)]

def create_message(instruction, comment):
    messages = [
        {"role": "system", "content": f"{instruction}"},
        {"role": "user", "content": f"Comment: {comment}"},
    ]

    return messages

def parse_classification_response(response):
    result = {
        "Category": "",
        "Explanation": "",
        "Errors": False
    }
    
    # Split the response into lines
    lines = response.split("\n")
    
    # Iterate through the lines to find the category and explanation
    for line in lines:
        if line.startswith("Category:"):
            result["Category"] = line.split(":", 1)[1].strip().strip('"')
        elif line.startswith("Explanation:"):
            result["Explanation"] = line.split(":", 1)[1].strip().strip('"')
    
    if len(result["Category"]) == 0 or len(result["Explanation"]) == 0:
        result["Errors"] = True

    return result