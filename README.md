# Report Generator Microservice

A Python-based microservice that ingests large input files and generates output reports by joining with reference data and applying configurable transformation rules.

## Features

- REST endpoints for uploading input and reference files
- On-demand report generation
- Download generated reports
- Configure transformation rules via external files (JSON/YAML)
- Scheduling capabilities using cron expressions
- Support for multiple file formats (CSV, Excel, JSON)
- Authentication and authorization
- Monitoring and observability
- Structured logging
- Containerized deployment

## Requirements

- Python 3.10+
- Docker and Docker Compose
- Git

## Setup Instructions

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/simran1002/Report-Generator.git
   cd report-generator
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Unix or MacOS
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   uvicorn app.main:app --reload
   ```

5. Access the API documentation at:
   ```
   http://localhost:8000/docs
   ```

### Docker Setup

1. Build and run the Docker containers:
   ```
   docker-compose up -d
   ```

2. Access the API documentation at:
   ```
   http://localhost:8000/docs
   ```

## API Documentation

The API documentation is available via Swagger UI at `/docs` or ReDoc at `/redoc` when the application is running.

### Main Endpoints

- `POST /api/v1/files/upload/input`: Upload input CSV file
- `POST /api/v1/files/upload/reference`: Upload reference CSV file
- `POST /api/v1/reports/generate`: Trigger report generation
- `GET /api/v1/reports/{report_id}`: Download generated report
- `GET /api/v1/rules`: Get transformation rules
- `POST /api/v1/rules`: Update transformation rules
- `POST /api/v1/schedules`: Create a new schedule
- `GET /api/v1/schedules`: List all schedules

## Configuration

Transformation rules are stored in `config/rules.yaml` and can be modified directly or through the API.

## Testing

Run the tests with:
```
pytest
```

Run with coverage:
```
pytest --cov=app
```

## Performance

The service is optimized to generate reports from 1GB files in under 30 seconds and can handle up to 250 fields in input/output files.
