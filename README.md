# Media Downloader

This project is a Python script to fetch and download media items and gallery content from the ParentZone API (parentzone.me).

## Features
- Fetch posts and gallery items from the API.
- Download media files to a local directory.
- Automatically handles API key retrieval from environment variables or a local file.
- Updates the creation date on the downloaded files based on the metadata.

## Requirements
- Python 3.7 or higher
- `requests` library (version 2.25.1 or higher)
- `python-dateutil` library (version 2.9.0 or higher)

## Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/skycubeuk/media-downloader.git
   cd media-downloader
   ```

2. **Install Dependencies**:
   Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the API Key**:
   The script will prompt you to enter your API key if it is not already set in the `config.ini` file or as an environment variable. The key will be saved to the `config.ini` file for future use.

   Alternatively, you can set the `API_KEY` environment variable:
   ```bash
   export API_KEY=your_api_key
   ```

   If you don't know how to extract the API key, refer to the [Extracting the API Key](#extracting-the-api-key) section below.

## Configuration

The script uses a `config.ini` file to store configuration settings, including the API key and directory paths. If the API key is not set in the environment or the `config.ini` file, the script will prompt you to enter it and save it automatically.

### Example `config.ini` File
```ini
[Credentials]
api_key=your_api_key

[Paths]
log_dir=./log
out_dir=./out
```

- **`[Credentials]`**: Stores the API key.
- **`[Paths]`**: Specifies the directories for logs and output files.

## Usage

Run the script using:
```bash
python main.py
```

The script will:
1. Fetch posts and gallery items from the API.
2. Download media files to the `./out` directory.

## Extracting the API Key

To extract the API key from the web application, follow these steps:

1. **Open the Web Application**:
   - Navigate to the web application where the API is being used.

2. **Open Developer Tools**:
   - Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or `Cmd+Option+I` (Mac) to open the browser's developer tools.

3. **Go to the Network Tab**:
   - Click on the "Network" tab in the developer tools.

4. **Filter Requests**:
   - Reload the page and look for network requests. Use the filter box to search for requests to the API endpoint (e.g., `https://api.parentzone.me`).

5. **Inspect Headers**:
   - Click on one of the requests to the API. In the "Headers" section, look for the `x-api-key` header under "Request Headers".

6. **Copy the API Key**:
   - Copy the value of the `x-api-key` header.

7. **Save the API Key**:
   - Paste the API key into the `config.ini` file or set it as an environment variable.

## License

This project is licensed under the MIT License.
