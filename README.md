# Eventfrog Ticket Buyer

Automated ticket purchasing script for Chilbi Gersau - Partyboot 2025. This script monitors the event page and automatically attempts to purchase tickets when they become available.

## Features

- Automatically monitors the event page for ticket availability
- Attempts to purchase tickets as soon as they become available
- Adjusts ticket quantity if maximum is not available
- Provides detailed logging of the purchase process

## Requirements

- Python 3.12 or higher
- Chrome browser installed
- ChromeDriver (compatible with your Chrome version)
- Selenium package

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/eventfrog-buyer.git
   cd eventfrog-buyer
   ```

2. Install the required dependencies:
   ```
   pip install -e .
   ```

3. Make sure you have Chrome and ChromeDriver installed. ChromeDriver should be in your PATH or specified in the script.

## Configuration

Before running the script, update the following information in `main.py`:

1. **User Information**: Replace the placeholder values in the `USER_INFO` dictionary with your actual information:
   ```python
   USER_INFO = {
       "email": "your.email@example.com",
       "first_name": "Your",
       "last_name": "Name",
       "phone": "0123456789",
       "address": "Your Street 123",
       "zip": "1234",
       "city": "Your City"
   }
   ```

2. **Ticket Selection**: Modify the ticket type and quantity based on your preferences:
   ```python
   TICKET_TYPE = "RAVE THE WAVE mit DJ SCHIFFJANONE (Ab 18J)"  # Example ticket type
   MAX_TICKET_QUANTITY = 3  # Maximum number of tickets to try purchasing
   ```

3. **Safety Measure**: By default, the script will not actually complete the purchase (for safety). When you're ready to use it for real, uncomment the appropriate line in the `_complete_purchase` method:
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
1. Start monitoring the event page
2. Check for ticket availability
3. Attempt to purchase tickets when they become available
4. Log the process to both the console and a file named `ticket_buyer.log`

You can stop the script at any time by pressing `Ctrl+C`.

## Important Notes

- This script is designed for educational purposes and personal use only.
- Be aware that automated ticket purchasing may be against the terms of service of some websites.
- The script includes a safety measure to prevent accidental purchases - you need to uncomment a line to enable actual purchasing.
- The script may need adjustments based on changes to the Eventfrog website structure.
- The ticket sale for this event starts on April 13, 2025, at 19:00.

## License

This project is licensed under the MIT License - see the LICENSE file for details.