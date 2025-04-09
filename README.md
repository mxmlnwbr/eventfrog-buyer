# Eventfrog Ticket Buyer

Automated ticket purchasing script for Chilbi Gersau - Partyboot 2025. This script monitors the event page and automatically attempts to purchase tickets when they become available.

## Features

- Automatically monitors the event page for ticket availability
- Logs in to Eventfrog with credentials from `.env` file
- Handles cookie consent modals automatically
- Attempts to purchase tickets as soon as they become available
- Adjusts ticket quantity if maximum is not available
- Uses a fast refresh rate (0.1 seconds) for optimal chances
- Provides detailed logging of the purchase process

## Requirements

- Python 3.12 or higher
- Chrome browser installed
- ChromeDriver (compatible with your Chrome version)
- Selenium package
- python-dotenv package

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/eventfrog-buyer.git
   cd eventfrog-buyer
   ```

2. Install the required dependencies using `uv`:
   ```
   uv sync
   ```

3. Make sure you have Chrome and ChromeDriver installed. ChromeDriver should be in your PATH or specified in the script.

4. Create a `.env` file with your Eventfrog credentials:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file to add your email and password.

## Configuration

Before running the script, you can customize the following settings in `main.py`:

1. **Ticket Selection**: Modify the ticket type and quantity based on your preferences:
   ```python
   TICKET_TYPE = "RAVE THE WAVE mit DJ SCHIFFJANONE (Ab 18J)"  # Example ticket type
   MAX_TICKET_QUANTITY = 3  # Maximum number of tickets to try purchasing
   REFRESH_INTERVAL = 0.1  # Refresh interval in seconds
   ```

2. **Safety Measure**: By default, the script will not actually complete the purchase (for safety). When you're ready to use it for real, uncomment the appropriate line in the `_complete_purchase` method:
   ```python
   # Uncomment the line below to actually complete the purchase
   # complete_button.click()
   ```

## Usage

Run the script with:

```
uv run python main.py
```

The script will:
1. Log in to your Eventfrog account using credentials from the `.env` file
2. Start monitoring the event page for ticket availability
3. Check for tickets every 0.1 seconds
4. Attempt to purchase tickets when they become available
5. Log the process to both the console and a file named `ticket_buyer.log`

You can stop the script at any time by pressing `Ctrl+C`.

## Important Notes

- This script is designed for educational purposes and personal use only.
- Be aware that automated ticket purchasing may be against the terms of service of some websites.
- The script includes a safety measure to prevent accidental purchases - you need to uncomment a line to enable actual purchasing.
- The script may need adjustments based on changes to the Eventfrog website structure.
- The ticket sale for this event starts on April 13, 2025, at 19:00.
- For best results, start the script about 5 minutes before the ticket sale begins.

## License

This project is licensed under the MIT License - see the LICENSE file for details.