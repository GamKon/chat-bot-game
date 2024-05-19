# https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0
# text-to-image diffusion model

# To use the whole base + refiner pipeline as an ensemble of experts you can run:

from diffusers import DiffusionPipeline, StableDiffusionXLPipeline
import torch

##########################################################################################################################################################

##########################################################################################################################################################
# base pipeline
def stable_diffusion_xl_base_1_0(prompt, file_path, n_steps: int):

##########################################################################################################################################################
# koala-1b-llava-cap
    # pipe = StableDiffusionXLPipeline.from_pretrained(
    #     "etri-vilab/koala-1b-llava-cap",
    #     torch_dtype=torch.float16)
    # pipe = pipe.to("cuda")

    # # prompt = "A portrait painting of a Golden Retriever like Leonard da Vinci"
    # negative = "worst quality, low quality, illustration, low resolution"
    # image = pipe(
    #     prompt=prompt,
    #     num_inference_steps=n_steps,
    #     negative_prompt=negative
    # ).images[0]


##########################################################################################################################################################
# stable-diffusion-xl-base-1.0
    # Stable diffusion pipeline
    pipe = DiffusionPipeline.from_pretrained(

        "stabilityai/stable-diffusion-xl-1.0-tensorrt",
        # "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16")
    pipe.to("cuda")

    # if using torch < 2.0
    # pipe.enable_xformers_memory_efficient_attention()

    # prompt = "An astronaut riding a green horse"

    #high_noise_frac = 0.8
    #n_steps = 40 # default 50

    image = pipe(
        prompt=prompt,
        num_inference_steps=n_steps,
#        denoising_end=high_noise_frac,
    ).images[0]

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path

##########################################################################################################################################################


##########################################################################################################################################################
# base + refiner pipeline
def stable_diffusion_xl_base_refiner_1_0(prompt, file_path, n_steps:int):
    # load both base & refiner
    base = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-base-1.0",
        torch_dtype=torch.float16,
        variant="fp16",
        use_safetensors=True
    )
    base.to("cuda")
    refiner = DiffusionPipeline.from_pretrained(
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        text_encoder_2=base.text_encoder_2,
        vae=base.vae,
        torch_dtype=torch.float16,
        use_safetensors=True,
        variant="fp16",
    )
    refiner.to("cuda")

    # Define how many steps and what % of steps to be run on each experts (80/20) here
    # n_steps = 40 # Default 75
    high_noise_frac = 0.8

#    prompt = "A majestic lion jumping from a big stone at night"

    # ! Crashes here:
    # base.unet = torch.compile(base.unet, mode="reduce-overhead", fullgraph=True)
    # refiner.unet = torch.compile(refiner.unet, mode="reduce-overhead", fullgraph=True)

    # run both experts
    image = base(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_end=high_noise_frac,
        output_type="latent",
    ).images
    image = refiner(
        prompt=prompt,
        num_inference_steps=n_steps,
        denoising_start=high_noise_frac,
        image=image,
    ).images[0]

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path
