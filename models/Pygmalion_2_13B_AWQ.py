#https://huggingface.co/TheBloke/Pygmalion-2-13B-AWQ

from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

async def Pygmalion_2_13B_AWQ(prompt_to_llm: str, max_new_tokens: int):

    if max_new_tokens <= 20 and max_new_tokens >= 2048: max_new_tokens = 256
    print("1----------------------------------------------prompt TO Pygmalion-2-13B-AWQ-----------------------------------------")
    print(prompt_to_llm)
    print("2---------------------------------------------------------------------------------------------------------------")


    model_name_or_path = "TheBloke/Pygmalion-2-13B-AWQ"

    # Load model
    model = AutoAWQForCausalLM.from_quantized(model_name_or_path, fuse_layers=True,
                                            trust_remote_code=False, safetensors=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, trust_remote_code=False)

    # prompt = "Tell me about AI"
    # prompt_template=f'''<|system|>Enter RP mode. Pretend to be {{char}} whose persona follows:
    # {{persona}}

    # You shall reply to the user while staying in character, and generate long responses.

    # '''

    # print("\n\n*** Generate:")

    tokens = tokenizer(
        prompt_to_llm,
        return_tensors='pt'
    ).input_ids.cuda()

    # Generate output
    generation_output = model.generate(
        tokens,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
        top_k=40,
        max_new_tokens=max_new_tokens
    )

    llm_reply_full = tokenizer.decode(generation_output[0])


    # Mistral format extraction
    #llm_reply = str(llm_reply_full.split('[/INST]')[-1]).split('</s>')[0]

    # Pygmalion format extraction
    llm_reply = str(llm_reply_full.split('<|model|>')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw output FROM Pygmalion-2-13B-AWQ-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)



# # Inference can also be done using transformers' pipeline
# from transformers import pipeline

# print("*** Pipeline:")
# pipe = pipeline(
#     "text-generation",
#     model=model,
#     tokenizer=tokenizer,
#     max_new_tokens=512,
#     do_sample=True,
#     temperature=0.7,
#     top_p=0.95,
#     top_k=40,
#     repetition_penalty=1.1
# )

# print(pipe(prompt_template)[0]['generated_text'])
