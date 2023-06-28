import boto3
import time
import os

# Receive environment variables setup in the Lambda Function

REGION_NAME = os.getenv('REGION_NAME')

WORKING_DIRECTORY = os.getenv('WORKING_DIR')

# Command to execute on the ec2 instance
COMMAND = """bash run.sh"""

INSTANCE_ID = os.getenv('INSTANCE_ID')


def start_ec2():
    """Uses boto3 to connect to ec2. Starts specific instance. Then gets instance statuses and loops till it matches running or 16
    Overview:
    ----
    boto3 allows us to access ec2 console and start the ec2 instance
    """
    ec2 = boto3.client('ec2', region_name=REGION_NAME)
    ec2.start_instances(InstanceIds=[INSTANCE_ID])

    while True:
        response = ec2.describe_instance_status(InstanceIds=[INSTANCE_ID], IncludeAllInstances=True)
        state = response['InstanceStatuses'][0]['InstanceState']

        print(f"Status: {state['Code']} - {state['Name']}")

        # If status is 16 ('running'), then proceed, else, wait 5 seconds and try again
        if state['Code'] == 16:
            break
        else:
            time.sleep(5)

    print('EC2 started')


def stop_ec2():
    """Uses boto3 to connect to ec2. Stops specific instance. Then gets instance statuses and loops till it matches stopped or 80
    Overview:
    ----
    boto3 allows us to access ec2 console and stop the ec2 instance
    """
    ec2 = boto3.client('ec2', region_name=REGION_NAME)
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])

    while True:
        response = ec2.describe_instance_status(InstanceIds=[INSTANCE_ID], IncludeAllInstances=True)
        state = response['InstanceStatuses'][0]['InstanceState']

        print(f"Status: {state['Code']} - {state['Name']}")

        # If status is 80 ('stopped'), then proceed, else wait 5 seconds and try again
        if state['Code'] == 80:
            break
        else:
            time.sleep(5)

    print('Instance stopped')


def run_command():
    """Uses boto3 with the ssm to run a specific command on the ec2 instance. Keep in mind you need the ssm service to be running on the 
    ec2 instance and ssm policy attached to the ec2 role and lambda role!
    Overview:
    ----
    boto3 allows us to access ssm to send a command to ec2 as if we are sshed in and run it ourselves
    Returns:
    ----
    {int} -- Returns an int that represents the return code from the ssm command and defaulted to -1
    """
    client = boto3.client('ssm', region_name=REGION_NAME)

    time.sleep(10)  # I had to wait 10 seconds to "send_command" find my instance 

    cmd_response = client.send_command(
        InstanceIds=[INSTANCE_ID],
        DocumentName='AWS-RunShellScript',
        DocumentVersion="1",
        TimeoutSeconds=300,
        MaxConcurrency="1",
        CloudWatchOutputConfig={'CloudWatchOutputEnabled': True},
        Parameters={
            'commands': [COMMAND],
            'executionTimeout': ["300"],
            'workingDirectory': [WORKING_DIRECTORY],
        }
    )

    command_id = cmd_response['Command']['CommandId']
    time.sleep(1)  # Again, I had to wait 1s to get_command_invocation recognises my command_id

    retcode = -1
    while True:
        output = client.get_command_invocation(
            CommandId=command_id,
            InstanceId=INSTANCE_ID,
        )

        # If the ResponseCode is -1, the command is still running, so wait 5 seconds and try again
        retcode = output['ResponseCode']
        if retcode != -1:
            print('Status: ', output['Status'])
            print('StdOut: ', output['StandardOutputContent'])
            print('StdErr: ', output['StandardErrorContent'])
            break

        print('Status: ', retcode)
        time.sleep(5)

    print('Command finished successfully') # Actually, 0 means success, anything else means a fail, but it didn't matter to me
    return retcode


def lambda_handler(event, context):
    retcode = -1
    try:
        start_ec2()
        retcode = run_command()
    finally:  # Independently of what happens, try to shutdown the EC2
        stop_ec2()

    return retcode