#https://huggingface.co/TheBloke/Guanaco-13B-Uncensored-AWQ
# TheBloke/Guanaco-13B-Uncensored-AWQ

from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer, pipeline, AutoModelForCausalLM

async def AWQ_Guanaco_13B_Uncensored_AWQ_pipe(prompt_to_llm: str, max_new_tokens: int):

    if max_new_tokens <= 20 and max_new_tokens >= 2048: max_new_tokens = 256
    print("1----------------------------------------------prompt TO AWQ Mistral 7b-----------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")

    model_name_or_path = "TheBloke/Guanaco-13B-Uncensored-AWQ"

    generation_type = "text-generation"
    # Conversational pipeline applies it's own chat template
    # which denies "system" role in prompt
    #generation_type = "conversational"


    # Load model
#    model = AutoAWQForCausalLM.from_quantized(model_name_or_path, fuse_layers=True,
#                                              trust_remote_code=False, safetensors=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=False)

    model = AutoModelForCausalLM.from_pretrained(
        model_name_or_path,
        device_map="cuda:0",
#        fuse_layers=True,
        trust_remote_code=False)#,
#        safetensors=True)

    # prompt = "Tell me about AI"
    prompt_template= prompt_to_llm
    #f'''### Human: {prompt_to_llm}




    # model_name_or_path = "TheBloke/Guanaco-13B-Uncensored-AWQ"

    # # Load model
    # model = AutoAWQForCausalLM.from_quantized(model_name_or_path, fuse_layers=True,
    #                                           trust_remote_code=False, safetensors=True)
    # tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=False)

    # prompt = "Tell me about AI"
    # prompt_template=f'''### Human: {prompt}
    # ### Assistant:

    # '''

    # print("\n\n*** Generate:")

    # tokens = tokenizer(
    #     prompt_template,
    #     return_tensors='pt'
    # ).input_ids.cuda()

    # # Generate output
    # generation_output = model.generate(
    #     tokens,
    #     do_sample=True,
    #     temperature=0.7,
    #     top_p=0.95,
    #     top_k=40,
    #     max_new_tokens=max_new_tokens
    # )

# print("Output: ", tokenizer.decode(generation_output[0]))

# # Inference can also be done using transformers' pipeline


# print("*** Pipeline:")
    pipe            = pipeline(
    task            = generation_type,
    model           = model,
    tokenizer       = tokenizer,
    max_new_tokens  = max_new_tokens,
    do_sample       = True,
    temperature     = 0.7,
    top_p           = 0.95,
    top_k           = 40,
    repetition_penalty= 1.1
)
    pipe_output = pipe(prompt_template)[0]['generated_text']

    llm_reply = str(pipe_output.split('###')[-1])#.split('</s>')[0]
    print("3----------------------------------------------RAW output FROM AWQ Mistral 7B-----------------------------------")
    print(pipe_output)
    print("4---------------------------------------------SPLIT output FROM AWQ Mistral 7B----------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)

##########################################################################################################################################################
async def AWQ_Guanaco_13B_Uncensored_AWQ(prompt_to_llm: str, max_new_tokens: int):

    model_name_or_path = "TheBloke/Guanaco-13B-Uncensored-AWQ"
    # Load model
    model = AutoAWQForCausalLM.from_quantized(model_name_or_path, fuse_layers=True,
                                              trust_remote_code=False, safetensors=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=False)

    # prompt = "Tell me about AI"
    # prompt_template=f'''### Human: {prompt}
    # ### Assistant:

    # '''

    # print("\n\n*** Generate:")

    tokens = tokenizer(
        prompt_to_llm,
        return_tensors='pt'
    ).input_ids.cuda()

    # Generate output
    output = model.generate(
        tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_new_tokens=max_new_tokens
    )

    llm_reply_full = tokenizer.decode(output[0])

    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw output FROM Mixtral 8x7B GPTQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)
