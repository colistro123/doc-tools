# URL Resolver and Link Checker

This script processes and validates URLs in Markdown files within a given directory. It resolves relative URLs, checks for file existence, and verifies external links to ensure proper navigation within a web-like structure.

## Features

- Resolves relative URLs (`../`, `./`) and absolute paths.
- Validates file paths against a specified directory structure.
- Ensures URLs correspond to real files or accessible web pages.
- Excludes specific URL patterns (e.g., `mailto:`, `discord.gg`).
- Provides feedback on broken or invalid links.

## Requirements

- Python 3.x
- Hugo server running at `http://localhost:1313/docs/` (for URL checking).

## How It Works

1. **Directory Traversal**: The script scans a specified directory for Markdown files.
2. **Link Extraction**: Extracts all Markdown links from files.
3. **Link Resolution**: Converts relative paths into absolute file paths.
4. **File Validation**: Checks if the resolved file exists within the defined directory.
5. **External Link Validation**: Uses `curl` to verify external URLs.

## Usage

1. Ensure Hugo is running:
 ```bash
   hugo serve -D
 ```

2. Run the script:
 ```bash
   python check_links.py
 ```

## Limitations

- The script relies on Hugo to resolve links correctly in a web-like manner.
- Links pointing to dynamically generated content may not resolve properly.
- Requires `curl` for external URL checking.

## Configuration

- **ROOT_DIR**: Base directory for file validation.
- **BASE_URL**: Base URL for external link validation.
- **SKIP_LINKS**: Patterns to skip during validation.

## Author

- colistro123 ([colistro123@aol.com](mailto:colistro123@aol.com))

## License

This project is licensed under the MIT License.