from utility import debug_print

from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, TextIteratorStreamer, pipeline


async def llm_answer_from_model(prompt_to_llm,
                                current_user_model,
                                max_new_tokens):
    debug_print(f"prompt TO {current_user_model[0]}", prompt_to_llm)

    tokenizer = AutoTokenizer.from_pretrained(current_user_model[0], trust_remote_code=True)

    revision = "gptq-4bit-32g-actorder_True"

    if "GPTQ" in current_user_model[0]:
        model = AutoModelForCausalLM.from_pretrained(
            current_user_model[0],
            low_cpu_mem_usage=True,
            device_map="cuda:0",
            trust_remote_code=True,
            revision=revision
    #        cache_dir="/home/user/models/"
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            current_user_model[0],
            low_cpu_mem_usage=True,
            device_map="cuda:0",
            trust_remote_code=True
        )
    # Using the text streamer to stream output one token at a time
    streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # Convert prompt to tokens
    tokens = tokenizer(
        prompt_to_llm,
        return_tensors='pt'
    ).input_ids.cuda()

    generation_params = {
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": max_new_tokens,
        "repetition_penalty": 1.1
    }
##########################################################################################################################################################
    # Capture the output from the stdout
    import sys
    from io import StringIO
    # Create StringIO object
    old_stdout = sys.stdout
    new_stdout = StringIO()
    # Redirect stdout to StringIO object
    sys.stdout = new_stdout
##########################################################################################################################################################
    # Generate streamed output, visible one token at a time
    generation_output = model.generate(
        tokens,
        streamer=streamer,
        **generation_params
    )

    # Return stdout to normal
    sys.stdout = old_stdout

    llm_reply_stdout = new_stdout.getvalue()
    debug_print(f"Stdout RAW LLM reply from {current_user_model[0]}", llm_reply_stdout)

    length_str = len(str("".join(llm_reply_stdout.splitlines())).strip())
    debug_print("Length_str", length_str)
    if len(str("".join(llm_reply_stdout.splitlines())).strip()) == 0:
        raise Exception("LLM reply is empty")

    return llm_reply_stdout

##########################################################################################################################################################
    # # Generation without a streamer, which will include the prompt in the output
    # generation_output = model.generate(
    #     tokens,
    #     **generation_params
    # )
##########################################################################################################################################################

    # Get the tokens from the output, decode them, print them
    # token_output = generation_output[0]
    # llm_reply_full = tokenizer.decode(token_output, skip_special_tokens=True)

    # debug_print(f"RAW LLM reply from {current_user_model[0]}", llm_reply_full)

    # Extract only answer from LLM reply
    # if current_user_model[2] == "Mistral":
    #     # Mistral format extraction
    #     llm_reply = str(llm_reply_full.split('[/INST]')[-1]).split('</s>')[0]

    # debug_print(f"EXTRACTED LLM reply from {current_user_model[0]}", llm_reply)


