# HTMLTableKnime
```markdown
# HTML Table Reader Extension for KNIME

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![KNIME Version](https://img.shields.io/badge/KNIME-5.5+-blue.svg)](https://www.knime.com/)
[![Python Version](https://img.shields.io/badge/Python-3.11+-green.svg)](https://www.python.org/)

A KNIME extension that reads HTML tables from files, even when they are saved with `.xls` extension. This is common when exporting data from web applications that save HTML tables with Excel file extensions.

## 🚀 Features

- **Read HTML tables from files**: Supports files with `.xls`, `.html`, `.htm` extensions
- **Multiple table support**: Select which table to extract when multiple tables exist
- **Flexible encoding**: Support for various character encodings (UTF-8, Latin-1, etc.)
- **Header detection**: Option to use first row as column headers
- **Data type inference**: Automatically converts numeric and date columns
- **Error handling**: Comprehensive validation and error reporting

## 📦 Installation

### Prerequisites

- KNIME Analytics Platform 5.5 or higher
- Python 3.11+
- [Pixi package manager](https://pixi.sh/) (recommended)

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/salmancert/HTMLTableKnime.git
   cd HTMLTableKnime
   ```

2. **Install dependencies**:
   ```bash
   pixi install
   ```

3. **Configure KNIME**:
   - Edit your `knime.ini` file and add:
     ```
     -Dknime.python.extension.config=/path/to/HTMLTableKnime/config.yml
     ```

4. **Start KNIME** and find the node under "Community Nodes" → "IO"

### Production Installation

1. **Build the extension**:
   ```bash
   pixi run build dest=./local-update-site
   ```

2. **Install in KNIME**:
   - File → Preferences → Install/Update → Available Software Sites
   - Add the `local-update-site` folder as a local update site
   - Install via File → Install KNIME Extensions

## 🔧 Usage

### Node Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| File Path | Path to the HTML file to read | (empty) |
| Table Index | Zero-based index of table to extract | 0 |
| First Row as Header | Use first row as column names | True |
| File Encoding | Character encoding of the file | utf-8 |
| Skip Empty Rows | Skip rows with no content | True |

### Example

```html
<!-- This content in a file with .xls extension -->
<table>
    <tr><th>Product</th><th>Sales</th></tr>
    <tr><td>Widget A</td><td>15000</td></tr>
    <tr><td>Widget B</td><td>22000</td></tr>
</table>
```

The node will extract this as a proper KNIME table with columns "Product" and "Sales".

## 🧪 Testing

Run the test suite:

```bash
pixi run test
```

Or manually test with sample files:

```bash
python tests/test_extension.py
```

## 🛠️ Development

### Project Structure

```
src/extension.py          # Main node implementation
icons/icon.png            # Node icon
demos/                    # Example workflows
tests/                    # Test files and sample data
knime.yml                 # Extension metadata
pixi.toml                 # Environment configuration
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pixi run test`
6. Commit changes: `git commit -am 'Add feature'`
7. Push to branch: `git push origin feature-name`
8. Submit a Pull Request

## 📋 Common Use Cases

- **Web application exports**: HTML tables saved with .xls extension
- **Email reports**: HTML email reports saved as files  
- **Web scraping**: HTML tables saved from web pages
- **Legacy systems**: Older systems exporting HTML as .xls

## 🐛 Troubleshooting

### Common Issues

**"No HTML tables found"**
- Verify the file contains `<table>` tags
- Check file encoding

**"Table index X not found"**  
- File has fewer tables than expected
- Use index 0 for first table

**Encoding errors**
- Try different encoding options
- Check original file encoding

## 📄 License

This project is licensed under the MIT License - see the [LICENSE.TXT](LICENSE.TXT) file for details.

## 🤝 Support

- 📖 [Documentation](README.md)
- 🐛 [Issue Tracker](https://github.com/yourusername/html-table-reader-extension/issues)
- 💬 [KNIME Community Forum](https://forum.knime.com/)

## 🏷️ Version History

- **1.0.0** - Initial release
  - Basic HTML table reading
  - Multiple table support
  - Data type inference
  - Comprehensive error handling

---

**Note**: This is a community extension and not officially supported by KNIME AG.
```
