from flask import Flask, request, jsonify
import paramiko
import json
import socket

app = Flask(__name__)

# read settings.json
with open('settings.json', 'r') as file:
    settings = json.load(file)


@app.route('/')
def initial():
    if settings['username'] and settings['password'] and settings['api']:
        #serve static files
        return app.send_static_file('index.html')
    else:
        return app.send_static_file('setup.html')

@app.route('/test')
def test():
    return app.send_static_file('index.html')

@app.route('/getUserName')
def get_user_name():
    if settings['username'] and settings['password'] and settings['api']:
        return jsonify({"username": settings['username']})
    else:
        return jsonify({"username": "Nikita"})

@app.route('/get-api')
def get_api():
    if settings['username'] and settings['password'] and settings['api']:
        return jsonify({"api": settings['api']})
    else:
        return jsonify({"api": "Nikita"})

@app.route('/register', methods=['POST'])
def register():
    # Get the data from the request's JSON body
    data = request.get_json()

    # Extract the provided username, password, and api key
    username = data.get('username')
    password = data.get('password')
    api = data.get('api')

    # Ensure all required details are provided
    if not username or not password or not api:
        return jsonify({"message": "Incomplete registration details!"}), 400

    # Save to settings.json
    with open('settings.json', 'w') as file:
        json.dump({
            "username": username,
            "password": password,
            "api": api
        }, file)

    return jsonify({"message": "Successfully registered!"})

@app.route('/backend-endpoint')
def handle_icon_click():
    icon_name = request.args.get('icon')
    # Check if the icon_name matches any of the expected values
    if icon_name in ["co-writer", "hyperSVG", "ssh", "settings"]:
        return app.send_static_file(f"{icon_name}.html")
    else:
        return jsonify({"error": "Unknown icon!"}), 400


@app.route('/execute', methods=['POST'])
def execute():
    command = request.form.get('command')
    ssh_output = execute_ssh_command(command)
    return jsonify({"output": ssh_output})

def execute_ssh_command(command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Getting the public IP of the server
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    
    ssh.connect(ip_address, username=settings['username'], password=settings['password'])
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    ssh.close()
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
