# with out gpu
# FROM tensorflow/tensorflow:latest

# with gpu
FROM tensorflow/tensorflow:latest-gpu

WORKDIR /home

# create volume for the data
VOLUME /home/data

# Copy necessary files into the container
COPY . .
RUN pip install -r requirements.txt

# Set the entry point to run the script using the conda environment
# ENTRYPOINT ["conda", "run", "-n", "decimer"]
# ENTRYPOINT ["bash"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]


