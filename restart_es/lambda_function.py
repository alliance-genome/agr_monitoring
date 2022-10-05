import boto3
import paramiko
from io import StringIO
import json
import urllib3
import logging

# Obtain the parameter from the AWS Systems Manager (SSM) Parameter Store.
def get_parameter(parameter):
    
    ssm_client = boto3.client('ssm')
    
    response = ssm_client.get_parameters(Names=[parameter],WithDecryption=True)
    
    for parameter in response['Parameters']:
        return parameter['Value']

# Uncomment the following lines for debugging purposes.
# logging.basicConfig()
# logging.getLogger("paramiko").setLevel(logging.DEBUG)

# Obtain the RSA Key from the AWS Systems Manager (SSM) Parameter Store.
private_key = paramiko.RSAKey.from_private_key(file_obj=StringIO(get_parameter('/ec2/rsakey')))

# Obtain the IP address for the production server.
production_ip = get_parameter('/ec2/production_ip')

# Obtain the username for the production server.
production_username = get_parameter('/ec2/production_username')

# Obtain the Slack webhook URL.
url = get_parameter('/slack/webhook')

# Launch an instance of the SSH client.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Obtain http for communicating with Slack.
http = urllib3.PoolManager()

# Connect to the EC2 instance via SSH.
def connect_ssh(ip, username):
    connected = False

    try:
        ssh.connect(hostname=ip, port=22, username=username, pkey=private_key)
        connected = True
        return connected
    except:
        ssh.close()

# Run shell command(s) on the EC2 instance.
def run_command(cmd):
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdin.flush()
    
    data_stdout = stdout.read().splitlines()
    data_error = stderr.read().splitlines()

    for line in data_stdout:
        print(line)

    for line in data_error:
        print(line)

def lambda_handler(event=None, context=None):
    # Edit the following variables before using this script.
    command_to_run = "docker start agr.production.elasticsearch.server || docker run --name agr.production.elasticsearch.server -d agr.production.elasticsearch.server"
     
    successful_connection = connect_ssh(production_ip, production_username)
    
    if (successful_connection) :
        run_command(command_to_run)
        ssh.close()  

    msg = "Attempting to relaunch agr.production.elasticsearch.server Docker container via AWS Lambda script."

    mesg = {
        "channel": "#system-alerts",
        "username": "AWS Lambda",
        "text": msg,
        "icon_emoji": ":aws:"
    }
    
    resp = http.request('POST',url, body=json.dumps(mesg).encode('utf-8'))
    
    # return {
    #     'statusCode': 200,
    #     'body': json.dumps(event)
    # }

    return True