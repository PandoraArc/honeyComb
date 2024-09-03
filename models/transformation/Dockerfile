# with gpu
FROM tensorflow/tensorflow:2.12.0

# Install OpenGL library
RUN apt-get update && apt-get install -y libgl1-mesa-glx libmagic1


WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .

RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt

RUN mkdir -p /root/.data/DECIMER-V2
RUN gdown https://drive.google.com/uc?id=1SaCURxgqb0O6D9KnDgX4PrDDjf5mLTXv -O /root/.data/DECIMER-V2/DECIMER_model.zip
RUN gdown https://drive.google.com/uc?id=1TZQtVsYn6R5kWtAZ_g3EDAL-i1tFIjxY -O /root/.data/DECIMER-V2/DECIMER_HandDrawn_model.zip
RUN unzip /root/.data/DECIMER-V2/DECIMER_model.zip -d /root/.data/DECIMER-V2/
RUN unzip /root/.data/DECIMER-V2/DECIMER_HandDrawn_model.zip -d /root/.data/DECIMER-V2/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
