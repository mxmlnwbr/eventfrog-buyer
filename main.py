#!/usr/bin/env python3
"""
Eventfrog Ticket Buyer - Automated ticket purchasing script for Chilbi Gersau - Partyboot 2025
"""

import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ticket_buyer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Print a message to confirm the script is starting
print("Script is starting - initializing logging...")
logger.info("Logging initialized")

# Constants
EVENT_URL = "https://eventfrog.ch/en/p/concert/other-music-genres/chilbi-gersau-partyboot-2025-7295184020190557758.html"
TICKET_TYPE = "RAVE THE WAVE mit DJ SCHIFFJANONE (Ab 18J)"
MAX_TICKET_QUANTITY = 3
REFRESH_INTERVAL = 0.1  # Refresh interval in seconds
SALE_DATE = "13.04.2025 19:00"  # Expected sale date and time

# User information - REPLACE WITH YOUR ACTUAL INFORMATION
USER_INFO = {
    "email": os.getenv("EMAIL", "your.email@example.com"),
    "first_name": "Your",
    "last_name": "Name",
    "phone": "0123456789",
    "address": "Your Street 123",
    "zip": "1234",
    "city": "Your City"
}

# Login credentials
LOGIN_EMAIL = os.getenv("EMAIL")
LOGIN_PASSWORD = os.getenv("PASSWORD")

class EventfrogTicketBuyer:
    def __init__(self):
        self.driver = None
        print("Initializing EventfrogTicketBuyer...")
        logger.info("Initializing EventfrogTicketBuyer instance")
        try:
            self.setup_driver()
            self.current_ticket_quantity = MAX_TICKET_QUANTITY
            logger.info("EventfrogTicketBuyer initialized successfully")
        except Exception as e:
            print(f"Error during initialization: {str(e)}")
            logger.error(f"Error during initialization: {str(e)}")
            raise
        
    def setup_driver(self):
        """Initialize the Chrome WebDriver with appropriate options."""
        try:
            print("Setting up Chrome WebDriver...")
            logger.info("Setting up Chrome WebDriver")
            
            chrome_options = Options()
            # Uncomment the line below if you want to run in headless mode
            # chrome_options.add_argument("--headless")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-notifications")
            
            print("Creating Chrome WebDriver instance...")
            logger.info("Creating Chrome WebDriver instance")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            print("Maximizing window...")
            logger.info("Maximizing window")
            self.driver.maximize_window()
            
            print("WebDriver initialized successfully")
            logger.info("WebDriver initialized successfully")
        except Exception as e:
            print(f"Error setting up WebDriver: {str(e)}")
            logger.error(f"Error setting up WebDriver: {str(e)}")
            raise
    
    def check_ticket_availability(self):
        """Check if tickets are available for purchase."""
        try:
            self.driver.get(EVENT_URL)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Checking ticket availability at {current_time}")
            logger.info(f"Current URL: {self.driver.current_url}")
            
            # Look for indicators that tickets are available
            try:
                # Check if there's a "Buy tickets" button or similar
                buy_button = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Buy') or contains(text(), 'Purchase') or contains(text(), 'Get tickets')]"))
                )
                logger.info(f"Found buy button with text: '{buy_button.text}'")
                logger.info("Tickets appear to be available! Proceeding with purchase...")
                return True
            except TimeoutException:
                # Check if the page contains text indicating tickets are not yet available
                page_source = self.driver.page_source
                if "Ticket sale online starts on 13.04.2025 19:00" in page_source:
                    logger.info("Found message: 'Ticket sale online starts on 13.04.2025 19:00'")
                    logger.info("Tickets are not yet available. Will check again.")
                    return False
                else:
                    # If the expected text is not found, the page might have changed
                    logger.info("Expected message about ticket sale date not found.")
                    logger.info("Page structure has changed. This might indicate tickets are available.")
                    return True
                    
        except Exception as e:
            logger.error(f"Error checking ticket availability: {str(e)}")
            return False
    
    def purchase_tickets(self):
        """Attempt to purchase tickets once they're available."""
        try:
            # Click on the buy tickets button
            buy_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Buy') or contains(text(), 'Purchase') or contains(text(), 'Get tickets')]"))
            )
            buy_button.click()
            logger.info("Clicked on buy tickets button")
            
            # Try purchasing with current quantity
            return self._try_purchase_with_current_quantity()
            
        except Exception as e:
            logger.error(f"Error during purchase process: {str(e)}")
            return False
    
    def _try_purchase_with_current_quantity(self):
        """Try to purchase tickets with the current quantity setting."""
        try:
            # Select ticket type
            self._select_ticket_type()
            
            # Add tickets to cart
            self._add_to_cart()
            
            # Check if there was an error (like quantity limit exceeded)
            try:
                error_message = WebDriverWait(self.driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'alert')]"))
                )
                error_text = error_message.text
                logger.warning(f"Error message found: {error_text}")
                
                # If there's an error and we still have room to decrease quantity
                if self.current_ticket_quantity > 1:
                    self.current_ticket_quantity -= 1
                    logger.info(f"Reducing ticket quantity to {self.current_ticket_quantity} and retrying")
                    self.driver.get(EVENT_URL)  # Refresh and start over
                    return self.purchase_tickets()
                else:
                    logger.error("Failed to purchase even with minimum quantity")
                    return False
            except TimeoutException:
                # No error found, continue with checkout
                pass
            
            # Proceed to checkout
            self._proceed_to_checkout()
            
            # Fill in user information
            self._fill_user_info()
            
            # Complete purchase
            self._complete_purchase()
            
            logger.info(f"Purchase process completed successfully with {self.current_ticket_quantity} tickets!")
            return True
            
        except Exception as e:
            logger.error(f"Error during purchase attempt with quantity {self.current_ticket_quantity}: {str(e)}")
            
            # If we still have room to decrease quantity, try again
            if self.current_ticket_quantity > 1:
                self.current_ticket_quantity -= 1
                logger.info(f"Reducing ticket quantity to {self.current_ticket_quantity} and retrying")
                self.driver.get(EVENT_URL)  # Refresh and start over
                return self.purchase_tickets()
            else:
                logger.error("Failed to purchase even with minimum quantity")
                return False
    
    def _select_ticket_type(self):
        """Select the desired ticket type."""
        try:
            # Wait for ticket options to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{TICKET_TYPE}')]"))
            )
            
            # Find the ticket type and click on it
            ticket_element = self.driver.find_element(By.XPATH, f"//div[contains(text(), '{TICKET_TYPE}')]")
            ticket_element.click()
            logger.info(f"Selected ticket type: {TICKET_TYPE}")
            
            # Set quantity if needed
            if self.current_ticket_quantity > 1:
                # This will need to be adjusted based on the actual page structure
                quantity_input = self.driver.find_element(By.XPATH, "//input[@type='number']")
                quantity_input.clear()
                quantity_input.send_keys(str(self.current_ticket_quantity))
                logger.info(f"Set ticket quantity to {self.current_ticket_quantity}")
                
        except Exception as e:
            logger.error(f"Error selecting ticket type: {str(e)}")
            raise
    
    def _add_to_cart(self):
        """Add selected tickets to cart."""
        try:
            add_to_cart_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to cart') or contains(text(), 'Continue')]"))
            )
            add_to_cart_button.click()
            logger.info("Added tickets to cart")
            
        except Exception as e:
            logger.error(f"Error adding tickets to cart: {str(e)}")
            raise
    
    def _proceed_to_checkout(self):
        """Proceed to checkout page."""
        try:
            checkout_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Checkout') or contains(text(), 'Proceed to payment')]"))
            )
            checkout_button.click()
            logger.info("Proceeded to checkout")
            
        except Exception as e:
            logger.error(f"Error proceeding to checkout: {str(e)}")
            raise
    
    def _fill_user_info(self):
        """Fill in user information on checkout page."""
        try:
            # Wait for form to be visible
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Fill in email
            email_field = self.driver.find_element(By.ID, "email")
            email_field.send_keys(USER_INFO["email"])
            
            # Fill in name
            first_name_field = self.driver.find_element(By.ID, "firstName")
            first_name_field.send_keys(USER_INFO["first_name"])
            
            last_name_field = self.driver.find_element(By.ID, "lastName")
            last_name_field.send_keys(USER_INFO["last_name"])
            
            # Fill in other details
            phone_field = self.driver.find_element(By.ID, "phone")
            phone_field.send_keys(USER_INFO["phone"])
            
            address_field = self.driver.find_element(By.ID, "address")
            address_field.send_keys(USER_INFO["address"])
            
            zip_field = self.driver.find_element(By.ID, "zip")
            zip_field.send_keys(USER_INFO["zip"])
            
            city_field = self.driver.find_element(By.ID, "city")
            city_field.send_keys(USER_INFO["city"])
            
            logger.info("Filled in user information")
            
        except Exception as e:
            logger.error(f"Error filling user information: {str(e)}")
            raise
    
    def _complete_purchase(self):
        """Complete the purchase process."""
        try:
            # Accept terms and conditions if present
            try:
                terms_checkbox = self.driver.find_element(By.XPATH, "//input[@type='checkbox']")
                terms_checkbox.click()
                logger.info("Accepted terms and conditions")
            except NoSuchElementException:
                logger.info("No terms and conditions checkbox found")
            
            # Click on complete purchase button
            complete_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Complete purchase') or contains(text(), 'Pay now')]"))
            )
            
            # Uncomment the line below to actually complete the purchase
            # complete_button.click()
            logger.info("Purchase button found but not clicked (safety measure)")
            
            # For safety, we're not actually clicking the final purchase button
            # Remove the safety comment above and uncomment the line below when ready to use for real
            # logger.info("Completed purchase")
            
        except Exception as e:
            logger.error(f"Error completing purchase: {str(e)}")
            raise
    
    def login(self):
        """Login to Eventfrog."""
        MAX_LOGIN_ATTEMPTS = 3
        attempt = 0
        
        while attempt < MAX_LOGIN_ATTEMPTS:
            attempt += 1
            logger.info(f"Login attempt {attempt}/{MAX_LOGIN_ATTEMPTS}")
            
            try:
                logger.info(f"Attempting to login with email: {LOGIN_EMAIL}")
                
                # Navigate to login page
                self.driver.get("https://eventfrog.ch/en/login.html")
                logger.info(f"Navigated to login page: {self.driver.current_url}")
                
                # Wait for page to load
                time.sleep(3)
                
                # Handle cookies consent modal if it appears
                try:
                    # Try different selectors for the accept cookies button
                    cookie_button_selectors = [
                        "//button[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'OK')]",
                        "//a[contains(text(), 'Accept') or contains(text(), 'Agree') or contains(text(), 'OK')]",
                        "//button[contains(@class, 'accept') or contains(@class, 'agree')]",
                        "//button[@id='accept-cookies']",
                        "//button[@id='acceptCookies']"
                    ]
                    
                    for selector in cookie_button_selectors:
                        try:
                            cookie_buttons = self.driver.find_elements(By.XPATH, selector)
                            if cookie_buttons:
                                for button in cookie_buttons:
                                    if button.is_displayed():
                                        logger.info(f"Found cookie consent button with text: '{button.text}'")
                                        button.click()
                                        logger.info("Clicked cookie consent button")
                                        time.sleep(1)  # Wait for modal to disappear
                                        break
                        except:
                            continue
                    
                    # Also try with JavaScript as a fallback
                    cookie_js = """
                        // Try to find and click any cookie accept button
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var button = buttons[i];
                            var text = button.textContent.toLowerCase();
                            if (text.includes('accept') || text.includes('agree') || text.includes('ok') || 
                                text.includes('cookie') || text.includes('consent')) {
                                button.click();
                                return true;
                            }
                        }
                        return false;
                    """
                    
                    cookie_clicked = self.driver.execute_script(cookie_js)
                    if cookie_clicked:
                        logger.info("Clicked cookie consent button using JavaScript")
                        time.sleep(1)  # Wait for modal to disappear
                
                except Exception as e:
                    logger.warning(f"Error handling cookie consent: {str(e)}")
                
                # Use JavaScript to fill in the form and submit
                # This bypasses element visibility and interactability issues
                login_script = f"""
                    // Fill in username and password
                    document.getElementById('username').value = '{LOGIN_EMAIL}';
                    document.getElementById('password').value = '{LOGIN_PASSWORD}';
                    
                    // Click the submit button
                    document.getElementById('submit').click();
                """
                
                self.driver.execute_script(login_script)
                logger.info("Executed JavaScript to fill in login form and click submit button")
                
                # Wait for login to complete
                time.sleep(5)
                
                # Check if login was successful
                if "login" not in self.driver.current_url.lower():
                    logger.info(f"Login successful - current URL: {self.driver.current_url}")
                    
                    # Additional verification - check for elements that indicate logged-in state
                    try:
                        # Look for common elements that appear when logged in
                        logged_in_indicators = [
                            "//a[contains(@href, 'logout')]",
                            "//div[contains(@class, 'user-menu')]",
                            "//span[contains(text(), 'My Account')]",
                            "//a[contains(@href, 'account')]",
                            "//a[contains(text(), 'My Profile')]"
                        ]
                        
                        for indicator in logged_in_indicators:
                            try:
                                element = self.driver.find_element(By.XPATH, indicator)
                                logger.info(f"Confirmed logged in state - found element: {indicator}")
                                return True
                            except:
                                continue
                        
                        # If we didn't find any indicators but we're not on the login page,
                        # we'll assume login was successful
                        logger.info("No specific logged-in indicators found, but not on login page - assuming success")
                        return True
                        
                    except Exception as e:
                        logger.warning(f"Error checking for logged-in indicators: {str(e)}")
                        # Still return True if we're not on the login page
                        return True
                else:
                    logger.warning(f"Login attempt {attempt} failed - still on login page")
                    
                    # Try to identify error messages
                    try:
                        error_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'error') or contains(@class, 'alert')]")
                        if error_elements:
                            for error in error_elements:
                                logger.error(f"Login error message: {error.text}")
                    except:
                        pass
                    
                    if attempt < MAX_LOGIN_ATTEMPTS:
                        logger.info("Waiting before next attempt...")
                        time.sleep(2)
                    else:
                        logger.error("Maximum login attempts reached")
                        return False
                
            except Exception as e:
                logger.error(f"Error during login attempt {attempt}: {str(e)}")
                if attempt < MAX_LOGIN_ATTEMPTS:
                    logger.info("Waiting before next attempt...")
                    time.sleep(2)
                else:
                    logger.error("Maximum login attempts reached")
                    return False
        
        return False
    
    def run(self):
        """Main execution method to monitor and purchase tickets."""
        try:
            logger.info("Starting Eventfrog Ticket Buyer")
            logger.info(f"Monitoring event: {EVENT_URL}")
            logger.info(f"Refresh interval: {REFRESH_INTERVAL} seconds")
            logger.info(f"Will try with max {MAX_TICKET_QUANTITY} tickets, reducing if needed")
            logger.info(f"Target ticket type: {TICKET_TYPE}")
            logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Expected ticket sale time: {SALE_DATE}")
            
            # Login is required - must succeed before continuing
            logger.info("Logging in to Eventfrog is required before monitoring tickets")
            if not self.login():
                logger.error("Failed to log in to Eventfrog. Cannot continue without login.")
                logger.error("Please check your credentials and try again.")
                return
            
            logger.info("Successfully logged in to Eventfrog. Starting ticket monitoring.")
            
            tickets_purchased = False
            retries = 0
            check_count = 0
            
            # Parse the sale date for logging purposes
            try:
                sale_datetime = datetime.strptime(SALE_DATE, "%d.%m.%Y %H:%M")
                logger.info(f"Parsed sale date: {sale_datetime}")
            except Exception as e:
                logger.error(f"Error parsing sale date: {str(e)}")
                sale_datetime = None
            
            while not tickets_purchased:
                check_count += 1
                logger.info(f"Check #{check_count} for ticket availability")
                
                try:
                    logger.info(f"Checking ticket availability at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Navigate to the event page
                    self.driver.get(EVENT_URL)
                    logger.info(f"Current URL: {self.driver.current_url}")
                    
                    # Wait for the page to load
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # Check if tickets are available
                    try:
                        # First, check if there's a message indicating tickets are not yet available
                        not_available_message = self.driver.find_elements(By.XPATH, "//div[contains(text(), 'Ticket sale online starts on')]")
                        if not_available_message:
                            logger.info(f"Found message: '{not_available_message[0].text}'")
                            logger.info("Tickets are not yet available. Will check again.")
                        else:
                            # Look for ticket selection elements
                            ticket_elements = self.driver.find_elements(By.XPATH, f"//div[contains(text(), '{TICKET_TYPE}')]")
                            
                            if ticket_elements:
                                logger.info(f"Found ticket type: {TICKET_TYPE}")
                                
                                # Try to purchase tickets
                                if self.purchase_tickets():
                                    tickets_purchased = True
                                    logger.info("Tickets purchased successfully!")
                                    break
                                else:
                                    retries += 1
                                    if retries >= 3:
                                        logger.error("Maximum retries reached. Could not purchase tickets.")
                                        break
                                    logger.warning(f"Failed to purchase tickets. Retry {retries}/3")
                            else:
                                logger.info("Ticket type not found. Will check again.")
                    except Exception as e:
                        logger.error(f"Error checking ticket availability: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error during check #{check_count}: {str(e)}")
                
                # Always use the fastest refresh rate since the script will be started close to sale time
                logger.info(f"Waiting for {REFRESH_INTERVAL} seconds before next check...")
                time.sleep(REFRESH_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Process interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

def main():
    ticket_buyer = EventfrogTicketBuyer()
    ticket_buyer.run()

if __name__ == "__main__":
    main()
