# Report Generator Microservice - Architecture Documentation

This document provides a comprehensive overview of the Report Generator microservice architecture, explaining how the different components interact and how data flows through the system.

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Breakdown](#component-breakdown)
4. [Data Flow](#data-flow)
5. [API Structure](#api-structure)
6. [Authentication & Authorization](#authentication--authorization)
7. [File Processing](#file-processing)
8. [Transformation Rules Engine](#transformation-rules-engine)
9. [Scheduling System](#scheduling-system)
10. [Monitoring & Observability](#monitoring--observability)
11. [Deployment Architecture](#deployment-architecture)
12. [Performance Considerations](#performance-considerations)

## System Overview

The Report Generator is a microservice designed to process large input files, join them with reference data, apply configurable transformation rules, and generate output reports. The system is built with FastAPI and follows a modular architecture with clear separation of concerns.

Key capabilities:
- File upload and download
- Configurable transformation rules
- On-demand and scheduled report generation
- Multiple output formats (CSV, Excel, JSON)
- Authentication and authorization
- Monitoring and observability

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Applications                        │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                              FastAPI                                 │
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │    Auth     │ │    Files    │ │   Reports   │ │    Rules    │   │
│  │  Endpoints  │ │  Endpoints  │ │  Endpoints  │ │  Endpoints  │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                   │
│  │  Schedules  │ │   Logging   │ │   Metrics   │                   │
│  │  Endpoints  │ │ Middleware  │ │ Middleware  │                   │
│  └─────────────┘ └─────────────┘ └─────────────┘                   │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            Service Layer                             │
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │    User     │ │    File     │ │   Report    │ │    Rule     │   │
│  │   Service   │ │   Service   │ │   Service   │ │   Service   │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
│                                                                     │
│  ┌─────────────┐                                                    │
│  │  Schedule   │                                                    │
│  │   Service   │                                                    │
│  └─────────────┘                                                    │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Storage Layer                              │
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│  │   Uploads   │ │   Reports   │ │    Rules    │ │  Schedules  │   │
│  │  Directory  │ │  Directory  │ │    YAML     │ │    YAML     │   │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### API Layer (FastAPI)

The API layer is built with FastAPI and provides RESTful endpoints for interacting with the system. It's organized into the following modules:

1. **Authentication Endpoints** (`app/api/endpoints/auth.py`):
   - Handles user authentication and token generation

2. **File Endpoints** (`app/api/endpoints/files.py`):
   - Manages file uploads and downloads
   - Lists available files

3. **Report Endpoints** (`app/api/endpoints/reports.py`):
   - Triggers report generation
   - Retrieves report metadata
   - Downloads generated reports

4. **Rule Endpoints** (`app/api/endpoints/rules.py`):
   - Retrieves and updates transformation rules
   - Validates rule expressions

5. **Schedule Endpoints** (`app/api/endpoints/schedules.py`):
   - Creates and manages report generation schedules

### Service Layer

The service layer contains the business logic of the application:

1. **User Service** (`app/services/user_service.py`):
   - Manages user authentication and retrieval

2. **File Service** (`app/services/file_service.py`):
   - Handles file storage and retrieval
   - Validates file formats

3. **Report Service** (`app/services/report_service.py`):
   - Core report generation logic
   - Processes input files and applies transformation rules

4. **Rule Service** (`app/services/rule_service.py`):
   - Manages transformation rules
   - Parses and evaluates rule expressions

5. **Schedule Service** (`app/services/schedule_service.py`):
   - Manages report generation schedules
   - Handles cron expressions and scheduling logic

### Middleware

1. **Logging Middleware** (`app/middleware/logging_middleware.py`):
   - Provides structured logging for all requests
   - Tracks request IDs and processing times

2. **Metrics Middleware** (`app/middleware/metrics_middleware.py`):
   - Collects metrics for monitoring
   - Tracks request counts and latencies

### Models

The models define the data structures used throughout the application:

1. **User Models** (`app/models/user.py`):
   - User authentication and authorization models

2. **Report Models** (`app/models/report.py`):
   - File formats
   - Report metadata
   - Transformation rules
   - Schedules

## Data Flow

### Report Generation Flow

1. **Input File Upload**:
   - Client uploads input.csv via `/api/v1/files/upload/input`
   - File is stored in the uploads directory

2. **Reference File Upload**:
   - Client uploads reference.csv via `/api/v1/files/upload/reference`
   - File is stored in the uploads directory

3. **Report Generation Request**:
   - Client sends a request to `/api/v1/reports/generate`
   - Request includes input file, reference file, output format, and rule set ID

4. **Processing**:
   - Report service loads the input and reference files
   - Retrieves the transformation rules from the rule service
   - Processes the input file in chunks to handle large files
   - Joins with reference data
   - Applies transformation rules to each row
   - Writes the output to a file in the requested format

5. **Report Retrieval**:
   - Client retrieves report metadata via `/api/v1/reports/{report_id}`
   - Client downloads the report via `/api/v1/reports/{report_id}/download`

### Scheduled Report Generation

1. **Schedule Creation**:
   - Client creates a schedule via `/api/v1/schedules`
   - Schedule includes a name, type (cron, interval, one-time), expression, and report request

2. **Schedule Execution**:
   - When the schedule is due, the system automatically triggers report generation
   - The report is generated using the same flow as on-demand generation

## API Structure

The API follows RESTful principles and is organized into logical groups:

1. **Authentication** (`/api/v1/auth`):
   - `POST /login`: Authenticate and get JWT token

2. **Files** (`/api/v1/files`):
   - `POST /upload/{file_type}`: Upload a file
   - `GET /download/{filename}`: Download a file
   - `GET /list/{file_type}`: List files by type
   - `GET /list`: List all files

3. **Reports** (`/api/v1/reports`):
   - `POST /generate`: Generate a report
   - `GET /{report_id}`: Get report metadata
   - `GET /{report_id}/download`: Download a report

4. **Rules** (`/api/v1/rules`):
   - `GET /`: Get transformation rules
   - `POST /`: Update transformation rules
   - `POST /validate`: Validate a rule

5. **Schedules** (`/api/v1/schedules`):
   - `GET /`: List all schedules
   - `GET /{schedule_id}`: Get a schedule
   - `POST /`: Create a new schedule
   - `PUT /{schedule_id}`: Update a schedule
   - `DELETE /{schedule_id}`: Delete a schedule

## Authentication & Authorization

The system uses JWT (JSON Web Tokens) for authentication:

1. **Token Generation**:
   - User provides credentials to `/api/v1/auth/login`
   - System validates credentials and generates a JWT token
   - Token includes user ID and expiration time

2. **Token Validation**:
   - All protected endpoints require a valid JWT token
   - Token is passed in the Authorization header as `Bearer {token}`
   - System validates the token and extracts user information

3. **Authorization**:
   - Regular users can access most endpoints
   - Some operations may require superuser privileges

## File Processing

The system is designed to handle large files efficiently:

1. **Chunked Processing**:
   - Input files are processed in chunks to minimize memory usage
   - Default chunk size is 100,000 rows

2. **File Formats**:
   - CSV: Primary format for input and output
   - Excel: Supported for both input and output
   - JSON: Supported for both input and output

3. **File Storage**:
   - Input and reference files are stored in the `uploads` directory
   - Generated reports are stored in the `reports` directory

## Transformation Rules Engine

The transformation rules engine is a key component of the system:

1. **Rule Definition**:
   - Rules are defined in YAML format
   - Each rule has an output field, expression, and optional description

2. **Rule Evaluation**:
   - Expressions are parsed and evaluated for each row of data
   - Supported operations: arithmetic operations, string concatenation, functions (max, min)

3. **Default Rules**:
   ```yaml
   - output_field: outfield1
     expression: field1 + field2
     description: Concatenate field1 and field2
   
   - output_field: outfield2
     expression: refdata1
     description: Use refdata1 directly
   
   - output_field: outfield3
     expression: refdata2 + refdata3
     description: Concatenate refdata2 and refdata3
   
   - output_field: outfield4
     expression: field3 * max(field5, refdata4)
     description: Multiply field3 by the maximum of field5 and refdata4
   
   - output_field: outfield5
     expression: max(field5, refdata4)
     description: Maximum of field5 and refdata4
   ```

## Scheduling System

The scheduling system allows for automated report generation:

1. **Schedule Types**:
   - **Cron**: Uses cron expressions for recurring schedules
   - **Interval**: Runs at fixed intervals (in seconds)
   - **One-time**: Runs once at a specific time

2. **Schedule Storage**:
   - Schedules are stored in YAML format in the `config/schedules.yaml` file

3. **Schedule Execution**:
   - In a production environment, a background worker would check for due schedules
   - For simplicity, this implementation requires manual triggering

## Monitoring & Observability

The system includes monitoring and observability features:

1. **Structured Logging**:
   - All requests are logged with a unique request ID
   - Logs include method, URL, status code, and processing time
   - Uses the `structlog` library for structured logging

2. **Metrics**:
   - Request counts and latencies are tracked
   - Report generation counts and latencies are tracked
   - Uses the `prometheus_client` library for metrics collection

## Deployment Architecture

The system is designed to be deployed as a containerized application:

1. **Docker**:
   - Dockerfile for building the application container
   - Uses Python 3.11 as the base image

2. **Docker Compose**:
   - docker-compose.yml for orchestrating the application
   - Mounts volumes for persistent storage of uploads, reports, and configuration

3. **Production Considerations**:
   - In a production environment, additional components would be needed:
     - Database for storing metadata
     - Message queue for background processing
     - Separate workers for processing reports
     - Load balancer for scaling

## Performance Considerations

The system is designed to handle large files efficiently:

1. **Chunked Processing**:
   - Input files are processed in chunks to minimize memory usage
   - This allows handling of files larger than available memory

2. **Optimized Joins**:
   - Uses pandas for efficient data processing and joins

3. **Parallel Processing**:
   - In a production environment, parallel processing could be implemented for faster processing

4. **Caching**:
   - Reference data could be cached for improved performance when processing multiple reports

5. **Performance Requirements**:
   - The system is designed to generate a report from a 1 GB file in under 30 seconds
   - Can handle up to 250 fields in input/output files
