import requests
import argparse
import os
import time
import sys
from prometheus_client import start_http_server, Gauge

# ----------------------------- Argument Parsing -----------------------------
def get_config():
    parser = argparse.ArgumentParser(description="DigitalOcean Billing Exporter")

    parser.add_argument('--api-token', type=str, help='DigitalOcean API Token')
    parser.add_argument('--port', type=int, default=None, help='Port to expose Prometheus metrics')

    args = parser.parse_args()

    # Priority: CLI args > Env vars > Defaults
    api_token = args.api_token or os.getenv('DO_API_TOKEN')
    port = args.port or int(os.getenv('EXPORTER_PORT', 8000))

    if not api_token:
        print("❌ API token is required. Pass via --api-token or DO_API_TOKEN env variable.")
        sys.exit(1)

    return api_token, port

# ----------------------------- API Endpoints -----------------------------
url_projects = "https://api.digitalocean.com/v2/projects"
url_droplets = "https://api.digitalocean.com/v2/droplets"
url_databases = "https://api.digitalocean.com/v2/databases"
url_volumes = "https://api.digitalocean.com/v2/volumes"

# ----------------------------- Prometheus Gauges -----------------------------
droplet_cost_monthly = Gauge(
    'droplet_cost_monthly',
    'Monthly cost of the droplet',
    ['droplet_name', 'project', 'region', 'size', 'tags', 'role']
)
database_cost_monthly = Gauge(
    'database_cost_monthly',
    'Monthly cost of the database cluster',
    ['database_name', 'engine', 'region', 'size', 'num_nodes']
)
volume_cost_monthly = Gauge(
    'volume_cost_monthly',
    'Monthly cost of the volume',
    ['volume_name', 'region', 'size_gigabytes']
)

# ----------------------------- Static Pricing -----------------------------
pricing_model = {
    'db-s-1vcpu-1gb': 15.00,
    'db-s-1vcpu-2gb': 30.00,
    'db-s-2vcpu-4gb': 60.00,
    'so1_5-2vcpu-16gb': 212.00
}

# ----------------------------- API Calls -----------------------------
def get_projects(headers):
    response = requests.get(url_projects, headers=headers)
    return response.json().get('projects', []) if response.ok else []

def get_all_droplets(headers):
    droplets, page, per_page = [], 1, 200
    while True:
        response = requests.get(f"{url_droplets}?page={page}&per_page={per_page}", headers=headers)
        if not response.ok:
            break
        data = response.json().get('droplets', [])
        droplets.extend(data)
        if len(data) < per_page:
            break
        page += 1
    return droplets

def get_all_databases(headers):
    response = requests.get(url_databases, headers=headers)
    return response.json().get('databases', []) if response.ok else []

def get_all_volumes(headers):
    volumes, page, per_page = [], 1, 200
    while True:
        response = requests.get(f"{url_volumes}?page={page}&per_page={per_page}", headers=headers)
        if not response.ok:
            break
        data = response.json().get('volumes', [])
        volumes.extend(data)
        if len(data) < per_page:
            break
        page += 1
    return volumes

# ----------------------------- Metric Extraction -----------------------------
def extract_role(tags):
    for tag in tags:
        if 'role:' in tag.lower():
            return tag.split(':', 1)[1].strip()
    return 'Unknown'

def expose_droplet_metrics(headers):
    projects = get_projects(headers)
    project_names = [p['name'].lower() for p in projects]
    droplets = get_all_droplets(headers)

    for droplet in droplets:
        name = droplet['name']
        tags = droplet.get('tags', [])
        project = next((tag for tag in tags if tag.lower() in project_names), 'Unknown')
        role = extract_role(tags)

        region = f"{droplet['region']['name']} ({droplet['region']['slug']})"
        size = f"{droplet['size']['slug']} (vCPUs: {droplet['size']['vcpus']}, RAM: {droplet['size']['memory']} MB, Disk: {droplet['size']['disk']} GB)"
        cost = droplet['size']['price_monthly']
        tag_str = ', '.join(tags) if tags else 'None'

        droplet_cost_monthly.labels(name, project, region, size, tag_str, role).set(cost)

def expose_database_metrics(headers):
    for db in get_all_databases(headers):
        name, engine, region, size = db['name'], db['engine'], db['region'], db['size']
        nodes = db.get('num_nodes', 1)
        base_price = pricing_model.get(size)
        if base_price:
            cost = base_price * nodes
            database_cost_monthly.labels(name, engine, region, size, str(nodes)).set(cost)

def expose_volume_metrics(headers):
    for volume in get_all_volumes(headers):
        name, region, size_gb = volume['name'], volume['region']['slug'], volume['size_gigabytes']
        cost = size_gb * 0.10  # $0.10 per GB
        volume_cost_monthly.labels(name, region, size_gb).set(cost)

# ----------------------------- Prometheus Server -----------------------------
def start_prometheus_server(api_token, port):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}",
    }

    start_http_server(port)
    print(f"🚀 Your custom metrics exposed on port {port}...")

    while True:
        expose_droplet_metrics(headers)
        expose_database_metrics(headers)
        expose_volume_metrics(headers)
        time.sleep(600)

# ----------------------------- Main Entry -----------------------------
if __name__ == '__main__':
    api_token, port = get_config()
    start_prometheus_server(api_token, port)
