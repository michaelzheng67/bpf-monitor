import math

from collections import deque
from datetime import datetime
from flask import Flask, render_template_string, request
from time import strftime

app = Flask(__name__)

q = deque()

@app.route("/")
def dashboard():

    conn_times = []
    for r in list(q):
        try:
            t = float(r['total'])
            if t >= 0:
                conn_times.append(t)
        except (TypeError, ValueError):
            continue
    
    q.clear()

    bin_size = 10 # ms
    if conn_times:
        max_time = max(conn_times)
        num_bins = math.ceil(max_time / bin_size)
        bins = [0] * (num_bins + 1)
        labels = [f"{i*bin_size}-{(i+1)*bin_size}ms" for i in range(len(bins))]

        for t in conn_times:
            try:
                index = min(int(t // bin_size), len(bins) - 1)
                bins[index] += 1
            except (TypeError, ValueError):
                continue
    else:
        bins = []
        labels = []

    return render_template_string("""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>
    </head>
    <body>
        <h1>TCP Connection Time Histogram</h1>
        <div>
            <a href="/">[Total Times]</a> |
            <a href="/handshake-times">[Handshake Times]</a>
        </div>                    
        <canvas id="latencyChart" width="800" height="400"></canvas>
        <script>
            Chart.register(ChartDataLabels);

            const ctx = document.getElementById('latencyChart').getContext('2d');
            const data = {
                labels: {{ labels | tojson }},
                datasets: [
                    {
                        label: 'Handshake Count',
                        data: {{ bins | tojson }},
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        minBarLength: 3  // ensures visibility
                    }
                ]
            };

            new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Histogram of TCP Handshake Times'
                        },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: function(value) {
                                return value > 0 ? value : '';
                            },
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Handshake Duration (ms)'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grace: '10%',  // adds space above tallest bar
                            title: {
                                display: true,
                                text: 'Number of Connections'
                            }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
        </script>
    </body>
    </html>
    """, labels=labels, bins=bins)

@app.route("/handshake-times")
def handshake_dashboard():

    handshake_times = []
    for r in list(q):
        try:
            t = float(r['handshake'])
            if t >= 0:
                handshake_times.append(t)
        except (TypeError, ValueError):
            continue

    bin_size = 10 # ms
    if handshake_times:
        max_time = max(handshake_times)
        num_bins = math.ceil(max_time / bin_size)
        bins = [0] * (num_bins + 1)
        labels = [f"{i*bin_size}-{(i+1)*bin_size}ms" for i in range(len(bins))]

        for t in handshake_times:
            try:
                index = min(int(t // bin_size), len(bins) - 1)
                bins[index] += 1
            except (TypeError, ValueError):
                continue
    else:
        bins = []
        labels = []

    return render_template_string("""
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels"></script>
    </head>
    <body>
        <h1>TCP Handshake Time Histogram</h1>
        <div>
            <a href="/">[Total Times]</a> |
            <a href="/handshake-times">[Handshake Times]</a>
        </div>                    
        <canvas id="latencyChart" width="800" height="400"></canvas>
        <script>
            Chart.register(ChartDataLabels);

            const ctx = document.getElementById('latencyChart').getContext('2d');
            const data = {
                labels: {{ labels | tojson }},
                datasets: [
                    {
                        label: 'Handshake Count',
                        data: {{ bins | tojson }},
                        backgroundColor: 'rgba(54, 162, 235, 0.7)',
                        minBarLength: 3  // ensures visibility
                    }
                ]
            };

            new Chart(ctx, {
                type: 'bar',
                data: data,
                options: {
                    responsive: true,
                    plugins: {
                        title: {
                            display: true,
                            text: 'Histogram of TCP Handshake Times'
                        },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: function(value) {
                                return value > 0 ? value : '';
                            },
                            font: {
                                weight: 'bold'
                            }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Handshake Duration (ms)'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grace: '10%',  // adds space above tallest bar
                            title: {
                                display: true,
                                text: 'Number of Connections'
                            }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });
        </script>
    </body>
    </html>
    """, labels=labels, bins=bins)

@app.route("/submit", methods=["POST"])
def receive_data():
    record = request.get_json()
    q.append(record)
    return "ok"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
