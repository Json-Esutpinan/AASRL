from dash import Dash, html, dcc, Input, Output
import requests
from datetime import datetime, timedelta
from .server_model import ServerModel

class Graphs:
    def create_dash(self,flask_app):
        app = Dash(
            server = flask_app,
            name="Graphs",
            url_base_pathname="/graphs/"
        )
        
        app.layout = html.Div([
            dcc.Location(id='url', refresh=False),
            html.Div(id='page-content')
        ])
        server_model = ServerModel()
        hosts = server_model.get_servers()

        # Función para generar el layout para cada host
        def cpu_layout(host_index):
            return html.Div([
                dcc.Graph(
                    id=f'cpu-usage-graph-{host_index}',
                    config={'displayModeBar': False, 'fillFrame': True, 'responsive': True}
                ),
                dcc.Interval(id=f'cpu-interval-{host_index}', interval=20 * 1000, n_intervals=0)
            ])
        def memory_layout(host_index):
            return html.Div([
                dcc.Graph(
                    id=f'memory-usage-graph-{host_index}',
                    config={'displayModeBar': False, 
                            'fillFrame': True, 
                            'responsive': True}
                ),
                dcc.Interval(id=f'memory-interval-{host_index}', interval=20 * 1000, n_intervals=0)
            ])
        def disk_layout(host_index):
            return html.Div([
                dcc.Graph(
                    id=f'disk-usage-graph-{host_index}',
                    config={'displayModeBar': False, 
                            'fillFrame': True, 
                            'responsive': True}
                ),
                dcc.Interval(id=f'disk-interval-{host_index}', interval=20 * 1000, n_intervals=0)
            ])
        def network_layout(host_index):
            return html.Div([
                dcc.Graph(
                    id=f'network-usage-graph-{host_index}',
                    config={'displayModeBar': False, 
                            'fillFrame': True, 
                            'responsive': True}
                ),
                dcc.Interval(id=f'network-interval-{host_index}', interval=20 * 1000, n_intervals=0)
            ])

        # Callback para manejar rutas dinámicas
        @app.callback(Output('page-content', 'children'),
                    Input('url', 'pathname'))
        def display_page(pathname): 
            global hosts 
            hosts = server_model.get_servers()
            if pathname.startswith('/graphs/cpu'): 
                try: 
                    host_index = int(pathname[len('/graphs/cpu'):]) - 1 
                    if 0 <= host_index < len(hosts): 
                        return cpu_layout(host_index) 
                except ValueError: 
                    return html.H3("Ruta inválida") 
            elif pathname.startswith('/graphs/memory'): 
                try: 
                    host_index = int(pathname[len('/graphs/memory'):]) - 1 
                    if 0 <= host_index < len(hosts): 
                        return memory_layout(host_index) 
                except ValueError: 
                    return html.H3("Ruta inválida") 
            elif pathname.startswith('/graphs/disk'): 
                try: 
                    host_index = int(pathname[len('/graphs/disk'):]) - 1 
                    if 0 <= host_index < len(hosts): 
                        return disk_layout(host_index) 
                except ValueError: return html.H3("Ruta inválida") 
            elif pathname.startswith('/graphs/net'): 
                try: 
                    host_index = int(pathname[len('/graphs/net'):]) - 1 
                    if 0 <= host_index < len(hosts): 
                        return network_layout(host_index) 
                except ValueError: 
                    return html.H3("Ruta inválida") 
            else: 
                return html.H3("404")

        # Callback para actualizar la gráfica de CPU
        for i, host in enumerate(hosts):
            @app.callback(
                Output(f'cpu-usage-graph-{i}', 'figure'),
                Input(f'cpu-interval-{i}', 'n_intervals'),
            )
            def update_cpu_graph(n_intervals, host=host['host']):
                query_url = f"http://{host}:9090/api/v1/query_range"
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

                # Convertir a porcentaje
                cpu_usage['value'] = [v * 100 for v in cpu_usage['value']]

                figure = {
                    'data': [{'x': cpu_usage['time'], 'y': cpu_usage['value'], 'type': 'line', 'name': f'CPU Usage {host}'}],
                    'layout': {
                        'yaxis': {'title': 'CPU%'},
                        'autosize': True,
                        'margin': {'t': 10, 'b': 50, 'r': 20}
                    }
                }
                return figure

            @app.callback(Output(f'memory-usage-graph-{i}', 'figure'),
                    Input(f'memory-interval-{i}', 'n_intervals'))
            def update_memory_graph(n_intervals,host=host['host']):
                query_url = f"http://{host}:9090/api/v1/query_range"
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
                        'margin': {'t': 10, 'b': 50, 'r': 20}
                    }
                }
                return figure
            
            @app.callback(Output(f'disk-usage-graph-{i}', 'figure'),
                    Input(f'disk-interval-{i}', 'n_intervals'))
            def update_disk_io_graph(n_intervlas,host=host['host']):
                query_url = f"http://{host}:9090/api/v1/query_range"
                query = "rate(node_disk_io_time_seconds_total[1m])"
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=8)
                response = requests.get(query_url, params={
                    'query': query,
                    'start': start_time.timestamp(),
                    'end': end_time.timestamp(),
                    'step': '1m'
                })
                data = response.json()

                disk_io = {'time': [], 'value': []}
                for result in data['data']['result']:
                    values = result['values']
                    for value in values:
                        timestamp = datetime.fromtimestamp(float(value[0]))
                        io_value = float(value[1])
                        if timestamp not in disk_io['time']:
                            disk_io['time'].append(timestamp)
                            disk_io['value'].append(io_value)
                        else:
                            index = disk_io['time'].index(timestamp)
                            disk_io['value'][index] += io_value

                figure = {
                    'data': [{'x': disk_io['time'], 'y': disk_io['value'], 'type': 'line', 'name': 'Disk IO Time'}],
                    'layout': {
                        'yaxis': {'title': 'Disk IO Time(s)'},
                        'autosize': True,
                        'margin': {'t': 10, 'b': 50, 'r': 20}
                    }
                }
                return figure
            
            @app.callback(Output(f'network-usage-graph-{i}', 'figure'),
                    Input(f'network-interval-{i}', 'n_intervals'))
            def update_network_receive_graph(n_intervals,host=host['host']):
                query_url = f"http://{host}:9090/api/v1/query_range"
                query = "rate(node_network_receive_bytes_total[1m])"
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=8)
                response = requests.get(query_url, params={
                    'query': query,
                    'start': start_time.timestamp(),
                    'end': end_time.timestamp(),
                    'step': '1m'
                })
                data = response.json()

                network_receive = {'time': [], 'value': []}
                for result in data['data']['result']:
                    values = result['values']
                    for value in values:
                        timestamp = datetime.fromtimestamp(float(value[0]))
                        net_value = float(value[1])
                        if timestamp not in network_receive['time']:
                            network_receive['time'].append(timestamp)
                            network_receive['value'].append(net_value)
                        else:
                            index = network_receive['time'].index(timestamp)
                            network_receive['value'][index] += net_value

                figure = {
                    'data': [{'x': network_receive['time'], 'y': network_receive['value'], 'type': 'line', 'name': 'Network Receive'}],
                    'layout': {
                        'yaxis': {'title': 'Bytes Recibidos'},
                        'autosize': True,
                        'margin': {'t': 10, 'b': 50, 'r': 20}
                    }
                }
                return figure
        return app