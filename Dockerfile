FROM ubuntu:20.04

RUN apt-get update && apt-get install -y \
    git \
    python3.8 \
    python3-pip \
    protobuf-compiler \
    vim

# install protobuf python module
RUN python3 -m pip install protobuf==3.20.*

# clone repo
RUN git clone https://github.com/giuliagerometta/xapp-oai.git /xapp-oai
WORKDIR /xapp-oai

# checkout mrn-base
RUN git checkout mrn-base

# synch submodules
RUN chmod +x submodule-sync.sh
RUN ./submodule-sync.sh

# Create a text file
RUN echo "Helloooo." > sample.txt

ENTRYPOINT ["/bin/bash"]
