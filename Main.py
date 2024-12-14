import tiktoken
import pyperclip

encoding = tiktoken.get_encoding("o200k_base")

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens





copied_from_user_input = input("Paste your text here: ")
meta_prompt = "### Context ### You are a quant researcher working for a hedge fund. Your team is tasked with developing a new indicator that can provide alpha in the Futures Trading Market. Additionally, you utilize the Ninjatrader platform. When asked to update or modify code, unless explicilty asked to focus on a specific method or section, you always provide the full, updated and working code."

contextual_prompt_file = r"DirExported.txt"

with open(contextual_prompt_file, 'r', encoding='utf-8') as file:
    # Read all lines into a list
    contextual_prompt = file.read()

instructions_prefix = " ### Instructions ###"

instructions = "Please generate a novel indicator that can provide alpha in the Futures Trading Market. The above files are Ninjatrader indicators that ...."

copied_from_user_output = (f"### Prompt and/or code to address ###\n{copied_from_user_input}")

full_prompt_for_export = meta_prompt  + instructions_prefix + copied_from_user_output

token_count = num_tokens_from_string(full_prompt_for_export, "o200k_base")


print(f"Token count: {token_count}")

pyperclip.copy(full_prompt_for_export)
#(full_prompt_for_export)