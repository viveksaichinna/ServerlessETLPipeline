🛒 AWS Serverless Data Pipeline – Online Orders Demo
===================================================

This project shows how to build a simple, ultra‑low‑cost serverless pipeline on AWS that processes online‑order data.

AWS services used
-----------------

• **S3** – stores raw and processed CSV files  
• **Lambda** – filters out stale `pending` / `cancelled` orders  
• **Glue** – crawls and catalogs cleaned data  
• **Athena** – runs ad‑hoc SQL queries  
• **CloudWatch** – captures Lambda logs and metrics  

Goal and data flow
------------------

1. Upload a CSV of orders to the `raw/` folder in S3.  
2. An S3 trigger invokes Lambda. The function drops every `pending` or `cancelled` order older than 30 days.  
3. Lambda writes a cleaned file to `processed/` in the same bucket.  
4. You run an AWS Glue crawler once (manually) to create an external table.  
5. Use Athena to query the cleaned dataset.  

S3 layout
---------

```
s3://<your‑bucket>/
├── raw/
│   └── orders.csv            ← upload here
└── processed/
    └── filtered_orders.csv   ← Lambda output
```

Step‑by‑step setup
------------------

### 1. Create the bucket and folders

– Create an S3 bucket, for example `online-orders-pipeline`.  
– Inside it, add two empty folders named `raw/` and `processed/`.  

### 2. Generate sample data locally

Run the following Python script; it creates `orders.csv` with 100 random rows.
```python
    import csv, random
    from datetime import datetime, timedelta

    STATUSES  = ['confirmed', 'shipped', 'pending', 'cancelled']
    CUSTOMERS = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']

    def random_date():
        return (datetime.now() - timedelta(days=random.randint(0, 90))).strftime('%Y-%m-%d')

    with open('orders.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['OrderID', 'Customer', 'Amount', 'Status', 'OrderDate'])
        for i in range(100):
            w.writerow([
                f'O{i+1:04}', random.choice(CUSTOMERS),
                round(random.uniform(10, 500), 2),
                random.choice(STATUSES),
                random_date()
            ])
    print('orders.csv generated')
```
Upload `orders.csv` to the `raw/` folder.

### 3. Create the Lambda function

**Handler (Python 3.9 or newer)**
```python

import boto3
import csv
import io
from datetime import datetime, timedelta

s3 = boto3.client('s3')

def lambda_handler(event, context):
    print("Lambda triggered by S3 event.")
    
    # Get the S3 bucket and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    raw_key = event['Records'][0]['s3']['object']['key']
    file_name = raw_key.split('/')[-1]

    print(f"Incoming file: {raw_key}")
    
    try:
        # Download raw CSV from S3
        response = s3.get_object(Bucket=bucket_name, Key=raw_key)
        raw_csv = response['Body'].read().decode('utf-8').splitlines()
        print(f"Successfully read file from S3: {file_name}")
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        raise e

    reader = csv.DictReader(raw_csv)
    filtered_rows = []
    original_count = 0
    filtered_out_count = 0
    cutoff_date = datetime.now() - timedelta(days=30)

    print("Processing records...")
    for row in reader:
        original_count += 1
        order_status = row['Status'].strip().lower()
        order_date = datetime.strptime(row['OrderDate'], "%Y-%m-%d")

        # Check if the order should be kept
        if order_status not in ['pending', 'cancelled'] or order_date > cutoff_date:
            filtered_rows.append(row)
        else:
            filtered_out_count += 1

    print(f"Total records processed: {original_count}")
    print(f"Records filtered out: {filtered_out_count}")
    print(f"Records kept: {len(filtered_rows)}")

    # Write the filtered rows to memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=reader.fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)

    # Save to processed/ folder
    processed_key = f"processed/filtered_{file_name}"
    
    try:
        s3.put_object(Bucket=bucket_name, Key=processed_key, Body=output.getvalue())
        print(f"Filtered file successfully written to S3: {processed_key}")
    except Exception as e:
        print(f"Error writing filtered file to S3: {e}")
        raise e

    return {
        'statusCode': 200,
        'body': f"Filtered {len(filtered_rows)} rows and saved to {processed_key}"
    }

```
**Configuration notes**

• Trigger: S3 event for the `raw/` prefix  
• IAM: allow `s3:GetObject` and `s3:PutObject` on the bucket, plus CloudWatch Logs write  

### 4. Set up a Glue crawler

1. AWS Glue ➜ Crawlers ➜ Create.  
2. Source: `s3://<bucket>/processed/`  
3. Target database: create (or reuse) one, e.g. `orders_db`.  
4. Table name: `orders_processed`.  
5. Run the crawler after Lambda finishes.  

### 5. Query the data with Athena

Make sure Athena’s query‑result location is set, then run:

Recent 10 orders:
```sql
    SELECT *
    FROM orders_processed
    ORDER BY orderdate DESC
    LIMIT 10;
```
Total revenue of fulfilled orders:
```sql
    SELECT SUM(amount) AS total_revenue
    FROM orders_processed
    WHERE status IN ('confirmed', 'shipped');
```
CloudWatch logs
---------------

CloudWatch Logs ➜ Log groups ➜ `/aws/lambda/<function‑name>`  
Each run shows:

• File processed  
• Rows kept / filtered  
• Output file path  
• Any errors  

Pipeline recap
--------------

1. Generate sample `orders.csv`.  
2. Store raw and processed files in S3.  
3. Lambda filters out stale pending/cancelled orders.  
4. Glue catalogs the cleaned data.  
5. Athena lets you query it with SQL.  
6. CloudWatch provides logs and metrics.