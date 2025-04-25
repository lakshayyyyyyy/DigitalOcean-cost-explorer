
# DigitalOcean Billing Exporter

Exports **DigitalOcean Droplet**, **Database**, and **Volume** costs as **Prometheus metrics**, enabling real-time cost monitoring with Prometheus, Grafana, and other monitoring tools.

### ✨ Features
- Export monthly cost of all active **Droplets**
- Export monthly cost of all active **Databases**
- Export monthly cost of all **Block Storage Volumes**
- Fully **scrape-ready** for Prometheus
- Lightweight and easy to run
- Supports **CLI arguments** and **Environment Variables** for configuration

### ⚙️ Usage
You can run the exporter either using CLI arguments or environment variables.

Can be executed from python as well the below example shows for already created executable file

---

```
./DigitalOcean-cost-explorer --api-token YOUR_DIGITALOCEAN_API_TOKEN --port 8000
```
---

```
export DO_API_TOKEN=YOUR_DIGITALOCEAN_API_TOKEN
export EXPORTER_PORT=8000
./DigitalOcean-cost-explorer
```
### Configuration Options

The DigitalOcean Billing Exporter supports two ways to configure settings:

- Using **Command Line Arguments (CLI flags)**
- Using **Environment Variables**

---

### 🛠 CLI Arguments

You can pass the required options when running the script manually.

| Argument        | Type    | Description                                      | Default    |
|-----------------|---------|--------------------------------------------------|------------|
| `--api-token`   | String  | Your DigitalOcean API token.                     | **(Required)** if env var is not set |
| `--port`        | Integer | Port number to expose Prometheus metrics server. | `8000`     |

### Example usage:

```bash
python exporter/billing_exporter.py --api-token YOUR_DIGITALOCEAN_API_TOKEN --port 8000
```
---

## ⚡ Priority Rule

**If you provide both CLI arguments and Environment Variables, CLI arguments will always take priority** .
