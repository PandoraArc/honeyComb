# Use an official Python runtime as a parent image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /app

# Copy the environment file into the container
COPY decimer.yml .

# Create the conda environment
RUN conda env create -f decimer.yml

# Activate the environment and ensure it's activated by default
SHELL ["conda", "run", "-n", "decimer", "/bin/bash", "-c"]

# Copy necessary files into the container
COPY classification.py .
COPY DECIMER_HandDrawn_model ./DECIMER_HandDrawn_model
COPY DECIMER_model ./DECIMER_model
COPY decimer.py .
COPY run.sh .
COPY segment_structures_in_document.py .
COPY ChemistryArt.png .
# COPY decimer .
# COPY DECIMER-Image-Segmentation .

# Ensure the script is executable
RUN chmod +x run.sh

# Use the default shell to install system-level packages
RUN apt-get update && apt-get install -y libgl1


#change module decimer
RUN rm /opt/conda/envs/decimer/lib/python3.10/site-packages/DECIMER/decimer.py
COPY decimer.py /opt/conda/envs/decimer/lib/python3.10/site-packages/DECIMER/



# Set the entry point to run the script using the conda environment
# ENTRYPOINT ["conda", "run", "-n", "decimer"]
ENTRYPOINT ["bash"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]
# ENTRYPOINT ["conda", "run", "-n", "decimer", "./run.sh"]


