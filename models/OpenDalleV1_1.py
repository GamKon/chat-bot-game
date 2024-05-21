# https://huggingface.co/dataautogpt3/OpenDalleV1.1


from diffusers import AutoPipelineForText2Image
import torch


def ProteusV0_2(prompt: str, file_path, n_steps: int):

    pipeline = AutoPipelineForText2Image.from_pretrained(
        "dataautogpt3/ProteusV0.2",
        torch_dtype=torch.float16
    ).to('cuda')

    image = pipeline(prompt,
                    num_inference_steps=n_steps,
                    ).images[0]

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path

def OpenDalleV1_1(prompt: str, file_path, n_steps: int):

    pipeline = AutoPipelineForText2Image.from_pretrained(
        'dataautogpt3/OpenDalleV1.1',
        torch_dtype=torch.float16
    ).to('cuda')

    image = pipeline(prompt,
                    num_inference_steps=n_steps,
                    ).images[0]

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path
