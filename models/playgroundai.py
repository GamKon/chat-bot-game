#https://huggingface.co/playgroundai/playground-v2.5-1024px-aesthetic
# playgroundai/playground-v2.5-1024px-aesthetic

from diffusers import DiffusionPipeline
import torch


def playground_v2_5_1024px_aesthetic(prompt: str, file_path, n_steps: int):

    pipe = DiffusionPipeline.from_pretrained(
        # "playgroundai/playground-v2-1024px-aesthetic",
        # "playgroundai/playground-v2.5-1024px-aesthetic",
        "stabilityai/stable-diffusion-3-medium-diffusers",
        torch_dtype=torch.float16,
#        use_safetensors=True,
#        add_watermarker=False,
#        variant="fp16",
    )
    pipe.to("cuda")

    #prompt = "Astronaut in a jungle, cold color palette, muted colors, detailed, 8k"
    image  = pipe(prompt=prompt,
                num_inference_steps=n_steps,
                guidance_scale=3).images[0]

    # print(image)
    # print(type(image))
    # image.save("test.png")
    # return "test.png"

    # Save image
    prompt = prompt[:70]
    prompt = prompt.replace(",", "")
    image_name  = prompt.replace(" ", "_")+".png"
    full_path   = file_path+"/"+image_name
    image.save(full_path)
    return full_path

#stabilityai/stable-diffusion-3-medium