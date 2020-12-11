FROM python:3.7-buster
LABEL maintainer="vadim@based.at"

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

COPY . /app/
COPY ./scripts/* /usr/local/bin/
WORKDIR /app

RUN rasa train

CMD ["run"]
