# with gpu
FROM tensorflow/tensorflow:2.12.0

# Install OpenGL library
RUN apt-get update && apt-get install -y libgl1-mesa-glx libmagic1


WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .

# COPY ./app /home/app

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]