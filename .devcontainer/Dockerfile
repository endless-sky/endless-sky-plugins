FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN set -ex; \
apt-get update; \
apt-get install -y git python3 python3.8-venv vim

RUN set -ex; \
yes | adduser es-user;

USER es-user

WORKDIR /home/es-user

ADD scripts/requirements.txt /home/es-user/requirements.txt

RUN set -ex; \
python3 -m venv ~/.pyenv; \
/bin/bash -exlc 'source ~/.pyenv/bin/activate; pip install -r requirements.txt'; \
echo 'source ~/.pyenv/bin/activate' > ~/.bashrc; \
echo 'source ~/.pyenv/bin/activate' > ~/.bash_profile


CMD /bin/bash
