# Gmail Search Tool

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

A Python-based GUI application for searching Gmail accounts using provided credentials and keywords. The tool validates email syntax and MX records, logs into Gmail via Selenium, and searches for emails matching specified keywords, saving results to `results.txt`. Built with PyQt5, it features a modern interface with a progress bar, headless mode, and customizable output.

## Features
- **Credential Processing**: Supports single email/password input or a file (`emails.txt`) with multiple `email:password` pairs.
- **Email Validation**: Checks email syntax and MX records before attempting login.
- **Gmail Search**: Searches Gmail for user-specified, comma-separated keywords (e.g., `google,invoice`).
- **Headless Mode**: Runs Selenium in headless mode by default for faster, invisible browser operation.
- **Progress Tracking**: Displays a progress bar for processing multiple credentials.
- **Logging**: Outputs detailed logs to the GUI and saves results to `results.txt`.
- **Custom Icon**: Uses `ProgmeleonTool.ico` for the executable, title bar, and Windows taskbar.
- **Thread-Safe**: Uses signals for GUI updates to prevent threading issues.
- **Cross-Platform**: Primarily tested on Windows, but compatible with Linux/Mac with minor adjustments.

## Prerequisites
- **Python**: Version 3.12 or higher (3.13 may have threading issues; see [Troubleshooting](#troubleshooting)).
- **Dependencies**:
  - `PyQt5`: For the GUI.
  - `selenium`: For browser automation.
  - `webdriver_manager`: For automatic ChromeDriver management.
  - `dnspython`: For MX record validation.
  - `pyinstaller`: For building the executable (optional).
- **Chrome Browser**: Required for Selenium (headless mode doesn’t need a visible window).
- **Icon File**: `ProgmeleonTool.ico` for the GUI and executable (included in the repository).

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/aligmirza/gmail-search-tool.git
   cd gmail-search-tool
   ```

2. **Install Dependencies**:
   ```bash
   pip install PyQt5 selenium webdriver_manager dnspython pyinstaller
   ```

3. **Verify Files**:
   Ensure the following files are in the project directory:
   - `main.py`: The main GUI script.
   - `gmail_search.py`: The backend search logic.
   - `ProgmeleonTool.ico`: The icon for the GUI and executable.

## Usage
1. **Run the Application**:
   ```bash
   python main.py
   ```
   The GUI will open, displaying fields for credentials, keywords, and output directory.

2. **Configure the Tool**:
   - **Credentials**:
     - Enter a single `email` and `password`, or
     - Click "Browse" to select an `emails.txt` file with `email:password` pairs (one per line, e.g., `user@example.com:pass123`).
   - **Options**:
     - Check "Run in Headless Mode" (default) for faster, invisible browser operation.
   - **Keywords**:
     - Enter comma-separated keywords (e.g., `google,invoice`).
   - **Output Directory**:
     - Click "Browse" to select a directory for `results.txt`.

3. **Start the Search**:
   - Click "Start Search" to process credentials and search Gmail.
   - Monitor the progress bar and log output in the GUI.
   - Results are saved to `results.txt` in the specified directory, including:
     - Invalid email syntax.
     - No valid MX records.
     - Login failures.
     - Search results for valid logins.

4. **Stop or Close**:
   - Click "Stop Search" to halt processing (some operations may complete).
   - Close the window to terminate the application cleanly.

## Building the Executable
To create a standalone `.exe` for Windows:
1. **Run PyInstaller**:
   ```bash
   pyinstaller --clean --onefile --noconsole --icon=ProgmeleonTool.ico --name=GmailSearchGUI_logo --add-data "ProgmeleonTool.ico;." --add-data "gmail_search.py;." main.py
   ```
   - `--clean`: Clears previous build cache.
   - `--onefile`: Creates a single `.exe`.
   - `--noconsole`: Runs without a console window.
   - `--icon`: Sets the `.exe` icon.
   - `--add-data`: Includes the icon and `gmail_search.py`.

2. **Find the Executable**:
   - The `.exe` is in `dist\GmailSearchGUI_logo.exe`.

3. **Run the `.exe`**:
   ```bash
   dist\GmailSearchGUI_logo.exe
   ```
   - The icon (`ProgmeleonTool.ico`) appears in File Explorer, the GUI title bar, and the Windows taskbar.

## Troubleshooting
- **Taskbar Icon Not Showing**:
  - Clear the Windows icon cache:
    ```bash
    del %LocalAppData%\IconCache.db
    taskkill /IM explorer.exe /F
    start explorer.exe
    ```
  - Unpin and re-pin the `.exe` to the taskbar.
  - Check `app.log` for icon path errors (e.g., `Icon file not found`).

- **Threading `SystemError` in Python 3.13**:
  - Use Python 3.12 for better compatibility:
    ```bash
    py -3.12 -m pip install PyQt5 selenium webdriver_manager dnspython pyinstaller
    py -3.12 -m PyInstaller --clean --onefile --noconsole --icon=ProgmeleonTool.ico --name=GmailSearchGUI_logo --add-data "ProgmeleonTool.ico;." --add-data "gmail_search.py;." main.py
    ```

- **Selenium `DevTools` Log**:
  - Harmless in non-headless mode. To suppress, add to `login_to_gmail` in `gmail_search.py`:
    ```python
    chrome_options.add_argument("--log-level=3")
    ```

- **Icon Missing in `.exe`**:
  - Verify `ProgmeleonTool.ico` is in the project directory and included via `--add-data`.
  - Check `build\GmailSearchGUI_logo\Analysis-00.toc` for `('ProgmeleonTool.ico', ...)`.

- **Button Icons Missing**:
  - `QIcon.fromTheme` may not work on Windows. Install `qtawesome` for consistent icons:
    ```bash
    pip install qtawesome
    ```
    Update `main.py`:
    ```python
    import qtawesome as qta
    self.browse_button.setIcon(qta.icon('fa.folder-open'))
    ```
    Update PyInstaller:
    ```bash
    pyinstaller --clean --onefile --noconsole --icon=ProgmeleonTool.ico --name=GmailSearchGUI_logo --add-data "ProgmeleonTool.ico;." --add-data "gmail_search.py;." --hidden-import=qtawesome main.py
    ```

## Contributing
1. Fork the repository.
2. Create a branch (`git checkout -b feature/your-feature`).
3. Commit changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.md) file for details.

## Acknowledgments
- Built with [PyQt5](https://www.riverbankcomputing.com/software/pyqt/), [Selenium](https://www.selenium.dev/), and [PyInstaller](https://pyinstaller.org/).
- Icon handling inspired by community solutions for PyQt5 and Windows taskbar integration.
