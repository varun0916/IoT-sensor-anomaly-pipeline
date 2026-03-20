import boto3
import csv
import json
import io
import time

s3 = boto3.client('s3')
kinesis = boto3.client('kinesis')

def lambda_handler(event, context):
    # Get bucket and key from the S3 event
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']
    except KeyError:
        return {"error": "Test event must be an S3-Put event template"}

    # Route to correct stream
    # updated logic to match your specific filenames
    if "environment" in key:
        stream = "environment-stream"
    elif "health" in key:
        stream = "health-stream"
    elif "operations" in key:
        stream = "operations-stream"
    elif "sensor" in key:
        stream = "sensor-stream"
    elif "time" in key:
        stream = "time-stream"
    else: 
        raise Exception(f"Filename does not match any stream: {key}")

    # Read data from S3
    obj = s3.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')
    reader = csv.DictReader(io.StringIO(data))

    batch = []
    for row in reader:
        cleaned = {}
        for k, v in row.items():
            if v == "" or v is None:
                cleaned[k] = None
            else:
                cleaned[k] = v.strip()

        batch.append({
            "Data": json.dumps(cleaned),
            "PartitionKey": "1"
        })

        if len(batch) == 500:
            send_with_retry(batch, stream) # Fixed variable name to lowercase
            batch = []
            time.sleep(0.2)

    if batch:
        send_with_retry(batch, stream) # Fixed variable name to lowercase
        time.sleep(0.2)

    return {"statusCode": 200, "file_processed": key}

def send_with_retry(records, stream_name):
    while True:
        response = kinesis.put_records(
            Records=records,
            StreamName=stream_name
        )

        failed = response['FailedRecordCount']
        if failed == 0:
            break

        print(f"Retrying {failed} failed records...")
        retry_records = []
        for i, record in enumerate(response['Records']):
            if 'ErrorCode' in record:
                retry_records.append(records[i])

        records = retry_records
        time.sleep(0.5)