FROM tensorflow/tensorflow:2.12.0

WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libmagic1 libgl1

# load weights model
RUN gdown https://drive.google.com/uc?id=1X00tXxqvbJNnaLJybVGQD00c1UYUe7SG -O /home/decimer_segmentation/mask_rcnn_molecule.h5


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]