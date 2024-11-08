from dash import dcc, html, Dash
from dash.dependencies import Input, Output
import requests
from datetime import datetime, timedelta
from flask import render_template_string,Flask

app = Dash(__name__, suppress_callback_exceptions=True)

# Layouts:

# Layout principal
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

cpu_layout = html.Div([
    dcc.Graph(
        id='cpu-usage-graph',
        config={'displayModeBar': False,
                'fillFrame':True,
                'responsive':True}
    ),
    dcc.Interval(id='cpu-interval', interval=30*1000, n_intervals=0)
])

memory_layout = html.Div([
    dcc.Graph(
        id='memory-usage-graph',
        config={'displayModeBar': False,
                'fillFrame':True,
                'responsive':True}
    ),
    dcc.Interval(id='memory-interval', interval=30*1000, n_intervals=0)
])

disk_layout = html.Div([
    dcc.Graph(
        id='disk-usage-graph',
        config={'displayModeBar': False,
                'fillFrame':True,
                'responsive':True}
    ),
    dcc.Interval(id='disk-interval', interval=30*1000, n_intervals=0)
])

network_layout = html.Div([
    dcc.Graph(
        id='network-usage-graph',
        config={'displayModeBar': False,
                'fillFrame':True,
                'responsive':True}
    ),
    dcc.Interval(id='network-interval', interval=30*1000, n_intervals=0)
])

# Callbacs para actualizar los gráficos

@app.callback(Output('cpu-usage-graph', 'figure'),
              Input('cpu-interval', 'n_intervals'))
def update_cpu_graph(n):
    query_url = "http://192.168.79.176:9090/api/v1/query_range"
    query = "rate(node_cpu_seconds_total[1m])"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=8)
    response = requests.get(query_url, params={
        'query': query,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': '1m' 
    })
    data = response.json()

    cpu_usage = {'time': [], 'value': []}
    for result in data['data']['result']:
        metric = result['metric']
        values = result['values']

        if metric.get('mode') != 'idle':
            for value in values:
                timestamp = datetime.fromtimestamp(float(value[0]))
                cpu_value = float(value[1])
                if timestamp not in cpu_usage['time']:
                    cpu_usage['time'].append(timestamp)
                    cpu_usage['value'].append(cpu_value)
                else:
                    index = cpu_usage['time'].index(timestamp)
                    cpu_usage['value'][index] += cpu_value
    cpu_usage['value'] = [v * 100 for v in cpu_usage['value']]

    figure = {
        'data': [{'x': cpu_usage['time'], 'y': cpu_usage['value'], 'type': 'line', 'name': 'CPU Usage'}],
        'layout':{
            'yaxis':{'title':'CPU%'},
            'autosize':True,
            'margin': {'t':0,'b':50,'r':20}
        }
    }
    return figure

@app.callback(Output('memory-usage-graph', 'figure'),
              Input('memory-interval', 'n_intervals'))
def update_memory_graph(n):
    query_url = "http://192.168.79.176:9090/api/v1/query_range"
    query_total = "node_memory_MemTotal_bytes"
    query_available = "node_memory_MemAvailable_bytes"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=8)

    # Obtener la memoria total
    response_total = requests.get(query_url, params={
        'query': query_total,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': '1m'
    })
    data_total = response_total.json()

    # Obtener la memoria disponible
    response_available = requests.get(query_url, params={
        'query': query_available,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': '1m'
    })
    data_available = response_available.json()

    memory_usage = {'time': [], 'value': []}
    for result_total, result_available in zip(data_total['data']['result'], data_available['data']['result']):
        values_total = result_total['values']
        values_available = result_available['values']
        for value_total, value_available in zip(values_total, values_available):
            timestamp = datetime.fromtimestamp(float(value_total[0]))
            mem_total = float(value_total[1])
            mem_available = float(value_available[1])
            mem_used = mem_total - mem_available
            memory_usage['time'].append(timestamp)
            memory_usage['value'].append(mem_used)

    figure = {
        'data': [{'x': memory_usage['time'], 'y': memory_usage['value'], 'type': 'line', 'name': 'Memory Used'}],
        'layout': {
            'yaxis': {'title': 'RAM (bytes)'},
            'autosize': True,
            'margin': {'t': 0, 'b': 50, 'r': 20}
        }
    }
    return figure


@app.callback(Output('disk-usage-graph', 'figure'),
              Input('disk-interval', 'n_intervals'))
def update_disk_io_graph(n):
    query_url = "http://192.168.79.176:9090/api/v1/query_range"
    query = "rate(node_disk_io_time_seconds_total[1m])"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=8)
    response = requests.get(query_url, params={
        'query': query,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': '1m'  # Intervalo de tiempo entre puntos de datos
    })
    data = response.json()

    disk_io = {'time': [], 'value': []}
    for result in data['data']['result']:
        values = result['values']
        for value in values:
            timestamp = datetime.fromtimestamp(float(value[0]))
            io_value = float(value[1])
            disk_io['time'].append(timestamp)
            disk_io['value'].append(io_value)

    figure = {
        'data': [{'x': disk_io['time'], 'y': disk_io['value'], 'type': 'line', 'name': 'Disk IO Time'}],
        'layout': {
            'yaxis': {'title': 'Disk IO Time (s)'},
            'autosize': True,
            'margin': {'t': 0, 'b': 50, 'r': 20}
        }
    }
    return figure

@app.callback(Output('network-usage-graph', 'figure'),
              Input('network-interval', 'n_intervals'))
def update_network_receive_graph(n):
    query_url = "http://192.168.79.176:9090/api/v1/query_range"
    query = "rate(node_network_receive_bytes_total[1m])"
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=8)
    response = requests.get(query_url, params={
        'query': query,
        'start': start_time.timestamp(),
        'end': end_time.timestamp(),
        'step': '1m'  # Intervalo de tiempo entre puntos de datos
    })
    data = response.json()

    network_receive = {'time': [], 'value': []}
    for result in data['data']['result']:
        values = result['values']
        for value in values:
            timestamp = datetime.fromtimestamp(float(value[0]))
            net_value = float(value[1])
            network_receive['time'].append(timestamp)
            network_receive['value'].append(net_value)

    figure = {
        'data': [{'x': network_receive['time'], 'y': network_receive['value'], 'type': 'line', 'name': 'Network Receive'}],
        'layout': {
            'yaxis': {'title': 'Red (bytes)'},
            'autosize': True,
            'margin': {'t': 0, 'b': 50, 'r': 20}
        }
    }
    return figure


# Callback para actualizar el contenido de la página
@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/cpu':
        return cpu_layout
    elif pathname == '/memory':
        return memory_layout
    elif pathname == '/disk':
        return disk_layout
    elif pathname == '/net':
        return network_layout
    else:
        return "404 Página no encontrada"

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
