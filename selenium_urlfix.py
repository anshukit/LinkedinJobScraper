from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse, parse_qs, unquote
from webdriver_manager.chrome import ChromeDriverManager
import time

class LinkedInLinkResolver:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless=new")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    def resolve_url(self, short_url):
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        
        try:
            driver.get(short_url)
            time.sleep(2)  # Basic wait - consider using WebDriverWait instead
            
            current_url = driver.current_url
            
            # Case 1: Direct redirect to job page
            if 'jobs/view' in current_url:
                return current_url
                
            # Case 2: Redirect to signup page with job URL in params
            if 'linkedin.com/signup' in current_url and 'session_redirect' in current_url:
                parsed = urlparse(current_url)
                params = parse_qs(parsed.query)
                if 'session_redirect' in params:
                    return unquote(params['session_redirect'][0])
            
            # Case 3: Interstitial warning page
            try:
                anchor = driver.find_element(By.CSS_SELECTOR, "a[href^='https']")
                resolved_url = anchor.get_attribute("href")
                if resolved_url and 'lnkd.in' not in resolved_url:
                    return resolved_url
            except:
                pass
                
            # If all else fails, return the current URL
            return current_url
            
        except Exception as e:
            print(f"Error resolving {short_url}: {str(e)}")
            return short_url  # Return original if we can't resolve
            
        finally:
            driver.quit()
