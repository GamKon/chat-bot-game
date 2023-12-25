# https://huggingface.co/TheBloke/Mixtral-8x7B-Instruct-v0.1-AWQ

from transformers import AutoModelForCausalLM, AutoTokenizer, MixtralForCausalLM, TextStreamer

def AWQ_Mixtral_8x7B_Instruct(prompt_to_llm):
    model_name_or_path = "TheBloke/Mixtral-8x7B-Instruct-v0.1-AWQ"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="auto",
        trust_remote_code=True,
        revision="main"
    )

    # # Using the text streamer to stream output one token at a time
    # streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # prompt = "Tell me about AI"
    # prompt_template=f'''[INST] {prompt} [/INST]
    # '''

    prompt_template = prompt_to_llm

    # Convert prompt to tokens
    tokens = tokenizer(
        prompt_template,
        return_tensors='pt'
    ).input_ids.cuda()

    generation_params = {
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": 512,
        "repetition_penalty": 1.1
    }

    # # Generate streamed output, visible one token at a time
    # generation_output = model.generate(
    #     tokens,
    #     streamer=streamer,
    #     **generation_params
    # )

    # Generation without a streamer, which will include the prompt in the output
    generation_output = model.generate(
        tokens,
        **generation_params
    )

    # # Get the tokens from the output, decode them, print them
    token_output = generation_output[0]
    llm_reply_full = tokenizer.decode(token_output)


    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]
    print("3----------------------------------------------raw prompt FROM AWQ Mixtral 8x7B-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)


    # print("model.generate output: ", text_output)
##########################################################################################################################################################
# Pipeline
def AWQ_Mixtral_8x7B_Instruct_pipe(prompt_to_llm):
    model_name_or_path = "TheBloke/Mixtral-8x7B-Instruct-v0.1-AWQ"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="cuda:0",
        trust_remote_code=True,
        revision="main"
    )

    # # Using the text streamer to stream output one token at a time
    # streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # prompt = "Tell me about AI"
    # prompt_template=f'''[INST] {prompt} [/INST]
    # '''

    prompt_template = prompt_to_llm

    # Convert prompt to tokens
    tokens = tokenizer(
        prompt_template,
        return_tensors='pt'
    ).input_ids.cuda()

    generation_params = {
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": 512,
        "repetition_penalty": 1.1
    }

    # # Generate streamed output, visible one token at a time
    # generation_output = model.generate(
    #     tokens,
    #     streamer=streamer,
    #     **generation_params
    # )

    # Generation without a streamer, which will include the prompt in the output
    # generation_output = model.generate(
    #     tokens,
    #     **generation_params
    # )

    # # # Get the tokens from the output, decode them, print them
    # token_output = generation_output[0]
    # text_output = tokenizer.decode(token_output)
    # print("model.generate output: ", text_output)


    # Inference is also possible via Transformers' pipeline
    from transformers import pipeline

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        **generation_params
    )

    llm_reply_full = pipe(prompt_to_llm)[0]['generated_text']#.split('[/INST] ')[-1]
    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]
    print("3----------------------------------------------raw prompt FROM  AWQ Mixtral 8x7B pipe-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)
