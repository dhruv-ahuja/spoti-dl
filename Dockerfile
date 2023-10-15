FROM ubuntu:20.04

RUN sudo apt install -y perl cpanminus libssl-dev pkg-config librust-openssl-dev && sudo cpanm IPC::Cmd

WORKDIR /output
CMD perl -V > perl_version_output.txt


WORKDIR /app 
