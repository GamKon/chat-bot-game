from aiogram.types import Message
from db.queries import *
from utility import debug_print
###########################################################
# Prepare prompt for LLM
async def chat_template(message_to_llm: str, message: Message, format_to: str = "Mistral", use_names: bool = True):

    current_system_prompt = await select_system_prompt(message.from_user.id)
    debug_print("current_system_prompt", current_system_prompt) # current_system_prompt[0]

    # If not use_names of roles are empty, don't add ":" to prompt
    if use_names:
        roles = [current_system_prompt[1], current_system_prompt[2]]
        user_role_name      = "" if roles[0] == "" else f"{roles[0]}: "
        assistant_role_name = "" if roles[1] == "" else f"{roles[1]}: "
    else:
        user_role_name      = ""
        assistant_role_name = ""

    messages_history = await select_user_chat_history(user_id = message.from_user.id)
    ###########################################################
    # Mistral format
    if format_to == "Mistral":
        # make messages list from DB in STRING format
        prompt_to_llm = "<s>[INST] <<SYS>>\n" + current_system_prompt[0] + "\n<</SYS>>\n"
        for prompt in messages_history:
            # Check for message's Author form Messages table (user, ai)
            if prompt[0].lower() == "user":
                prompt_to_llm += user_role_name + prompt[1] + " [/INST] "
            elif prompt[0].lower() == "ai":
# No need any more. TEST it!
#                # Remove assistant role name from prompt if AI added it
#                if assistant_role_name != "":
#                    assistant_prompt = prompt[1].replace(assistant_role_name, "", 1)
#                else:
#                    assistant_prompt = prompt[1]

                # Add ai message to prompt
                prompt_to_llm += assistant_role_name + prompt[1] + "</s>[INST] "
        prompt_to_llm += user_role_name + message_to_llm + " [/INST] " + assistant_role_name
    ###########################################################
    # ChatML format
    elif format_to == "ChatML":
        if user_role_name == "": user_role_name = "user"
        if assistant_role_name == "": assistant_role_name = "assistant"

        # make messages list from DB in STRING format
        prompt_to_llm = "<|im_start|>system\n" + current_system_prompt[0] + "<|im_end|>\n"
        for prompt in messages_history:
            # TODO add custom role names
            # !!! Anyway in DB roles must be "user" and "assistant" !!!
            # x if C else y
            if prompt[0].lower() == "user":
                # If roles are empty, don't add ":" to prompt
                prompt_to_llm += f"<|im_start|>{user_role_name}\n{prompt[1]}<|im_end|>\n"
            else:
                prompt_to_llm += f"<|im_start|>{assistant_role_name}\n{prompt[1]}<|im_end|>\n"
        prompt_to_llm += f"<|im_start|>{user_role_name}\n{message_to_llm}<|im_end|>\n<|im_start|>{assistant_role_name}\n"
# "<|assistant (provide varied, creative, and vivid narration; follow all narrative instructions;
# include all necessary possessive pronouns; maintain consistent story details; only roleplay as {{char}})|>\n"


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
                # If roles are empty, don't add ":" to prompt
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
                # If roles are empty, don't add ":" to prompt
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
                # If roles are empty, don't add ":" to prompt
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
    # print("----------------------------------------------prompt_to_llm after TEMPLATING-----------------------------------------------------")
    # print(prompt_to_llm)
    # print("---------------------------------------------------------------------------------------------------------------")

    return prompt_to_llm
