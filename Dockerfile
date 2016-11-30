FROM python:2.7.12

EXPOSE 5001 5002 5003

ADD . /service
WORKDIR /service

RUN python setup.py install
