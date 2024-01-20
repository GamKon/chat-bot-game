from utility import debug_print
from llama_cpp import Llama

def llm_answer_from_gguf(prompt_to_llm,
                                current_user_model,
                                max_new_tokens):
    debug_print(f"prompt TO {current_user_model[0]}", prompt_to_llm)

    # Set gpu_layers to the number of layers to offload to GPU. Set to 0 if no GPU acceleration is available on your system.

    llm = Llama(
        model_path   = f"/home/user/.cache/huggingface/{current_user_model[0]}",#"+current_user_model[0],  # Download the model file first
        n_ctx        = 32768,  # The max sequence length to use - note that longer sequence lengths require much more resources
        n_threads    = 12,     # The number of CPU threads to use, tailor to your system and the resulting performance
        n_gpu_layers = -1      # The number of layers to offload to GPU, if you have GPU acceleration available
    )

    # Simple inference example
    output = llm(
        prompt_to_llm,      # Prompt
        max_tokens  = max_new_tokens,  # Generate up to 512 tokens
        # stop        = ["</s>"],   # Example stop token - not necessarily correct for this specific model! Please check before using.
        echo        = False        # Whether to echo the prompt
    )

    debug_print(f"RAW LLM reply from {current_user_model[0]}", output)

    #usage': {'prompt_tokens': 127, 'completion_tokens': 21, 'total_tokens': 148}
    llm_reply = output['choices'][0]['text'].strip()

    num_tokens = [output['usage']['prompt_tokens'], output['usage']['completion_tokens'], output['usage']['total_tokens']]
    debug_print("tokens", num_tokens)

    debug_print("llm_reply", llm_reply)

    # length_str = len(str("".join(llm_reply_stdout.splitlines())).strip())
    # debug_print("Length_str", length_str)
    # if len(str("".join(llm_reply_stdout.splitlines())).strip()) == 0:
    #     raise Exception("LLM reply is empty")

    return llm_reply, num_tokens
