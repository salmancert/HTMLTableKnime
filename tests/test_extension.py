import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from extension import HTMLTableReaderNode

class MockExecutionContext:
    def __init__(self):
        self.warnings = []
    
    def set_warning(self, msg):
        self.warnings.append(msg)

class TestHTMLTableReaderNode(unittest.TestCase):
    
    def setUp(self):
        self.sample_html = """
        <!DOCTYPE html>
        <html>
        <body>
            <table border="1">
                <tr>
                    <th>Product</th>
                    <th>Sales</th>
                    <th>Region</th>
                </tr>
                <tr>
                    <td>Widget A</td>
                    <td>15000</td>
                    <td>North</td>
                </tr>
                <tr>
                    <td>Widget B</td>
                    <td>22000</td>
                    <td>South</td>
                </tr>
            </table>
        </body>
        </html>
        """
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.xls', delete=False)
        self.temp_file.write(self.sample_html)
        self.temp_file.close()
        
    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_basic_table_reading(self):
        """Test basic table reading functionality"""
        node = HTMLTableReaderNode()
        node.file_path = self.temp_file.name
        node.table_index = 0
        node.has_header = True
        node.encoding = "utf-8"
        node.skip_empty_rows = True
        
        exec_context = MockExecutionContext()
        result = node.execute(exec_context)
        df = result.to_pandas()
        
        # Check basic properties
        self.assertEqual(df.shape, (2, 3))
        self.assertListEqual(list(df.columns), ['Product', 'Sales', 'Region'])
        self.assertEqual(df.iloc[0]['Product'], 'Widget A')
        self.assertEqual(df.iloc[1]['Sales'], 22000)  # Should be converted to int
    
    def test_file_validation(self):
        """Test file path validation"""
        node = HTMLTableReaderNode()
        
        # Test empty path
        with self.assertRaises(ValueError):
            node.validate_file_path("")
        
        # Test non-existent file
        with self.assertRaises(ValueError):
            node.validate_file_path("/path/that/does/not/exist.xls")
    
    def test_no_header_mode(self):
        """Test reading without headers"""
        node = HTMLTableReaderNode()
        node.file_path = self.temp_file.name
        node.table_index = 0
        node.has_header = False  # Don't use first row as header
        node.encoding = "utf-8"
        node.skip_empty_rows = True
        
        exec_context = MockExecutionContext()
        result = node.execute(exec_context)
        df = result.to_pandas()
        
        # Should have 3 rows (including header row as data)
        self.assertEqual(df.shape, (3, 3))
        self.assertListEqual(list(df.columns), ['Column_1', 'Column_2', 'Column_3'])
        self.assertEqual(df.iloc[0]['Column_1'], 'Product')  # Header becomes data

if __name__ == '__main__':
    print("Running HTML Table Reader Extension Tests")
    unittest.main()
