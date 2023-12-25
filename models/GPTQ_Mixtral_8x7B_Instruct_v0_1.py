from os import getenv
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline, BitsAndBytesConfig, ConversationalPipeline

##########################################################################################################################################################
# Not pipeline
def GPTQ_Mixtral_8x7B_Instruct(prompt_to_llm):
    model_name_or_path = "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ"
    # revision = "gptq-8bit-128g-actorder_True"
    revision = "gptq-4bit-32g-actorder_True"
    # revision = "gptq-4bit-128g-actorder_True"


    print("1----------------------------------------------prompt TO Mixtral 8x7B GPTQ-----------------------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")

    device = "cuda" # the device to load the model onto

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="auto",
        trust_remote_code=False,
        revision=revision)

    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        use_fast=True, add_generation_prompt=False)

    input_ids = tokenizer(prompt_to_llm, return_tensors='pt').input_ids.cuda()

    output = model.generate(
        inputs=input_ids,
        temperature=0.7,
        do_sample=True,
        top_p=0.95,
        top_k=40,
        max_new_tokens=256)

    # string
    llm_reply_full = tokenizer.decode(output[0])

    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw prompt FROM Mixtral 8x7B GPTQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)

##########################################################################################################################################################
# Pipeline
async def GPTQ_Mixtral_8x7B_Instruct_pipeline(prompt_to_llm):

    #model_name_or_path = "TheBloke/Mistral-7B-Instruct-v0.2-GPTQ"
    model_name_or_path = "TheBloke/Mixtral-8x7B-Instruct-v0.1-GPTQ"

    revision = "gptq-4bit-128g-actorder_True"
    #revision = "gptq-4bit-32g-actorder_True"
    #revision = "gptq-8bit-128g-actorder_True"
    #revision = "gptq-8bit-32g-actorder_True"

    generation_type = "text-generation"
    #generation_type = "conversational"

    print("1----------------------------------------------prompt TO Mixtral 8x7B GPTQ-----------------------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="auto",
        trust_remote_code=False,
        revision=revision)

    tokenizer = AutoTokenizer.from_pretrained(
        model_name_or_path,
        use_fast=True, add_generation_prompt=False)

    # encoders = tokenizer.apply_chat_template(messages, return_tensors="pt")
    # full_templated_prompt = f'''[INST] <<SYS>> {initial_prompt} <</SYS>> [/INST] <s>[INST] user: {message.text} [/INST]'''

##########################################################################################################################################################
# Pipeline
    pipe = pipeline(
        task            = generation_type,
        model           = model,
        tokenizer       = tokenizer,
        max_new_tokens  = 256,
        do_sample       = True,
#        num_beams=3,
        temperature     = 0.7,
        top_p           = 0.95,
        top_k           = 40,
        repetition_penalty = 1.1
    )
    llm_reply_full = pipe(prompt_to_llm)[0]['generated_text']#.split('[/INST]')[-1]
# string

    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw prompt FROM Mixtral 8x7B GPTQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)










    # Mistral
    # device = "cuda" # the device to load the model onto

    # encodeds = tokenizer.apply_chat_template(prompt_to_llm, return_tensors="pt")
    # model_inputs = encodeds.to(device)
    # model.to(device)
    # generated_ids = model.generate(model_inputs, max_new_tokens=1000, do_sample=True)
    # decoded = tokenizer.batch_decode(generated_ids)
    # #print(decoded[0])
    # llm_reply = decoded[0].split('[/INST]')[-1]

    # TheBloke
    # input_ids = tokenizer(prompt_to_llm, return_tensors='pt').input_ids.cuda()
    # output = model.generate(
    #     inputs=input_ids,
    #     temperature=0.7,
    #     do_sample=True,
    #     top_p=0.95,
    #     top_k=40,
    #     max_new_tokens=512)
    # print(tokenizer.decode(output[0]))





