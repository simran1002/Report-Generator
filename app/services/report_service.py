import os
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
from fastapi import HTTPException

from app.core.config import settings
from app.models.report import FileFormat, ReportGenerationRequest, ReportMetadata, ReportStatus
from app.services.rule_service import get_rule_set, parse_expression


def generate_report(
    request: ReportGenerationRequest, 
    username: str
) -> ReportMetadata:
    """
    Generate a report by processing input and reference files with transformation rules.
    
    This function handles the core report generation logic:
    1. Load input and reference files
    2. Apply transformation rules
    3. Save the output file
    4. Return metadata about the report
    """
    # Validate input files
    input_file_path = _get_latest_file("input") if not request.input_file else os.path.join(settings.UPLOAD_DIR, request.input_file)
    reference_file_path = _get_latest_file("reference") if not request.reference_file else os.path.join(settings.UPLOAD_DIR, request.reference_file)
    
    if not os.path.exists(input_file_path):
        raise HTTPException(status_code=404, detail=f"Input file not found: {request.input_file}")
    if not os.path.exists(reference_file_path):
        raise HTTPException(status_code=404, detail=f"Reference file not found: {request.reference_file}")
    
    # Get rule set
    rule_set = get_rule_set(request.rule_set_id)
    
    # Create report metadata
    report_id = str(uuid.uuid4())
    output_filename = f"report_{report_id}.{request.output_format.value}"
    output_file_path = os.path.join(settings.REPORTS_DIR, output_filename)
    
    report_metadata = ReportMetadata(
        id=report_id,
        input_file=os.path.basename(input_file_path),
        reference_file=os.path.basename(reference_file_path),
        output_file=output_filename,
        output_format=request.output_format,
        rule_set_id=rule_set.version,
        status=ReportStatus.PROCESSING,
        start_time=datetime.now(),
        created_by=username,
        rows_processed=0
    )
    
    try:
        # Process the files
        start_time = time.time()
        rows_processed = _process_files(
            input_file_path=input_file_path,
            reference_file_path=reference_file_path,
            output_file_path=output_file_path,
            output_format=request.output_format,
            rule_set=rule_set.rules
        )
        end_time = time.time()
        
        # Update report metadata
        report_metadata.status = ReportStatus.COMPLETED
        report_metadata.end_time = datetime.now()
        report_metadata.processing_time_seconds = end_time - start_time
        report_metadata.rows_processed = rows_processed
        
        return report_metadata
    
    except Exception as e:
        # Update report metadata with error
        report_metadata.status = ReportStatus.FAILED
        report_metadata.end_time = datetime.now()
        report_metadata.error_message = str(e)
        
        # Re-raise the exception
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


def _get_latest_file(file_type: str) -> str:
    """Get the latest uploaded file of a specific type."""
    files = [f for f in os.listdir(settings.UPLOAD_DIR) if f.startswith(file_type)]
    if not files:
        raise HTTPException(status_code=404, detail=f"No {file_type} files found")
    
    # Sort by modification time (newest first)
    files.sort(key=lambda f: os.path.getmtime(os.path.join(settings.UPLOAD_DIR, f)), reverse=True)
    return os.path.join(settings.UPLOAD_DIR, files[0])


def _process_files(
    input_file_path: str,
    reference_file_path: str,
    output_file_path: str,
    output_format: FileFormat,
    rule_set: List
) -> int:
    """
    Process the input and reference files to generate the output file.
    
    This is the core processing function that:
    1. Reads input data in chunks to handle large files
    2. Merges with reference data
    3. Applies transformation rules
    4. Writes output in the requested format
    
    Returns the number of rows processed.
    """
    # Read reference data (assuming it fits in memory)
    reference_df = pd.read_csv(reference_file_path)
    
    # Create an empty output dataframe for appending results
    output_columns = [rule.output_field for rule in rule_set]
    output_df = pd.DataFrame(columns=output_columns)
    
    # Process input file in chunks
    chunk_size = settings.CHUNK_SIZE
    total_rows = 0
    
    # Read input file in chunks
    for chunk in pd.read_csv(input_file_path, chunksize=chunk_size):
        # Merge with reference data
        merged_df = pd.merge(
            chunk,
            reference_df,
            left_on=["refkey1", "refkey2"],
            right_on=["refkey1", "refkey2"],
            how="left"
        )
        
        # Create output dataframe for this chunk
        chunk_output = pd.DataFrame(columns=output_columns)
        
        # Apply transformation rules
        for rule in rule_set:
            chunk_output[rule.output_field] = merged_df.apply(
                lambda row: parse_expression(rule.expression, row),
                axis=1
            )
        
        # Append to output
        output_df = pd.concat([output_df, chunk_output])
        
        # Update row count
        total_rows += len(chunk)
    
    # Write output file based on format
    if output_format == FileFormat.CSV:
        output_df.to_csv(output_file_path, index=False)
    elif output_format == FileFormat.EXCEL:
        output_df.to_excel(output_file_path, index=False)
    elif output_format == FileFormat.JSON:
        output_df.to_json(output_file_path, orient="records")
    
    return total_rows


def get_report_metadata(report_id: str) -> Optional[ReportMetadata]:
    """Get metadata for a specific report."""
    # In a real implementation, this would retrieve from a database
    # For now, we'll just check if the file exists
    report_file = f"report_{report_id}.csv"
    report_path = os.path.join(settings.REPORTS_DIR, report_file)
    
    if not os.path.exists(report_path):
        return None
    
    # In a real implementation, we would retrieve the actual metadata
    # For now, we'll just return a placeholder
    return ReportMetadata(
        id=report_id,
        input_file="input.csv",
        reference_file="reference.csv",
        output_file=report_file,
        output_format=FileFormat.CSV,
        rule_set_id="default",
        status=ReportStatus.COMPLETED,
        start_time=datetime.fromtimestamp(os.path.getctime(report_path)),
        end_time=datetime.fromtimestamp(os.path.getmtime(report_path)),
        processing_time_seconds=10.0,
        created_by="user",
        rows_processed=1000
    )
