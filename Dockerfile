FROM ubuntu:16.04


RUN apt update && apt install -y virtualenv ffmpeg libchromaprint-tools git bash-completion

RUN useradd -m bot

USER bot

WORKDIR /home/bot/
RUN git clone https://github.com/LoveIsGrief/reddit-whatsongisthis-bot.git

WORKDIR reddit-whatsongisthis-bot
RUN virtualenv -p python3 env
RUN env/bin/pip install -r requirements.txt

SHELL ["/bin/bash", "-c"]
RUN source env/bin/activate
