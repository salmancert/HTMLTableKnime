import knime.extension as knext
import pandas as pd
from bs4 import BeautifulSoup
import logging
from pathlib import Path

# Set up logging
LOGGER = logging.getLogger(__name__)

@knext.node(
    name="HTML Table Reader",
    node_type=knext.NodeType.SOURCE,
    icon_path="../icons/icon.png",
    category="/community/io"
)
@knext.output_table(
    name="Output Table",
    description="Table data extracted from HTML file"
)
class HTMLTableReaderNode:
    """HTML Table Reader Node
    
    This node reads HTML tables from files saved with .xls extension.
    Many applications save HTML tables with .xls extension even though
    they contain HTML markup rather than Excel binary format.
    
    The node uses BeautifulSoup to parse the HTML and extract table data,
    then converts it to a pandas DataFrame for use in KNIME.
    """
    
    file_path = knext.StringParameter(
        "File Path",
        "Path to the HTML file (may have .xls extension)",
        default_value="",
    )
    
    table_index = knext.IntParameter(
        "Table Index",
        "Index of the table to extract (0-based, first table = 0)",
        default_value=0,
        min_value=0
    )
    
    has_header = knext.BoolParameter(
        "First Row as Header",
        "Use the first row as column headers",
        default_value=True
    )
    
    encoding = knext.StringParameter(
        "File Encoding",
        "Character encoding of the HTML file",
        default_value="utf-8",
        enum=["utf-8", "latin-1", "cp1252", "iso-8859-1", "ascii"]
    )
    
    skip_empty_rows = knext.BoolParameter(
        "Skip Empty Rows",
        "Skip rows that are completely empty",
        default_value=True
    )
    
    @file_path.validator
    def validate_file_path(self, value):
        if not value:
            raise ValueError("File path cannot be empty")
        
        path = Path(value)
        if not path.exists():
            raise ValueError(f"File does not exist: {value}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {value}")
    
    def configure(self, config_context):
        """Configure the node - return the output schema"""
        # We can't determine the exact schema without reading the file
        # Return a generic schema that will be updated during execution
        return None
    
    def execute(self, exec_context):
        """Execute the node - read and parse the HTML table"""
        try:
            LOGGER.info(f"Reading HTML file: {self.file_path}")
            
            # Read the file content
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                content = file.read()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            
            if not tables:
                raise ValueError("No HTML tables found in the file")
            
            if self.table_index >= len(tables):
                raise ValueError(
                    f"Table index {self.table_index} not found. "
                    f"File contains {len(tables)} table(s)"
                )
            
            LOGGER.info(f"Found {len(tables)} table(s), extracting table {self.table_index}")
            
            # Extract the specified table
            table = tables[self.table_index]
            
            # Convert table to DataFrame
            df = self._table_to_dataframe(table)
            
            if df.empty:
                exec_context.set_warning("The extracted table is empty")
                # Return empty DataFrame with at least one column
                df = pd.DataFrame({'Column_1': []})
            
            LOGGER.info(f"Successfully extracted table with shape: {df.shape}")
            
            return knext.Table.from_pandas(df)
            
        except Exception as e:
            LOGGER.error(f"Error reading HTML table: {str(e)}")
            raise RuntimeError(f"Failed to read HTML table: {str(e)}")
    
    def _table_to_dataframe(self, table):
        """Convert HTML table to pandas DataFrame"""
        rows = []
        
        # Extract all rows (including header rows)
        for tr in table.find_all('tr'):
            row_data = []
            
            # Extract cells (both td and th)
            for cell in tr.find_all(['td', 'th']):
                # Get text content and clean it
                cell_text = cell.get_text(strip=True)
                
                # Handle colspan
                colspan = int(cell.get('colspan', 1))
                for _ in range(colspan):
                    row_data.append(cell_text)
            
            if row_data:  # Only add non-empty rows
                rows.append(row_data)
        
        if not rows:
            return pd.DataFrame()
        
        # Skip empty rows if requested
        if self.skip_empty_rows:
            rows = [row for row in rows if any(cell.strip() for cell in row)]
        
        if not rows:
            return pd.DataFrame()
        
        # Ensure all rows have the same length
        max_cols = max(len(row) for row in rows)
        normalized_rows = []
        for row in rows:
            # Pad short rows with empty strings
            while len(row) < max_cols:
                row.append('')
            # Truncate long rows
            normalized_rows.append(row[:max_cols])
        
        # Create DataFrame
        if self.has_header and len(normalized_rows) > 0:
            # Use first row as header
            df = pd.DataFrame(normalized_rows[1:], columns=normalized_rows[0])
            
            # Clean column names
            df.columns = [self._clean_column_name(col) for col in df.columns]
        else:
            # Generate generic column names
            df = pd.DataFrame(normalized_rows)
            df.columns = [f'Column_{i+1}' for i in range(len(df.columns))]
        
        # Convert data types
        df = self._convert_data_types(df)
        
        return df
    
    def _clean_column_name(self, name):
        """Clean column names to be valid KNIME column names"""
        # Remove extra whitespace
        name = str(name).strip()
        
        # Replace empty names
        if not name:
            return "Unnamed_Column"
        
        # Replace problematic characters
        name = name.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        
        # Collapse multiple spaces
        while '  ' in name:
            name = name.replace('  ', ' ')
        
        return name
    
    def _convert_data_types(self, df):
        """Attempt to convert columns to appropriate data types"""
        for col in df.columns:
            # Skip if column is already non-string
            if df[col].dtype != 'object':
                continue
            
            # Try to convert to numeric
            try:
                # First try integer
                numeric_series = pd.to_numeric(df[col], errors='coerce')
                
                # Check if all non-null values are integers
                if numeric_series.notna().any():
                    if numeric_series.dropna().apply(lambda x: x.is_integer()).all():
                        df[col] = numeric_series.astype('Int64')  # Nullable integer
                    else:
                        df[col] = numeric_series
                        
            except (ValueError, TypeError):
                # If numeric conversion fails, try datetime
                try:
                    datetime_series = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    # Only convert if at least some values are valid dates
                    if datetime_series.notna().sum() > len(df) * 0.5:  # More than 50% valid dates
                        df[col] = datetime_series
                except (ValueError, TypeError):
                    # Keep as string if all conversions fail
                    pass
        
        return df
