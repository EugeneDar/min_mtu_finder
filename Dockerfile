FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip iputils-ping

WORKDIR /app

COPY main.py /app/main.py

ENTRYPOINT ["python3", "/app/main.py"]
