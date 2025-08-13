import csv
from datetime import datetime
import io
from typing import List, Dict, Any

from fastapi import UploadFile, HTTPException
from fastapi.responses import StreamingResponse

from app.services.file_transfer.base_file_transfer import BaseFileTransfer

class CsvFileTransfer(BaseFileTransfer):
    
    def export_file(self, user_id: int) -> StreamingResponse:
    
        # Load json data from configured file storage
        expenses_data: list[dict] = self.storage.load_file(user_id, 'expenses.json')
        if not expenses_data:
            raise ValueError('No data found for export')
        
        # Prepare expenses data to include in CSV 
        fields = ['description', 'category', 'amount', 'date']
        filtered_data = []
        
        for expense in expenses_data:
            row = {}
            for field in fields:
                if field == 'date' and expense.get(field):
                    # Ensure date is in yyyy-mm-dd format for export
                    date_value = expense.get(field, '')
                    try:
                        # Check if date is in dd/mm/yyyy format and convert to yyyy-mm-dd
                        if '/' in date_value:
                            parsed_date = datetime.strptime(date_value, "%d/%m/%Y")
                            row[field] = parsed_date.strftime("%Y-%m-%d")
                        elif '-' in date_value:
                            # Validate it's already in yyyy-mm-dd format
                            datetime.strptime(date_value, "%Y-%m-%d")
                            row[field] = date_value
                        else:
                            row[field] = date_value  # Keep as-is if format is unknown
                    except ValueError:
                        row[field] = date_value  # Keep original if parsing fails
                else:
                    row[field] = expense.get(field, '')
            filtered_data.append(row)
        
        # Sort data by date (newest to oldest, change reverse=False for oldest to newest)
        def get_sort_date(row):
            date_str = row.get('date', '')
            try:
                if '/' in date_str:
                    return datetime.strptime(date_str, "%d/%m/%Y")
                elif '-' in date_str:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    return datetime.min  # Put invalid dates at the beginning
            except ValueError:
                return datetime.min  # Put invalid dates at the beginning
        
        filtered_data.sort(key=get_sort_date, reverse=True)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        writer.writerows(filtered_data)

        # Rewind the StringIO buffer
        output.seek(0)

        # Return as downloadable file
        return StreamingResponse(
            io.StringIO(output.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=expenses.csv"}
        )
            

    def import_file(self, user_id: int, file: UploadFile) -> None:
        """
        Import CSV file and save expenses data to storage.
        
        Args:
            user_id: The user ID to associate the data with
            file: The uploaded CSV file
            
        Raises:
            HTTPException: If file processing fails
            ValueError: If data validation fails
        """
        try:
            # Validate file type
            if not file.filename or not file.filename.lower().endswith('.csv'):
                raise HTTPException(status_code=400, detail="File must be a CSV file")
            
            # Read file content
            contents = file.file.read()
            
            # Decode bytes to string
            try:
                csv_content = contents.decode('utf-8')
            except UnicodeDecodeError:
                # Try with different encoding if UTF-8 fails
                try:
                    csv_content = contents.decode('latin-1')
                except UnicodeDecodeError:
                    raise HTTPException(status_code=400, detail="Unable to decode file. Please ensure it's a valid CSV file.")
            
            # Create StringIO object from content
            csv_file = io.StringIO(csv_content)
            
            # Read CSV data
            csv_reader = csv.DictReader(csv_file)
            
            # Validate that required columns exist
            required_fields = ['description', 'category', 'amount', 'date']
            if not csv_reader.fieldnames:
                raise HTTPException(status_code=400, detail="CSV file appears to be empty or invalid")
            
            # Check if all required fields are present (case-insensitive)
            fieldnames_lower = [field.lower().strip() for field in csv_reader.fieldnames]

            missing_fields = []
            
            for required_field in required_fields:
                if required_field.lower() not in fieldnames_lower:
                    missing_fields.append(required_field)
            
            if missing_fields:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required columns: {', '.join(missing_fields)}. Required columns are: {', '.join(required_fields)}"
                )
            
            # Create field mapping for case-insensitive matching
            field_mapping = {}
            for required_field in required_fields:
                for original_field in csv_reader.fieldnames:
                    if original_field.lower().strip() == required_field.lower():
                        field_mapping[required_field] = original_field
                        break
            
            # existing data length for id reference
            existing_data_length = len(self.storage.load_file(user_id, 'expenses.json'))

            # Parse CSV rows into list of dictionaries
            expenses_data: List[Dict[str, Any]] = []
            row_number = 1  # Start from 1 since header is row 0
            next_id = existing_data_length + 1  # Start ID from next available number

            for row in csv_reader:
                row_number += 1
                
                try:
                    # Create expense dictionary with normalized field names
                    expense = {}
                    
                    # Assign ID first, outside the field loop
                    expense['id'] = next_id
                    next_id += 1  # Increment for next record
                    

                    for required_field in required_fields:
                        original_field = field_mapping[required_field]
                        value = row.get(original_field, '').strip()
                        
                        # Validate and process each field
                        if required_field == 'amount':
                            if not value:
                                raise ValueError(f"Amount is required in row {row_number}")
                            try:
                                # Remove any currency symbols and convert to float
                                cleaned_amount = value.replace('₱', '').replace(',', '').strip()
                                expense[required_field] = float(cleaned_amount)
                            except ValueError:
                                raise ValueError(f"Invalid amount format '{value}' in row {row_number}")
                        
                        elif required_field == 'date':
                            if not value:
                                raise ValueError(f"Date is required in row {row_number}")
                            try:
                                # Validate date format but keep original yyyy-mm-dd format
                                datetime.strptime(value, "%Y-%m-%d")
                                expense[required_field] = value  # Keep original format
                            except ValueError:
                                # If it's not in yyyy-mm-dd format, try other common formats and convert
                                try:
                                    # Try dd/mm/yyyy format
                                    parsed_date = datetime.strptime(value, "%d/%m/%Y")
                                    expense[required_field] = parsed_date.strftime("%Y-%m-%d")
                                except ValueError:
                                    try:
                                        # Try mm/dd/yyyy format
                                        parsed_date = datetime.strptime(value, "%m/%d/%Y")
                                        expense[required_field] = parsed_date.strftime("%Y-%m-%d")
                                    except ValueError:
                                        raise ValueError(f"Invalid date format in row {row_number}: {value}. Expected format: YYYY-MM-DD")
                            
                        
                        elif required_field in ['description', 'category']:
                            if not value:
                                raise ValueError(f"{required_field.capitalize()} is required in row {row_number}")
                            expense[required_field] = value
                        
                        else:
                            expense[required_field] = value
                    
                    # Add any additional fields that might be in the CSV
                    for field_name, field_value in row.items():
                        normalized_field = field_name.lower().strip()
                        if normalized_field not in [f.lower() for f in required_fields]:
                            # Add extra fields with original case
                            expense[field_name] = field_value.strip() if field_value else ''
                    
                    expenses_data.append(expense)
                    
                except ValueError as ve:
                    raise HTTPException(status_code=400, detail=str(ve))
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error processing row {row_number}: {str(e)}")
                    

            # Check if we have any data
            if not expenses_data:
                raise HTTPException(status_code=400, detail="No valid data found in CSV file")
            
            # Load existing expenses data if any
            try:
                existing_data: List[Dict[str, Any]] = self.storage.load_file(user_id, 'expenses.json') or []
            except:
                existing_data = []
            
            # Combine existing data with new data
            # You might want to add logic here to prevent duplicates or handle ID assignment
            combined_data = existing_data + expenses_data
            
            # Save combined data to storage
            self.storage.save_file(user_id, 'expenses.json', combined_data)
            
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {str(e)}")
        finally:
            # Ensure file is closed
            if hasattr(file.file, 'close'):
                file.file.close()