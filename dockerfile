FROM python:3.12 AS chat-bot-ai

#install tools
RUN apt-get update && apt-get install --assume-yes \
    curl \
    nano \
    git
#     unzip

#RUN rm -rf /usr/lib/x86_64-linux-gnu/libnvidia-*.so* \
#           /usr/lib/x86_64-linux-gnu/libcuda.so*
#     /usr/lib/x86_64-linux-gnu/libnvcuvid.so* \
#     /usr/lib/x86_64-linux-gnu/libnvidia-*.so* \
#     /usr/local/cuda/compat/lib/*.515.65.01

# Create dir for storing models
RUN mkdir -p /root/.cache/huggingface

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

# Copy the requirements file
COPY requirements.txt .
# Install the dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt
RUN pip3 install --upgrade "git+https://github.com/huggingface/transformers" optimum

USER user

# Create directories for media files
RUN mkdir -p /app/db
RUN mkdir -p /app/models
RUN mkdir -p /app/keyboards
RUN mkdir -p /app/handlers
RUN mkdir -p /app/data/database

# Copy the application code

COPY ./db/*.py ./db/
COPY ./models/*.py ./models/
COPY ./keyboards/*.py ./keyboards/
COPY ./handlers/*.py ./handlers/
COPY ./main.py ./
COPY ./classes.py ./classes/


# Create dir for storing models
#RUN mkdir /root/.cache/huggingface
RUN mkdir -p /home/user/.cache/huggingface
# Run the application
#CMD ["python", "main.py"]
ENTRYPOINT ["tail", "-f", "/dev/null"]
