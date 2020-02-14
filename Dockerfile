FROM ubuntu:18.04

ARG BUILD_DIR=/opt/manifest-validator

RUN apt update -qq -y && \
    apt upgrade -qq -y && \
    apt install -y \
    python3 \
    python3-setuptools \
    python3-pip

RUN mkdir -p $BUILD_DIR
COPY . $BUILD_DIR
RUN cd $BUILD_DIR \
    && python3 setup.py test \
    && python3 setup.py install

