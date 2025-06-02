BPF Monitor

Python-based dashboard to visualize how long TCP connections take to establish

Setup

Building docker containers

for ebpf program per pod:
cd /ebpf
docker build -t michaelzheng67/ebpf-collector:latest .
docker push michaelzheng67/ebpf-collector:latest

same for centralized dashboard:
cd /backend
docker build -t michaelzheng67/ebpf-dashboard:latest .
docker push michaelzheng67/ebpf-dashboard:latest

if running on VM:
kubectl port-forward service/dashboard-nodeport 30080:5000

port forward the k8s port so that the dashboard is reachable from the host on localhost:30080
