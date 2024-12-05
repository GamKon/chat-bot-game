from aiogram.types import Message
from db.queries import *
from utility import debug_print, num_tokens_from_string
from rag import get_relevant_chat_history, get_num_vectors


#####################################################################################
# Apply template syntax to the prompt
def apply_template_syntax(message_to_llm: str, messages_history, current_system_prompt, user_role_name, assistant_role_name, format_to: str = "Llama3") -> str:

    # for message in messages_history:
    #     rag_system_prompt += message + "\n\n"

##    rag_system_prompt += "Last new user input: \n"
#    debug_print("rag_system_prompt", rag_system_prompt)

    ###########################################################
    # Template according to model format
    ###########################################################

    ###########################################################
    # Alpaca format
    if format_to == "Alpaca":
        if user_role_name == "": user_role_name = "Instruction: "
        if assistant_role_name == "": assistant_role_name = "Response: "
        #user_role_name = "User: "
        #assistant_role_name = "Assistant: "

        prompt_to_llm = "System:\n" + current_system_prompt[0] + "\n"
        for message in messages_history:
            user_message = message.split('\n\n')[0]
            ai_message = message.split('\n\n')[1]

            prompt_to_llm += f"{user_role_name}\n{user_message}\n"
            prompt_to_llm += f"{assistant_role_name}\n{ai_message}\n\n"
        prompt_to_llm += f"{user_role_name}\n{message_to_llm}\n{assistant_role_name}\n"

    ###########################################################
    # Mistral format
    elif format_to == "Mistral":
        if user_role_name == "":
            user_role_name = "User: "
        else:
            user_role_name = user_role_name + ": "

        if assistant_role_name == "":
            assistant_role_name = "Assistant: "
        else:
            assistant_role_name = assistant_role_name + ": "

        prompt_to_llm = "[INST] <<SYS>> " + current_system_prompt[0] + " <</SYS>> \n"
        for message in messages_history:
            user_message = message.split('\n\n')[0]
            ai_message = message.split('\n\n')[1]

            prompt_to_llm += user_role_name + user_message + " [/INST] "
            prompt_to_llm += assistant_role_name + ai_message + "</s><s> [INST] "
        prompt_to_llm += user_role_name + message_to_llm + " [/INST] "

        # Without roles names at all
        # prompt_to_llm = "<s>[INST] " + current_system_prompt[0] + "\n"
        # for message in messages_history:
        #     user_message = message.split('\n\n')[0]
        #     ai_message = message.split('\n\n')[1]

        #     prompt_to_llm += user_message + " [/INST] "
        #     prompt_to_llm += ai_message + "</s> \n[INST] "
        # prompt_to_llm += message_to_llm + " [/INST]"

    ###########################################################
    # Llama2 format
    elif format_to == "Llama2":
        # if user_role_name == "":
        #     user_role_name = "Instruction: "
        # else:
        #     user_role_name = user_role_name + ": "

        # if assistant_role_name == "":
        #     assistant_role_name = "Response: "
        # else:
        #     assistant_role_name = assistant_role_name + ": "

        prompt_to_llm = "[INST] <<SYS>>\n" + current_system_prompt[0] + "\n<</SYS>>\n\n"
        for message in messages_history:
            user_message = message.split('\n\n')[0]
            ai_message = message.split('\n\n')[1]
            prompt_to_llm += user_message + " [/INST] "
            prompt_to_llm += ai_message + " </s><s> [INST] "
        prompt_to_llm += message_to_llm + " [/INST] "

    ###########################################################
    # Meta Llama-3 format (default)
    else:
        #format_to == "Llama3":

        if user_role_name == "": user_role_name = "user"
        if assistant_role_name == "": assistant_role_name = "assistant"

        # make messages list from DB in STRING format

        # TODO check if <|begin_of_text|> at the beginning gives a following error:
        # llama_tokenize_internal: Added a BOS token to the prompt as specified by the model but the prompt also starts with a BOS token. So now the final prompt starts with 2 BOS tokens. Are you sure this is what you want?
        # prompt_to_llm = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n" + current_system_prompt[0] + "<|eot_id|>"

        prompt_to_llm = "<|start_header_id|>system<|end_header_id|>\n" + current_system_prompt[0] + "<|eot_id|>"
        for message in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            user_message = message.split('\n\n')[0]
            ai_message = message.split('\n\n')[1]
            prompt_to_llm += "<|start_header_id|>"+user_role_name+"<|end_header_id|>\n"+user_message+"<|eot_id|>"
            prompt_to_llm += "<|start_header_id|>"+assistant_role_name+"<|end_header_id|>\n"+ai_message+"<|eot_id|>"

        prompt_to_llm += f"<|start_header_id|>{user_role_name}<|end_header_id|>\n{message_to_llm}<|eot_id|><|start_header_id|>{assistant_role_name}<|end_header_id|>\n"



    return prompt_to_llm

###########################################################
# Prepare prompt for LLM
async def chat_template_rag(message_to_llm: str, namespace: str, message: Message, format_to: str = "Meta", top_k: int = 1, use_names: bool = True, depth: int = 3, max_tokens_to_llm: int = 2048):

    prompt_to_llm = ""
    #top_k = 0
    current_system_prompt = await select_system_prompt(message.from_user.id)
    #debug_print("current_system_prompt", current_system_prompt) # current_system_prompt[0]

    # If not use_names of roles are empty, don't add ":" to prompt
    if use_names:
        roles = [current_system_prompt[1], current_system_prompt[2]]
        user_role_name      = "" if roles[0] == "" else f"{roles[0]}"
        assistant_role_name = "" if roles[1] == "" else f"{roles[1]}"
    else:
        user_role_name      = ""
        assistant_role_name = ""

    ##########################################################################################################################################################
    # Get last dialogues and add them to RAG rezults to keep context of the last events
    last_dialogues_user, last_dialogues_ai = await select_last_dialogues(user_id = message.from_user.id, depth = depth)
    last_dialogues = []

    # If there are not enought messages yet to get depth of dialogues
    if len(last_dialogues_user) < depth:
        depth = len(last_dialogues_user)

    for i in range(depth):
        last_dialogues.append(str(last_dialogues_user[i][0]) + "\n\n" + str(last_dialogues_ai[i][0]))
#            debug_print(f"Dialogue {i}", str(last_dialogues_user[i][0]) + " \n" + str(last_dialogues_ai[i][0]))
    # Reverse order to have last dialogues in time order
    last_dialogues.reverse()
#        debug_print("last_dialogues", last_dialogues)

    # Add last ai message to rag request
    if len(last_dialogues_ai) > 0:
        message_to_rag = last_dialogues_ai[0][0] + "\n\n" + message_to_llm
    else:
        message_to_rag = message_to_llm

    ##########################################################################################################################################################
    # Get relevant chat history from Pinecone
    messages_history = get_relevant_chat_history(message_to_rag, namespace, top_k)
    debug_messages_history = messages_history
    ##########################################################################################################################################################
    # Remove dialogues to have last dialogs added in order
    for dialogue in last_dialogues:
        if dialogue in messages_history:
            messages_history.remove(dialogue)
#                debug_print("Removed", dialogue)
    # Append last dialogues to messages_history
    for dialogue in last_dialogues:
        messages_history.append(dialogue)
#            debug_print("Appended", dialogue)

#    rag_system_prompt = current_system_prompt[0] + "\n\nHere is what happened earlier:\n\n"

    # # Add empty element to the beginning of messages_history
    # messages_history.insert(0, "")


    prompt_to_llm = apply_template_syntax(message_to_llm, messages_history, current_system_prompt, user_role_name, assistant_role_name, format_to)
    num_tokens_to_llm = num_tokens_from_string(prompt_to_llm, "cl100k_base")
    pop_count = 0
    while num_tokens_to_llm > max_tokens_to_llm:

        # remove first element from messages_history
        messages_history.pop(0)
        pop_count += 1
        prompt_to_llm = apply_template_syntax(message_to_llm, messages_history, current_system_prompt, user_role_name, assistant_role_name, format_to)
        num_tokens_to_llm = num_tokens_from_string(prompt_to_llm, "cl100k_base")

    # debug_print("prompt_to_llm", prompt_to_llm)
    debug_print("num_tokens_to_llm", num_tokens_to_llm)
    debug_print("max_tokens_to_llm", max_tokens_to_llm)
    # debug_print("Total Vectors in DB", get_num_vectors(namespace))



    # if len(prompt_to_llm) > max_prompt_to_llm:
    #     return ""
    # else:
        # Show rag retrieved messages
    # for message in debug_messages_history:
    #     debug_print("relevant chat history from Pinecone", message)
    return prompt_to_llm, pop_count

'''
Meta format:
    <|begin_of_text|><|start_header_id|>system<|end_header_id|>
    {{ system_prompt }}<|eot_id|><|start_header_id|>user<|end_header_id|>
    {{ user_message_1 }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
    {{ model_answer_1 }}<|eot_id|><|start_header_id|>user<|end_header_id|>
    {{ user_message_2 }}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''

'''
    ###########################################################
    # ChatML format
    if format_to == "ChatML":
        if user_role_name == "": user_role_name = "user"
        if assistant_role_name == "": assistant_role_name = "assistant"

        # make messages list from DB in STRING format
        prompt_to_llm = "<|im_start|>system\n" + current_system_prompt[0] + "<|im_end|>\n"
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                prompt_to_llm += f"<|im_start|>{user_role_name}\n{prompt[1]}<|im_end|>\n"
            else:
                prompt_to_llm += f"<|im_start|>{assistant_role_name}\n{prompt[1]}<|im_end|>\n"
        prompt_to_llm += f"<|im_start|>{user_role_name}\n{message_to_llm}<|im_end|>\n<|im_start|>{assistant_role_name}\n"
    # "<|assistant (provide varied, creative, and vivid narration; follow all narrative instructions;
    # include all necessary possessive pronouns; maintain consistent story details; only roleplay as {{char}})|>\n"

    ###########################################################
    # Meta Llama-3 format
    elif format_to == "Meta":

        if user_role_name == "": user_role_name = "user"
        if assistant_role_name == "": assistant_role_name = "assistant"

        # make messages list from DB in STRING format
        prompt_to_llm = "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n" + current_system_prompt[0] + "<|eot_id|>"
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                prompt_to_llm += f"<|start_header_id|>{user_role_name}<|end_header_id|>\n{prompt[1]}<|eot_id|>"
            else:
                prompt_to_llm += f"<|start_header_id|>{assistant_role_name}<|end_header_id|>\n{prompt[1]}<|eot_id|>"
        prompt_to_llm += f"<|start_header_id|>{user_role_name}<|end_header_id|>\n{message_to_llm}<|eot_id|><|start_header_id|>{assistant_role_name}<|end_header_id|>\n"

    ###########################################################
    # Pygmalion format
    elif format_to == "Pygmalion":
        #if user_role_name == "": user_role_name = "user"
        #if assistant_role_name == "": assistant_role_name = "model"
        user_role_name = ""
        assistant_role_name = ""
        # make messages list from DB in STRING format
        prompt_to_llm = "<|system|>" + current_system_prompt[0]
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                prompt_to_llm += f"<|user|>{user_role_name}{prompt[1]}"
            else:
                prompt_to_llm += f"<|assistant|>{assistant_role_name}{prompt[1]}"
        prompt_to_llm += f"<|user|>{user_role_name}{message_to_llm}<|assistant|>{assistant_role_name}"

    ###########################################################
    # Alpaca format
    elif format_to == "Alpaca":
        if user_role_name == "": user_role_name = "Input: "
        if assistant_role_name == "": assistant_role_name = "Response: "

        # make messages list from DB in STRING format
        prompt_to_llm = "### Insruction:\n" + current_system_prompt[0] + "\n"
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                prompt_to_llm += f"### {user_role_name}\n{prompt[1]}\n"
            else:
                prompt_to_llm += f"### {assistant_role_name}{prompt[1]}\n"
        prompt_to_llm += f"### {user_role_name}\n{message_to_llm}\n### {assistant_role_name}\n"

    ###########################################################
    # Vicuna format
    elif format_to == "Vicuna":
        # if user_role_name == "": user_role_name = "user"
        user_role_name = "USER: "
        # if assistant_role_name == "": assistant_role_name = "assistant"
        assistant_role_name = "ASSISTANT: "

        # make messages list from DB in STRING format
        prompt_to_llm = "SYSTEM: " + current_system_prompt[0] + "\n"
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                prompt_to_llm += f"{user_role_name}{prompt[1]}\n"
            else:
                prompt_to_llm += f"{assistant_role_name}{prompt[1]}\n"
        prompt_to_llm += f"{user_role_name}{message_to_llm}\n{assistant_role_name}"

    ###########################################################
    elif format_to == "json":
        # make messages list from DB in JSON format
        if user_role_name == "": user_role_name = "user"
        if assistant_role_name == "": assistant_role_name = "assistant"
        prompt_to_llm = []

        prompt_to_llm.append({"role": "system", "content": current_system_prompt[0]})
        for prompt in messages_history:
            prompt_to_llm.append({"role": "assistant", "content": prompt[1]})
        prompt_to_llm.append({"role": "user", "content": message_to_llm})

    ###########################################################
    # Mistral format (default)
    else:
        # format_to == "Mistral":
        # make messages list from DB in STRING format
        prompt_to_llm = "<s>[INST] <<SYS>>\n" + current_system_prompt[0] + "\n<</SYS>>\n"
        for prompt in messages_history:
            # Check for message's Author form Messages table (user, ai)
            if prompt[0].lower() == "user":
                prompt_to_llm += user_role_name + prompt[1] + " [/INST] "
            elif prompt[0].lower() == "ai":
                # Add ai message to prompt
                prompt_to_llm += assistant_role_name + prompt[1] + "</s>[INST] "
        prompt_to_llm += user_role_name + message_to_llm + " [/INST] " + assistant_role_name


    return prompt_to_llm
'''