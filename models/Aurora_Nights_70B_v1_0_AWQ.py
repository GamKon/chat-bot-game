# https://huggingface.co/TheBloke/Aurora-Nights-70B-v1.0-AWQ

from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer, pipeline
from accelerate.utils import release_memory
import torch

async def AWQ_Aurora_Nights_70B_v1_0(prompt_to_llm: str, max_new_tokens: int):

    if max_new_tokens <= 20 and max_new_tokens >= 2048: max_new_tokens = 256
    print("1----------------------------------------------prompt TO TheBloke/Aurora-Nights-70B-v1.0-AWQ-----------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")

    model_name_or_path = "TheBloke/Aurora-Nights-70B-v1.0-AWQ"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="cuda:0"
    )

    # # Using the text streamer to stream output one token at a time
    # streamer = TextStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # prompt = "Tell me about AI"
    # prompt_template=f'''### Instruction:
    # {prompt}
    # ### Response:
    # '''

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

    # Get the tokens from the output, decode them, print them
    token_output = generation_output[0]
    llm_reply_full = tokenizer.decode(token_output)

    print("\n!!!!!!!MAX MEMORY!!!!!!!!!!!!!!\n")
    print(torch.cuda.max_memory_allocated())
    release_memory(model)
    print(torch.cuda.max_memory_allocated())
    print("\n!!!!!!!MAX MEMORY!!!!!!!!!!!!!!\n")

    # Mistral format extraction
    #llm_reply = str(llm_reply_full.split('[/INST]')[-1]).split('</s>')[0]

    # Pygmalion format extraction
    llm_reply = str(llm_reply_full.split('<|assistant|>')[-1]).split('</s>')[0]

    # CtatML format extraction
    #llm_reply = str(llm_reply_full.split('<|im_start|>')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw output FROM TheBloke/Aurora-Nights-70B-v1.0-AWQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)

##########################################################################################################################################################
    # Inference is also possible via Transformers' pipeline
async def AWQ_Aurora_Nights_70B_v1_0_pipe(prompt_to_llm: str, max_new_tokens: int):

    if max_new_tokens <= 20 and max_new_tokens >= 2048: max_new_tokens = 256
    print("1----------------------------------------------prompt TO TheBloke/Aurora-Nights-70B-v1.0-AWQ-----------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")

    model_name_or_path = "TheBloke/Aurora-Nights-70B-v1.0-AWQ"

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        low_cpu_mem_usage=True,
        device_map="cuda:0"
    )

    generation_params = {
        "do_sample": True,
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_new_tokens": max_new_tokens,
        "repetition_penalty": 1.1
    }

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        **generation_params
    )


    llm_reply_full = pipe(prompt_to_llm)[0]['generated_text']
    # Pygmalion format extraction
    llm_reply = str(llm_reply_full.split('<|assistant|>')[-1]).split('</s>')[0]

    # CtatML format extraction
    #llm_reply = str(llm_reply_full.split('<|im_start|>')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw output FROM TheBloke/Aurora-Nights-70B-v1.0-AWQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)


    # pipe_output = pipe(prompt_template)[0]['generated_text']
    # print("pipeline output: ", pipe_output)

    # llm_reply_full = pipe(prompt_to_llm)[0]['generated_text']#.split('[/INST] ')[-1]
    # llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]
    # print("3----------------------------------------------raw output FROM TheBloke/Aurora-Nights-70B-v1.0-AWQ-----------------------------------------------------")
    # print(llm_reply_full)
    # print("4-splitted--------------------------------------------------------------------------------------------------------------")
    # print(llm_reply)
    # print("5---------------------------------------------------------------------------------------------------------------")
    # return str(llm_reply)