Cloud & Region

Cloud: Google Cloud Platform (GCP)

Region: us-central1

Services used: Compute Engine VM (self-managed MySQL), Cloud SQL for MySQL (managed)

How to Reproduce

Create a VM (Ubuntu) on Compute Engine with ports 22 and 3306 open.

Install MySQL on the VM (apt install mysql-server).

Run mysql_secure_installation.

Edit MySQL config (bind-address = 0.0.0.0) and restart service.

Create MySQL user + database on VM.

Create Cloud SQL for MySQL instance with public IP + authorized networks.

Create user + database on Cloud SQL.

Add secrets to .env (not committed).

Run python scripts/vm_demo.py.

Run python scripts/managed_demo.py.

Connection String Pattern

VM:
mysql+pymysql://USER:PASS@VM_IP:3306/DBNAME

Managed:
mysql+pymysql://USER:PASS@CLOUDSQL_IP:3306/DBNAME

Secrets stored in .env using variables:
VM_DB_HOST, VM_DB_USER, VM_DB_PASS, VM_DB_NAME
MAN_DB_HOST, MAN_DB_USER, MAN_DB_PASS, MAN_DB_NAME

Screenshots Included

screenshots/vm/: VM creation, firewall, MySQL install, MySQL prompt.

screenshots/managed/: Cloud SQL creation, public IP, authorized networks, SQL query page.

Python output of successful vm_demo.py and managed_demo.py.