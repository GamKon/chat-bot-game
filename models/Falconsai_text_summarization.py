from transformers import pipeline

async def text_summarization(prompt: str, max_length: int, min_length: int, do_sample: bool):
    summarizer = pipeline("summarization", model="Falconsai/text_summarization")
    summary = summarizer(prompt, max_length=max_length, min_length=min_length, do_sample=do_sample)[0]['summary_text']
    print(summary)
    return summary


# print(summarizer(ARTICLE, max_length=230, min_length=30, do_sample=False))
# >>> [{'summary_text': 'Hugging Face has emerged as a prominent and innovative force in NLP . From its inception to its role in democratizing AI, the company has left an indelible mark on the industry . The name "Hugging Face" was chosen to reflect the company\'s mission of making AI models more accessible and friendly to humans .'}]
