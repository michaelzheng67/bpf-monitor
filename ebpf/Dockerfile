FROM ubuntu:22.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 python3-pip bpfcc-tools linux-headers-$(uname -r) \
    python3-bpfcc python3-flask \
    gcc make libelf-dev iproute2 net-tools curl

COPY ebpf_tracer.py /ebpf_tracer.py

RUN pip3 install flask requests

ENTRYPOINT ["python3", "/ebpf_tracer.py"]