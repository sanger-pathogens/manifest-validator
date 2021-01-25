FROM ubuntu:bionic-20200403

# check xlrd compatibility before upgradung ubuntu base image or python

LABEL maintainer=path-help@sanger.ac.uk
ENV   DEBIAN_FRONTEND="noninteractive"

ARG BUILD_DIR=/opt/manifest-validator

RUN apt update -qq -y && \
    apt install -y \
    python3=3.6.7-1~18.04 \
    python3-setuptools \
    python3-pip

RUN mkdir -p $BUILD_DIR
COPY . $BUILD_DIR
RUN cd $BUILD_DIR \
    && python3 setup.py test \
    && python3 setup.py install

