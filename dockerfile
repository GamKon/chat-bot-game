FROM python:3.11.5 AS chat-bot-ai
# nvidia/cuda:12.3.1-runtime-ubuntu22.04

#FROM ghcr.io/ggerganov/llama.cpp:light-cuda AS chat-bot-ai


## GGUF To compile llama_cpp_python for cuda
##RUN wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
##RUN dpkg -i cuda-keyring_1.1-1_all.deb

#sudo apt-get update
#sudo apt-get -y install cuda-toolkit-12-3

#install tools
RUN apt-get update && apt-get install --assume-yes \
    curl \
    nano \
    git \
    ffmpeg \
    mc
    #    \
##    cuda-toolkit-12-3
#    nvtop

# To fix a bug in the nvidia driver installation
#RUN rm -rf /usr/lib/x86_64-linux-gnu/libnvidia-*.so* \
#           /usr/lib/x86_64-linux-gnu/libcuda.so*
#     /usr/lib/x86_64-linux-gnu/libnvcuvid.so* \
#     /usr/lib/x86_64-linux-gnu/libnvidia-*.so* \
#     /usr/local/cuda/compat/lib/*.515.65.01

# Copy the requirements file
COPY requirements.txt .
# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip install --upgrade "git+https://github.com/huggingface/transformers" optimum

# Flash attention
#RUN CUDA_HOME=/usr/lib/nvidia-cuda-toolkit
##RUN pip install flash-attn --no-build-isolation

# llama.cpp
##RUN CUDACXX=/usr/local/cuda-12/bin/nvcc CMAKE_ARGS="-DLLAMA_CUBLAS=on -DCMAKE_CUDA_ARCHITECTURES=all" FORCE_CMAKE=1 pip install llama-cpp-python --no-cache-dir --force-reinstall --upgrade
#  nvcc --list-gpu-arch
# -DCMAKE_CUDA_ARCHITECTURES=!!native/all/86

# Create user
RUN useradd -m -u 1000 user

# Set the working directory
WORKDIR /app

# Install CrOps Team
ARG OPS_VERSION="2.3.2"
RUN curl -fsSL "https://github.com/nickthecook/crops/releases/download/${OPS_VERSION}/crops.tar.bz2" \
    | tar xj --strip-components=3 -C /usr/local/bin crops/build/linux_x86_64/ops
#Copy ops.yml file
COPY ops_for_image.yml ./ops.yml

# Create dir for storing models
#RUN mkdir -p /root/.cache/huggingface

# Create app directories
RUN mkdir -p /app/db
RUN mkdir -p /app/models
RUN mkdir -p /app/keyboards
RUN mkdir -p /app/handlers
RUN mkdir -p /app/data/voice
RUN mkdir -p /app/data/generated_images
RUN mkdir -p /app/llama_cpp

# Copy the application code
COPY ./db/*.py ./db/
COPY ./models/*.py ./models/
COPY ./keyboards/*.py ./keyboards/
COPY ./handlers/*.py ./handlers/
COPY ./main.py ./
COPY ./classes.py ./
COPY ./templating.py ./
COPY ./utility.py ./

# Copy precompiled llama_cpp_python with CUDA GPU support
COPY ./llama_cpp/ /usr/local/lib/python3.11/site-packages/llama_cpp/

# RUN chown -R user:user /app
# RUN chown -R user:user /home/user
RUN chmod -R 777 /app
USER user
RUN mkdir -p /home/user/.cache/huggingface
RUN mkdir -p /home/user/.cache/torch/kernels
#RUN mkdir -p /home/user/models
# Run the application
# CMD ["python", "main.py"]
ENTRYPOINT ["tail", "-f", "/dev/null"]
