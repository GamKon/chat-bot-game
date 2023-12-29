# https://huggingface.co/Linaqruf/animagine-xl-2.0
#Linaqruf/animagine-xl-2.0


import torch
from diffusers import (
    StableDiffusionXLPipeline,
    EulerAncestralDiscreteScheduler,
    AutoencoderKL
)
async def animagine_xl_2_0(prompt: str, file_path, n_steps: int):
    # Load VAE component
    vae = AutoencoderKL.from_pretrained(
        "madebyollin/sdxl-vae-fp16-fix",
        torch_dtype=torch.float16
    )

    # Configure the pipeline
    pipe = StableDiffusionXLPipeline.from_pretrained(
        "Linaqruf/animagine-xl-2.0",
        vae=vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16"
    )
    pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)
    pipe.to('cuda')

    # Define prompts and generate image
    #prompt = "face focus, cute, masterpiece, best quality, 1girl, green hair, sweater, looking at viewer, upper body, beanie, outdoors, night, turtleneck"
    negative_prompt = "lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry"

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        width=1024,
        height=1024,
        guidance_scale=12,
        num_inference_steps=n_steps #50
    ).images[0]

# Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path
