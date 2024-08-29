FROM tensorflow/tensorflow:2.13.0

WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y libmagic1

# Set the entry point to run the script using the conda environment
# ENTRYPOINT ["conda", "run", "-n", "decimer"]
# ENTRYPOINT ["bash"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]