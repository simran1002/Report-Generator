# Report Generator Microservice - Usage Guide

This guide provides step-by-step instructions for using the Report Generator microservice.

## Getting Started

### Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python run.py
   ```
   
   Or using uvicorn directly:
   ```
   uvicorn app.main:app --reload
   ```

3. Access the API documentation at:
   ```
   http://localhost:8000/docs
   ```

## Authentication

Before using the API, you need to authenticate:

1. Go to `/api/v1/auth/login` endpoint in the Swagger UI
2. Use the following credentials:
   - Username: `user`
   - Password: `user`
   
   Or for admin access:
   - Username: `admin`
   - Password: `admin`

3. The API will return a JWT token. Click the "Authorize" button in Swagger UI and enter the token as `Bearer {token}`.

## Basic Workflow

### 1. Upload Files

Upload input and reference files using the `/api/v1/files/upload/{file_type}` endpoint:

- For input file: `file_type = input`
- For reference file: `file_type = reference`

Sample files are already included in the `uploads` directory:
- `input_sample.csv`
- `reference_sample.csv`

### 2. Generate a Report

Use the `/api/v1/reports/generate` endpoint with the following JSON body:

```json
{
  "input_file": "input_sample.csv",
  "reference_file": "reference_sample.csv",
  "output_format": "csv",
  "rule_set_id": null
}
```

If `rule_set_id` is null, the default rule set will be used.

### 3. Download the Report

1. Get the report ID from the response of the generate endpoint
2. Use the `/api/v1/reports/{report_id}/download` endpoint to download the report

## Working with Transformation Rules

### View Current Rules

Use the `/api/v1/rules` endpoint to view the current transformation rules.

### Update Rules

Use the `/api/v1/rules` POST endpoint with a JSON body like:

```json
{
  "rules": [
    {
      "output_field": "outfield1",
      "expression": "field1 + ' ' + field2",
      "description": "Full name"
    },
    {
      "output_field": "outfield2",
      "expression": "refdata1",
      "description": "Customer ID"
    }
  ],
  "version": "custom"
}
```

## Setting Up Schedules

### Create a Schedule

Use the `/api/v1/schedules` endpoint with parameters:

- `name`: Name of the schedule
- `schedule_type`: Type of schedule (cron, interval, or one_time)
- `expression`: Schedule expression (cron expression, interval in seconds, or ISO datetime)
- `report_request`: Report generation request

Example for a daily schedule at midnight:
- `name`: Daily Report
- `schedule_type`: cron
- `expression`: 0 0 * * *
- `report_request`: Same as in the generate report example

## Docker Deployment

To run the application using Docker:

```
docker-compose up -d
```

This will start the application and make it available at http://localhost:8000.
