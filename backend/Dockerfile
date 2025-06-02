FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3-pip curl \
    && rm -rf /var/lib/apt/lists/*

COPY app.py /app.py

RUN pip3 install flask requests

EXPOSE 5000

ENTRYPOINT ["python3", "/app.py"]
