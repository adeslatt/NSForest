FROM continuumio/miniconda3:latest

WORKDIR /app

# Install emacs at OS level
RUN apt-get update && \
    apt-get install -y emacs && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY nsforest.yml .

RUN conda env create -f nsforest.yml

# Activate and install NSForest
COPY . .

RUN /bin/bash -c "source activate nsforest && pip install ."

CMD ["/bin/bash"]

