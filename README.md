# BPF Monitor

Centralized dashboard to monitor your TCP connections in K8s 🐙

## Setup

Building docker containers

for ebpf program per pod:

```
cd /ebpf
docker build -t michaelzheng67/ebpf-collector:latest .
docker push michaelzheng67/ebpf-collector:latest
```

same for centralized dashboard:

```
cd /backend
docker build -t michaelzheng67/ebpf-dashboard:latest .
docker push michaelzheng67/ebpf-dashboard:latest
```

if running on VM:

```
kubectl port-forward service/dashboard-nodeport 30080:5000
```

port forward the k8s port so that the dashboard is reachable from the host on localhost:30080

to test using fake workload, run the test_pod.yaml which instantiates a pod that makes a curl
request every 5 seconds. The ebpf tracer will keep track of these calls and forward them to the
central dashboard.

## Technical Design

The main technology that the bpf monitor leverages is ebpf, the ability to essentially "peek"
inside the kernel at runtime and see what syscalls are being made. We are able to run
a daemonset which monitors the given node and sends back its monitoring data to a central
dashboard to be displayed.

The linux syscalls that are tracked are sys_connect, tcp_set_state, and tcp_close. sys_connect
is an identifier for the 'connect()' function that allows one socket to establish a connection
with another. The tcp_set_state and tcp_close are tcp tracepoints which tell us when a given
tcp connection changes state and when it closes respectively.

Screenshot:

![Screenshot 2025-06-03 at 11 27 07 AM](https://github.com/user-attachments/assets/e62dc200-5daa-4280-b729-044af21c21b3)

## Takeaways from tracking TCP connections

TCP connection time (i.e. time to complete HTTP request / response) follows a long tail
distribution, with a majority of requests being quick, and a few requests taking much longer.
This was expected as the majority of our fake curl requests would complete without issue,
while a few may experience additional latency for whatever reason (i.e. congested network,
client / server-side issues, etc).

It was also worth noting that a large majority of the time was spent on the actual request /
response portion of an HTTP request, with a small amount being the handshake time. Although small,
it was still non-negligible (few ms).
