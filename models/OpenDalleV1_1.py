# https://huggingface.co/dataautogpt3/OpenDalleV1.1


from diffusers import AutoPipelineForText2Image
import torch


def ProteusV0_2(prompt: str, file_path, n_steps: int):

    from diffusers import (
    StableDiffusionXLPipeline,
    KDPM2AncestralDiscreteScheduler,
    AutoencoderKL
    )

    # Load VAE component
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix",
        torch_dtype=torch.float16
    )

    # Configure the pipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "dataautogpt3/ProteusV0.2",
        vae=vae,
        torch_dtype=torch.float16
    )
    pipe.scheduler = KDPM2AncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.to('cuda')

    # Define prompts and generate image
    prompt = "best quality, HD, ~*~aesthetic~*~, "+ prompt
    # prompt = "black fluffy gorgeous dangerous cat animal creature, large orange eyes, big fluffy ears, piercing gaze, full moon, dark ambiance, best quality, extremely detailed"

    negative_prompt = "bad quality, bad anatomy, worst quality, low quality, low resolutions, extra fingers, blur, blurry, ugly, wrongs proportions, watermark, image artifacts, lowres, ugly, jpeg artifacts, deformed, noisy image"

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        width=1024,
        height=1024,
        guidance_scale=7.5,
        num_inference_steps=n_steps
    ).images[0]

    # prompt = "best quality, HD, ~*~aesthetic~*~, "+ prompt
    # pipeline = AutoPipelineForText2Image.from_pretrained(
    #     #"cagliostrolab/animagine-xl-3.1",
    #     "dataautogpt3/ProteusV0.2",
    #     torch_dtype=torch.float16
    # ).to('cuda')

    # image = pipeline(prompt,
    #                 num_inference_steps=n_steps,
    #                 ).images[0]

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path

def OpenDalleV1_1(prompt: str, file_path, n_steps: int):

    pipeline = AutoPipelineForText2Image.from_pretrained(
        #"stabilityai/sdxl-turbo",
        "dataautogpt3/OpenDalleV1.1",
        #"dataautogpt3/ProteusV0.4",
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
