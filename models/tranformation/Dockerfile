# with gpu
FROM tensorflow/tensorflow:2.12.0

# Install OpenGL library
RUN apt-get update && apt-get install -y libgl1-mesa-glx


WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt


