import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")

async def gpt_3_5_turbo_1106(prompt_to_llm):

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    # INITIAL_PROMPT = """
    # You are a funny AI that adds a joke to every answer
    # """

    # FORMATTING_PROMPT = (
    #     "User: 'user question'\n"
    #     "AI: 'AI answer'\n"
    #     "Ai: 'AI joke about the question'\n"
    # )

    # text = "What is the distance from the Moon to the Sun?"
    # open('last2.txt', 'r').read()



    completion = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=prompt_to_llm
#        messages=[
#            {"role": "system", "content": INITIAL_PROMPT},
#            {"role": "system", "content": FORMATTING_PROMPT},
#            {"role": "user", "content": text}
#        ]
    )

    llm_reply_full = completion.choices[0].message.content

    print("3----------------------------------------------raw prompt FROM Chat GPT-----------------------------------------------------")
    print(llm_reply_full)
    print("--------------------------------------------------------------------------------------------------------------")
    # print(llm_reply)
    # print("5---------------------------------------------------------------------------------------------------------------")

    return llm_reply_full


# Alex
# from openai import OpenAI

# client = OpenAI(api_key=KEY)

# INITIAL_PROMPT = """
# You are the smart video transcription summarizer. Based on the video transcript you can generate chapters and provide
# key points for every chapter
# """

# FORMATTING_PROMPT = (
#     "A chapter is a topic that was discussed in the video. If concurrent topics are similar, combine them "
#     "into one topic. For each chapter, generate key points that summarize the chapter content. Provide the "
#     "output in a list, and only output this list. Here is an example output delimited by triple backticks to "
#     "understand the desired output format:\n\n"
#     "```\n"
#     "the first chapter\n"
#     "- key point 1 ...\n"
#     "- key point 2 ...\n"
#     "- key point 3 ...\n\n"
#     "the second chapter\n"
#     "a brief summary on what was discussed in this chapter\n"
#     "```\n\n"
#     "Do not use the content of above example in the final output under any circumstances.\n"
#     "The input is in Russian, and you need to respond in Russian, also"
# )

# text = open('last2.txt', 'r').read()

# completion = client.chat.completions.create(
#     model="gpt-3.5-turbo-1106",
#     messages=[
#         {"role": "system", "content": INITIAL_PROMPT},
#         {"role": "system", "content": FORMATTING_PROMPT},
#         {"role": "user", "content": text}
#     ]
# )

# print(completion.choices[0].message.content)