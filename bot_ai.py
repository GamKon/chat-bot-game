

def template_prompt(initial_prompt, chat_history, user_prompt):
    if True:
        user_name = "user:"
        llm_name = "game:"

    full_templated_prompt=f"[INST] <<SYS>> {initial_prompt} <</SYS>> [/INST] "

    for dialog in chat_history:
        full_templated_prompt += f" <s> [INST] {user_name} {dialog['input']} [/INST] {llm_name}: {dialog['output']} </s> "

    full_templated_prompt += f" <s> [INST] {user_name} {user_prompt} [/INST] "
    return full_templated_prompt
