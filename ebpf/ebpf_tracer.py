import ctypes
import socket
import struct
import requests

from bcc import BPF
from datetime import datetime

def get_connection_latency():
    bpf_program = """
    #include <uapi/linux/ptrace.h>
    #include <linux/in.h>
    #include <linux/in6.h>
    #include <linux/socket.h>

    struct conn_info_t {
        u64 ts_start;
        u64 ts_established;
        u64 ts_end;
        u32 daddr;
        u16 dport;
    };

    BPF_HASH(start_times, u32, u64);
    BPF_HASH(conn_infos, u32, struct conn_info_t);
    BPF_PERF_OUTPUT(events);

    int trace_connect_entry(struct pt_regs *ctx, int sockfd, struct sockaddr __user *uservaddr, int addrlen) {
        u32 pid = bpf_get_current_pid_tgid();

        u64 ts = bpf_ktime_get_ns();
        start_times.update(&pid, &ts);

        struct sockaddr_in sa = {};
        bpf_probe_read_user(&sa, sizeof(sa), uservaddr);

        if (sa.sin_family == AF_INET) {
            struct conn_info_t info = {};
            info.ts_start = ts;
            info.daddr = sa.sin_addr.s_addr;
            info.dport = ntohs(sa.sin_port);
            conn_infos.update(&pid, &info);
        }

        return 0;
    }

    int trace_connect_return(struct pt_regs *ctx) {
        u32 pid = bpf_get_current_pid_tgid();
        start_times.delete(&pid); // Clean up; already stored in conn_infos
        return 0;
    }

    int trace_tcp_set_state(struct pt_regs *ctx, void *sk, int state) {
        if (state != 1) return 0; // TCP_ESTABLISHED = 1

        u32 pid = bpf_get_current_pid_tgid();
        struct conn_info_t *info = conn_infos.lookup(&pid);
        if (info) {
            info->ts_established = bpf_ktime_get_ns();
        }
        return 0;
    }

    int trace_tcp_close(struct pt_regs *ctx, void *sk) {
        u32 pid = bpf_get_current_pid_tgid();
        struct conn_info_t *info = conn_infos.lookup(&pid);
        if (info) {
            info->ts_end = bpf_ktime_get_ns();
            events.perf_submit(ctx, info, sizeof(*info));
            conn_infos.delete(&pid);
        }
        return 0;
    }
    """

    class ConnInfo(ctypes.Structure):
        _fields_ = [
            ("ts_start", ctypes.c_ulonglong),
            ("ts_established", ctypes.c_ulonglong),
            ("ts_end", ctypes.c_ulonglong),
            ("daddr", ctypes.c_uint32),
            ("dport", ctypes.c_uint16)
        ]

    def inet_ntoa(addr):
        return socket.inet_ntoa(struct.pack("I", addr))

    def handle_event(cpu, data, size):
        event = ctypes.cast(data, ctypes.POINTER(ConnInfo)).contents
        start = event.ts_start / 1e6
        est = event.ts_established / 1e6 if event.ts_established else 0
        end = event.ts_end / 1e6
        payload = {
            "handshake": est - start,
            "total": end - start
        }

        try:
            requests.post("http://central-dashboard.default.svc.cluster.local:5000/submit", json=payload)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] data sent to master succcessfully")
        except:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] request could not be sent")
            pass

    b = BPF(text=bpf_program)
    b.attach_kprobe(event="__sys_connect", fn_name="trace_connect_entry")
    b.attach_kretprobe(event="__sys_connect", fn_name="trace_connect_return")
    b.attach_kprobe(event="tcp_set_state", fn_name="trace_tcp_set_state")
    b.attach_kprobe(event="tcp_close", fn_name="trace_tcp_close")

    b["events"].open_perf_buffer(handle_event)
    print("Tracing full TCP connection lifecycle... Ctrl+C to exit.")
    while True:
        try:
            b.perf_buffer_poll()
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    print("starting ebpf tracer...")
    get_connection_latency()