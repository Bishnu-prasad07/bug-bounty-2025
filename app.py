from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess
import whois
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return render_template('ping.html')

@app.route('/whois')
def whoisdomain():
    return render_template('whois.html')

@app.route('/ip_lookup')
def iplookup():
    return render_template('ip_lookup.html')

@app.route('/certificate_search')
def crtsh():
    return render_template('certificate_search.html')

@app.route('/open_ports')
def openports():
    return render_template('open_ports.html')

@app.route('/recon')
def recon():
    return render_template('recon.html')

@socketio.on('start_ping')
def start_ping(data):
    domain = data['domain']
    with subprocess.Popen(['ping', '-c', '4', domain], stdout=subprocess.PIPE, bufsize=1, universal_newlines=True) as p:
        for line in p.stdout:
            emit('ping_update', {'data': line.strip()})
    emit('ping_update', {'data': 'Ping Finished'})

@socketio.on('start_iplookup')
def start_iplookup(data):
    ipAddress = data['ipAddress']
    ip = subprocess.run(['curl', f'http://ip-api.com/json/{ipAddress}'], stdout=subprocess.PIPE, text=True)
    emit('iplookup_update', {'data': ip.stdout})

@socketio.on('start_whois')
def start_whois(data):
    domain = data['domain']
    domain_info = whois.whois(domain)
    emit('whois_update', {'data': str(domain_info)})

@socketio.on('start_crtsh')
def start_crtsh(data):
    domain = data['domain']
    crtsh_info = subprocess.run(['curl', f'https://crt.sh/?q=%.{domain}&output=json'], stdout=subprocess.PIPE, text=True)
    emit('crtsh_update', {'data': crtsh_info.stdout})

@socketio.on('start_openports')
def start_openports(data):
    domain = data['domain']
    open_ports = subprocess.run(['nmap', '-F', domain], stdout=subprocess.PIPE, text=True)
    emit('openports_update', {'data': open_ports.stdout})

@socketio.on('start_recon')
def start_recon(data):
    org_name = data['org_name']
    domains = data['domains']
    recon_folder = 'recon'
    os.makedirs(recon_folder, exist_ok=True)

    # create orgs.txt if it doesn't exist
    orgs_file_path = os.path.join(recon_folder, 'orgs.txt')
    if not os.path.exists(orgs_file_path):
        with open(orgs_file_path, 'w') as f:
            pass
    
    # Check if org_name already exists in orgs.txt
    orgs_file_path = os.path.join(recon_folder, 'orgs.txt')
    with open(orgs_file_path, 'r') as orgs_file:
        existing_orgs = orgs_file.read().splitlines()
    if org_name in existing_orgs:
        org_folder = os.path.join(recon_folder, org_name)
        domains_file_path = os.path.join(org_folder, 'domains.txt')
        
        # Check if domains file exists
        if os.path.exists(domains_file_path):
            with open(domains_file_path, 'r') as domains_file:
                existing_domains = domains_file.read().splitlines()
            for domain in domains:
                if domain not in existing_domains:
                    with open(domains_file_path, 'a') as f:
                        f.write(domain + '\n')
                    emit('recon_update', {'data': f'Domain {domain} added to {org_name}'})
                else:
                    emit('recon_update', {'data': f'Domain {domain} already exists in {org_name}'})
        else:
            os.makedirs(org_folder, exist_ok=True)  # Ensure the org folder exists
            with open(domains_file_path, 'a') as f:
                for domain in domains:
                    f.write(domain + '\n')
            emit('recon_update', {'data': f'Domains added to {org_name}'})
    else:
        # Write org_name to orgs.txt
        with open(orgs_file_path, 'a') as f:
            f.write(org_name + '\n')
        
        # Write domains to domains.txt inside org folder
        org_folder = os.path.join(recon_folder, org_name)
        os.makedirs(org_folder, exist_ok=True)  # Ensure the org folder exists
        domains_file_path = os.path.join(org_folder, 'domains.txt')
        with open(domains_file_path, 'a') as f:
            for domain in domains:
                f.write(domain + '\n')
        
        emit('recon_update', {'data': f'Domains added to {org_name}'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)
