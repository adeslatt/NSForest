# Use the latest official miniconda3 image as the base
FROM continuumio/miniconda3:latest

# Set the working directory
WORKDIR /app

# Copy the NSForest repository contents into the container
COPY . .

# Create the nsforest environment using the provided YAML file
RUN conda env create -f nsforest.yml

# Activate the environment and install NSForest
RUN /bin/bash -c "source activate nsforest && pip install ."

# Set the default command to run when the container starts
CMD ["/bin/bash"]

