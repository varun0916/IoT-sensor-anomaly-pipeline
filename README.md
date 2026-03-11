# IoT-sensor-anomaly-pipeline

IoT Sensor Anomaly Detection Pipeline
[
End-to-end real-time IoT data pipeline using AWS (S3, Lambda, Kinesis, Firehose) + Databricks Medallion Architecture.
​

🎯 Project Overview
IoT anomaly detection system processing 5 datasets (sensor_stream, device_operations, environment_network, time_anomaly_events, device_health_diagnostics) into star schema (4 dimension + 1 fact table) for monitoring, diagnostics, and analytics. Supports sensor monitoring, predictive maintenance, anomaly detection.
​

Data Sources (S3 iot-anomaly-pipeline-varun/raw/):

sensor_stream_dataset

device_operations_dataset

environment_network_dataset

time_anomaly_events_dataset

device_health_diagnostics_dataset
​

🏗️ Architecture

S3 Raw CSV (5 folders)
  ↓ S3 Event
Lambda Producer ──> Kinesis Stream (iot-kinesis-stream)
  ↓ Consumer
Firehose ──> S3 Bronze (iot-anomaly-bronze-varun/bronze/)
  ↓ Auto Loader
Databricks:
  Bronze (raw JSON) → Silver (cleaned) → Gold (star schema + KPIs)
  
Medallion Layers:
​
Layer	                  Tables	                                                    Purpose
Bronze	      bronze_sensorstream, bronze_deviceoperations, etc.          	Raw ingestion (duplicates/nulls OK)
Silver	      silver_sensorstream, silver_deviceoperations, etc.	          Cleaned, standardized, validated
Gold	        dimsensormaster, dimdevicemaster, dimlocationenvironment, 
              dimtimeanomaly, factiotevents	                                Star schema + metrics (avg health, failure ratio, anomaly trends)


🚀 Quick Start

AWS Setup:
# Buckets
aws s3 mb s3://iot-anomaly-pipeline-varun  # Raw
aws s3 mb s3://iot-anomaly-bronze-varun    # Bronze

# Kinesis stream (ap-south-1)
aws kinesis create-stream --stream-name iot-kinesis-stream --shard-count 2

# Firehose
aws firehose create-delivery-stream --delivery-stream-name iot-kinesis-to-bronze \
  --kinesis-stream-source-configuration StreamARN=arn:aws:kinesis:.../iot-kinesis-stream \
  --s3-destination-configuration BucketARN=arn:aws:s3:::iot-anomaly-bronze-varun,BufferingHints={SizeInMBs=1,IntervalInSeconds=60}
Deploy Lambda Producer (s3-to-kinesis-producer):

Code: lambda_producer.py

Trigger: S3 iot-anomaly-pipeline-varun, prefix raw/, events ObjectCreated

IAM: S3 GetObject, Kinesis PutRecords

Upload Sample CSVs:

aws s3 cp datasets/*.csv s3://iot-anomaly-pipeline-varun/raw/[dataset_folder]/
Databricks (ap-south-1 workspace):

python
# notebooks/bronze_silver_gold.py
%run ./notebooks/medallion_pipeline
dbutils.notebook.run("./bronze", 0)
dbutils.notebook.run("./silver", 0)
dbutils.notebook.run("./gold_star_schema", 0)

📊 Key Features

Real-time: S3 → Kinesis → Firehose → Bronze (<60s latency)

Scalable: Auto Loader handles new files, Delta auto-optimize

Star Schema: Ready for BI (PowerBI/Tableau)
​
Metrics: Health scores, failure ratios, anomaly trends, environment impact
​

Gold KPIs:

Total Sensor Readings by Category | Device Utilization Rate
Anomaly Events by Severity | Temperature Impact on Readings
Device Failure Ratio | Signal Quality by Region

🛠️ Tech Stack
Layer	Tech
Ingestion	AWS S3, Lambda, Kinesis Data Stream, Firehose
Storage	S3 Bronze, Delta Lake
Processing	Databricks (PySpark, SQL, Auto Loader)
Analytics	Star Schema (dimsensor, dimdevice, dimlocation, dimtimeanomaly, factiotevents)
Monitoring	CloudWatch, Databricks Jobs

📁 Repository Structure
text
├── README.md                 # This file
├── IOT-LOW-LEVEL-DESIGN.pdf  # Architecture spec [file:150]
├── aws/
│   ├── lambda_producer.py
│   └── terraform.tf          # Infra as code
├── datasets/                 # Sample CSVs
├── databricks/
│   ├── notebooks/
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold_star_schema.py
│   └── cluster-config.json
└── dashboards/               # PowerBI/Tableau exports

🔍 Usage
Stream Data: Upload CSV → Real-time bronze tables populate.

Query Gold:

sql
SELECT deviceid, AVG(healthscore) FROM gold.factiotevents GROUP BY deviceid;
SELECT anomalycategory, COUNT(*) FROM gold.dimtimeanomaly GROUP BY anomalycategory;
Dashboards: Connect to gold.factiotevents for KPIs.

⚠️ Prerequisites
AWS account (ap-south-1)

Databricks workspace + S3 IAM access

Git repo with Delta Lake Unity Catalog

🤝 Contributing
Fork → Add notebooks → PR. Issues: Lambda errors, scaling, cost optimization.
