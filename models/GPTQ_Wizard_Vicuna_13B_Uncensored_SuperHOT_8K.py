#https://huggingface.co/TheBloke/Wizard-Vicuna-13B-Uncensored-SuperHOT-8K-GPTQ

from transformers import AutoTokenizer, pipeline, logging
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
import argparse

async def GPTQ_Wizard_Vicuna_13B(prompt_to_llm):



    model_name_or_path = "TheBloke/Wizard-Vicuna-13B-Uncensored-SuperHOT-8K-GPTQ"
    model_basename = "wizard-vicuna-13b-uncensored-superhot-8k-GPTQ-4bit-128g.no-act.order"

    use_triton = False

    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

    model = AutoGPTQForCausalLM.from_quantized(
        model_name_or_path,
#           revision='gptq-4bit-128g.no-act.order',
        use_safetensors=True,
        trust_remote_code=True,
        device_map='auto',
        use_triton=use_triton,
        quantize_config=None)

    model.seqlen = 8192
    prompt_template = prompt_to_llm

    # # Note: check the prompt template is correct for this model.
    # prompt = "Tell me about AI"
    # prompt_template=f'''USER: {prompt}
    # ASSISTANT:'''

    # print("\n\n*** Generate:")

    input_ids = tokenizer(prompt_template, return_tensors='pt').input_ids.cuda()
    output = model.generate(inputs=input_ids, temperature=0.7, max_new_tokens=512)
    # print(tokenizer.decode(output[0]))

    # string
    llm_reply_full = tokenizer.decode(output[0])

    llm_reply = str(llm_reply_full.split('[/INST] ')[-1]).split('</s>')[0]

    print("3----------------------------------------------raw output FROM Wizard Vicuna 13B-----------------------------------------------------")
    print(llm_reply_full)
    print("4-splitted--------------------------------------------------------------------------------------------------------------")
    print(llm_reply)
    print("5---------------------------------------------------------------------------------------------------------------")
    return str(llm_reply)


    # Inference can also be done using transformers' pipeline

    # Prevent printing spurious transformers error when using pipeline with AutoGPTQ
    logging.set_verbosity(logging.CRITICAL)

    print("*** Pipeline:")
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        temperature=0.7,
        top_p=0.95,
        repetition_penalty=1.15
    )

    print(pipe(prompt_template)[0]['generated_text'])
