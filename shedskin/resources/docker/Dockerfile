FROM ubuntu:24.04

RUN echo 'debconf debconf/frontend select Noninteractive' | debconf-set-selections

RUN apt-get update
RUN apt-get install -y apt-utils
RUN apt-get install -y git g++ libpcre2-dev python3 python3-dev libgc-dev

WORKDIR /
RUN git clone https://github.com/shedskin/shedskin.git

WORKDIR shedskin
RUN python3 setup.py install
