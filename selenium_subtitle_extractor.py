import os
import sys
import time
import requests
import json
import logging
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager # To auto-manage ChromeDriver

# --- Setup Logging ---
LOG_FILE = os.path.join(os.path.expanduser("~"), "selenium_subtitle_extractor.log")
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class SeleniumSubtitleExtractor:
    def __init__(self, download_dir, user_agent=None, headless=True, driver_path=None):
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)
        self.user_agent = user_agent if user_agent else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        self.headless = headless
        self.driver_path = driver_path # Optional: path to chromedriver.exe
        self.driver = None

        self.base_url = "https://vplatform.assembly.go.kr"
        self.subtitle_api_url = "https://videometaapi.assembly.go.kr/metaApi/api/subtitles/apiContentsSubtitleView.do"

        self.headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Referer': self.base_url + "/", # Dynamic referer will be set by Selenium
            'Origin': self.base_url,
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
    def _initialize_driver(self):
        logging.debug("Initializing Selenium WebDriver...")
        try:
            options = Options()
            options.add_argument(f"user-agent={self.user_agent}")
            if self.headless:
                options.add_argument("--headless")
                options.add_argument("--disable-gpu") # Required for headless on some OS
                options.add_argument("--window-size=1920,1080") # Set a default window size
            options.add_argument("--no-sandbox") # Bypass OS security model
            options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems

            if self.driver_path and os.path.exists(self.driver_path):
                service = Service(executable_path=self.driver_path)
                logging.debug(f"Using ChromeDriver from specified path: {self.driver_path}")
            else:
                # Use ChromeDriverManager to automatically download and manage ChromeDriver
                service = Service(ChromeDriverManager().install())
                logging.debug("Using ChromeDriver managed by webdriver_manager.")
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30) # 30 seconds timeout
            logging.debug("WebDriver initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize WebDriver: {e}", exc_info=True)
            if "Message: 'chromedriver' executable needs to be in PATH." in str(e) or "WebDriverException: Message: 'msedgedriver' executable needs to be in PATH." in str(e):
                logging.error("ChromeDriver/EdgeDriver not found. Please ensure it's in PATH or specify 'driver_path'.")
            raise

    def get_cont_id_from_cid(self, cid, sid=""):
        if not self.driver:
            self._initialize_driver()

        detail_page_url = f"{self.base_url}/video/seminar/FULL?cid={cid}&sid={sid}"
        logging.debug(f"Navigating to detail page: {detail_page_url}")
        
        try:
            self.driver.get(detail_page_url)
            time.sleep(2) # Add a small sleep to ensure DOM is ready, temporary debugging
            
            # Wait for the video player iframe to be present
            # Refined XPath: explicitly check for both parts
            iframe_element = WebDriverWait(self.driver, 20).until( # Increased timeout to 20s
                EC.presence_of_element_located((By.XPATH, "//iframe[contains(@src, 'player_meta.html') and contains(@src, 'videoId=')]"))
            )
            iframe_src = iframe_element.get_attribute('src')
            logging.debug(f"Found video player iframe src: {iframe_src}")

            # Extract videoId from iframe_src
            match = re.search(r'videoId=(\d+)', iframe_src)
            if match:
                cont_id = match.group(1)
                logging.info(f"Successfully extracted contId: {cont_id} for cid: {cid}")
                return cont_id
            else:
                logging.warning(f"Failed to extract contId from iframe src: {iframe_src} for cid: {cid}")
                return None
            
        except Exception as e:
            logging.error(f"Error getting contId for cid {cid} from {detail_page_url}: {e}", exc_info=True)
            return None

    def download_subtitle(self, cont_id, output_filename_base):
        subtitle_api_call_url = f"{self.subtitle_api_url}?maxLength=17&contId={cont_id}" # maxLength is arbitrary from original log
        logging.debug(f"Attempting to download subtitle from: {subtitle_api_call_url}")
        
        try:
            # Need to ensure headers are properly sent, especially Referer/Origin
            # Selenium driver might manage session cookies, but requests.get needs explicit headers
            response_headers = self.headers.copy()
            response_headers['Referer'] = f"{self.base_url}/video/seminar/FULL?cid=DUMMY_CID&sid=DUMMY_SID" # Need a plausible Referer
            response_headers['Origin'] = "https://openplayer.assembly.go.kr" # Subtitle API has a different origin from log
            response_headers['Sec-Fetch-Site'] = 'same-site' # from log
            
            response = requests.get(subtitle_api_call_url, headers=response_headers, timeout=15)
            response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
            
            content_type = response.headers.get('Content-Type', '').lower()
            
            # --- Check if the response is JSON (like the smiList format) ---
            if 'application/json' in content_type or response.text.strip().startswith('{'):
                try:
                    json_data = response.json()
                    smi_list = json_data.get('smiList', [])
                    
                    if smi_list:
                        plain_text_lines = [item.get('cc', '') for item in smi_list]
                        plain_text_content = "\n".join(plain_text_lines)
                        
                        subtitle_filepath = os.path.join(self.download_dir, f"{output_filename_base}.txt")
                        with open(subtitle_filepath, 'w', encoding='utf-8') as f:
                            f.write(plain_text_content)
                        logging.info(f"JSON-based subtitle extracted and saved to: {subtitle_filepath}")
                        return subtitle_filepath
                    else:
                        logging.warning(f"JSON response found for contId {cont_id}, but 'smiList' was empty or not found.")
                        return None
                except json.JSONDecodeError:
                    logging.warning(f"Response for contId {cont_id} claimed JSON but failed to decode. Treating as raw text/smi/vtt.")
                    # Fall through to raw content handling if JSON decode fails
            
            # --- Handle raw SMI/VTT content ---
            if 'text/vtt' in content_type or response.text.startswith("WEBVTT"):
                subtitle_extension = ".vtt"
            elif 'text/html' in content_type or 'application/smil' in content_type or 'text/xml' in content_type or "<smi>" in response.text.lower():
                subtitle_extension = ".smi"
            else:
                logging.warning(f"Could not determine subtitle type for contId {cont_id} from Content-Type or initial content. Defaulting to .txt")
                subtitle_extension = ".txt" # This will be the raw content
                
            subtitle_filepath = os.path.join(self.download_dir, f"{output_filename_base}{subtitle_extension}")
            
            with open(subtitle_filepath, 'wb') as f: # Use 'wb' to write raw content safely
                f.write(response.content)
            logging.info(f"Raw subtitle downloaded successfully to: {subtitle_filepath}")
            return subtitle_filepath
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error downloading subtitle for contId {cont_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred during subtitle download for contId {cont_id}: {e}", exc_info=True)
            return None

    def quit(self):
        if self.driver:
            self.driver.quit()
            logging.debug("WebDriver quit.")

if __name__ == '__main__':
    # Example usage:
    # This part should ideally be integrated into SeminarGUI later.
    DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "smb_packages", "seminars_download_selenium")
    
    extractor = None
    try:
        # User needs to ensure chromedriver is in PATH or provide driver_path
        # For example: driver_path="C:\path	o\chromedriver.exe"
        extractor = SeleniumSubtitleExtractor(download_dir=DOWNLOAD_PATH, headless=True) # Set headless=False to see browser
        
        # Example CID from previous logs
        example_cid = "94057" # "산림재난 대응체계의 패러다임 전환 국회토론회"

        cont_id = extractor.get_cont_id_from_cid(example_cid)
        if cont_id:
            print(f"Found contId: {cont_id} for cid: {example_cid}")
            subtitle_output_base = f"Subtitle_{example_cid}_{cont_id}"
            subtitle_file = extractor.download_subtitle(cont_id, subtitle_output_base)
            if subtitle_file:
                print(f"Subtitle downloaded to: {subtitle_file}")
            else:
                print("Subtitle download failed.")
        else:
            print(f"Failed to get contId for cid: {example_cid}")

    except Exception as e:
        print(f"An error occurred: {e}")
        logging.critical(f"Unhandled error in main execution: {e}", exc_info=True)
    finally:
        if extractor:
            extractor.quit()
