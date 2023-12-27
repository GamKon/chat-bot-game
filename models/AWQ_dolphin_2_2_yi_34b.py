# https://huggingface.co/TheBloke/dolphin-2_2-yi-34b-AWQ

from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer#, YiTokenizer, YiModel
import re
async def AWQ_Dolphin_2_2_yi_34b_pipe(prompt_to_llm: str, max_new_tokens: int):

    if max_new_tokens <= 20 and max_new_tokens >= 2048: max_new_tokens = 256

    model_name_or_path = "TheBloke/dolphin-2_2-yi-34b-AWQ"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="cuda:0",
        trust_remote_code=True
    )

    # # Using the text streamer to stream output one token at a time
    # streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)


# !!!!!!
    # prompt = "Tell me about AI"
    # prompt_template=f'''<|im_start|>system
    # {system_message}<|im_end|>
    # <|im_start|>user
    # {prompt}<|im_end|>
    # <|im_start|>assistant
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
        "max_new_tokens": max_new_tokens,
        "repetition_penalty": 1.1
    }

    # Generate streamed output, visible one token at a time
    # generation_output = model.generate(
    #     tokens,
    #     streamer=streamer,
    #     **generation_params
    # )

    # # Generation without a streamer, which will include the prompt in the output
    # generation_output = model.generate(
    #     tokens,
    #     **generation_params
    # )

    # # Get the tokens from the output, decode them, print them
    # token_output = generation_output[0]
    # text_output = tokenizer.decode(token_output)
    # print("model.generate output: ", text_output)

    # # string
    # llm_reply_full = tokenizer.decode(output[0])

    # llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]

    # print("3----------------------------------------------raw output FROM AWQ_Dolphin-----------------------------------------------------")
    # print(llm_reply_full)
    # print("4-splitted--------------------------------------------------------------------------------------------------------------")
    # print(llm_reply)
    # print("5---------------------------------------------------------------------------------------------------------------")
    # return str(llm_reply)




    # Inference is also possible via Transformers' pipeline
    from transformers import pipeline

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        **generation_params
    )

    pipe_output = pipe(prompt_template)[0]['generated_text']
    #print("pipeline output: ", pipe_output)


    llm_reply = pipe_output.split('<|im_start|>')[-1]
    print("3----------------------------------------------raw output FROM AWQ_Dolphin pipe-----------------------------------------------------")
    print(pipe_output)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)
