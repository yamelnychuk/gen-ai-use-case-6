import boto3
import json
import os
import tempfile

ec2 = boto3.resource('ec2')
s3 = boto3.client('s3')

bucket_name = os.getenv('BUCKET_NAME')

def save_to_s3(data, filename):
    try:
        if not bucket_name:
            raise ValueError("No bucket name provided. Please set the BUCKET_NAME environment variable.")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(json.dumps(data).encode())

        with open(tmp.name, 'rb') as data:
            s3.upload_fileobj(data, bucket_name, filename)
        os.unlink(tmp.name)
    except Exception as e:
        print(f"Error occurred while uploading data to S3: {e}")

def unattached_volumes():
    unattached_volumes = []
    try:
        for volume in ec2.volumes.all():
            if volume.state == 'available':
                unattached_volumes.append(volume)
    except Exception as e:
        print(f"Error occurred while getting unattached volumes: {e}")
        return

    total_size = sum([vol.size for vol in unattached_volumes])
    data = {'count': len(unattached_volumes), 'total_size': total_size}
    save_to_s3(data, 'unattached_volumes.json')
    return data

def non_encrypted_volumes():
    non_encrypted_volumes = []
    try:
        for volume in ec2.volumes.all():
            if not volume.encrypted:
                non_encrypted_volumes.append(volume)
    except Exception as e:
        print(f"Error occurred while getting non-encrypted volumes: {e}")
        return

    total_size = sum([vol.size for vol in non_encrypted_volumes])
    data = {'count': len(non_encrypted_volumes), 'total_size': total_size}
    save_to_s3(data, 'non_encrypted_volumes.json')
    return data

def non_encrypted_snapshots():
    non_encrypted_snapshots = []
    try:
        for snapshot in ec2.snapshots.filter(OwnerIds=['self']):
            if not snapshot.encrypted:
                non_encrypted_snapshots.append(snapshot)
    except Exception as e:
        print(f"Error occurred while getting non-encrypted snapshots: {e}")
        return

    total_size = sum([snap.volume_size for snap in non_encrypted_snapshots])
    data = {'count': len(non_encrypted_snapshots), 'total_size': total_size}
    save_to_s3(data, 'non_encrypted_snapshots.json')
    return data

def lambda_handler(event, context):
    print(f"Unattached Volumes: {unattached_volumes()}")
    print(f"Non-Encrypted Volumes: {non_encrypted_volumes()}")
    print(f"Non-Encrypted Snapshots: {non_encrypted_snapshots()}")