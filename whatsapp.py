import os
import time
import logging
import traceback
import hashlib
from typing import Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver(headless: bool = False) -> webdriver.Chrome:
	try:
		options = webdriver.ChromeOptions()
		# persistent profile to avoid re-scanning QR
		profile_dir = os.path.abspath(os.path.join(os.getcwd(), "chrome_profile"))
		options.add_argument(f"--user-data-dir={profile_dir}")
		# avoid flags that can crash on Windows
		options.add_argument("--disable-dev-shm-usage")
		options.add_experimental_option("excludeSwitches", ["enable-logging"])
		if headless:
			options.add_argument("--headless=new")

		# use webdriver-manager to obtain a matching chromedriver
		driver_path = ChromeDriverManager().install()
		service = Service(driver_path)
		try:
			driver = webdriver.Chrome(service=service, options=options)
			driver.set_window_size(1200, 900)
			return driver
		except Exception:
			logging.exception("Primary Chrome launch failed, retrying without profile")
			# fallback: retry without user-data-dir (avoids profile lock)
			options = webdriver.ChromeOptions()
			if headless:
				options.add_argument("--headless=new")
			options.add_argument("--disable-dev-shm-usage")
			options.add_experimental_option("excludeSwitches", ["enable-logging"])
			driver = webdriver.Chrome(service=service, options=options)
			driver.set_window_size(1200, 900)
			return driver
	except Exception as e:
		logging.exception("get_driver error: %s", traceback.format_exc())
		raise


def load_whatsapp(driver: webdriver.Chrome, timeout: int = 60) -> bool:
	try:
		driver.get("https://web.whatsapp.com")
		wait = WebDriverWait(driver, timeout)
		# wait until chat list or QR canvas appears (user scans QR)
		wait.until(lambda d: "WhatsApp" in d.title or d.find_elements(By.XPATH, "//canvas"))
		# then wait until the chat list is present
		wait.until(EC.presence_of_element_located((By.XPATH, '//div[@aria-label="Chat list"]')))
		return True
	except TimeoutException:
		logging.warning("Timed out waiting for WhatsApp Web to load")
		return False
	except Exception:
		logging.exception("load_whatsapp error: %s", traceback.format_exc())
		return False


def open_chat(driver: webdriver.Chrome, contact_name: str) -> bool:
	try:
		# try to click the contact directly
		xpath = f"//span[@title='{contact_name}']"
		try:
			el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
			el.click()
			time.sleep(0.5)
			return True
		except Exception:
			# fallback to search box
			search_xpath = "//div[@contenteditable='true' and @data-tab='3']"
			sb = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, search_xpath)))
			sb.click()
			sb.clear()
			sb.send_keys(contact_name)
			time.sleep(1)
			el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
			el.click()
			time.sleep(0.5)
			return True
	except Exception:
		logging.exception("open_chat error: %s", traceback.format_exc())
		return False


def _find_last_message_element(driver):
	selectors = [
		"//div[contains(@class,'message-in') or contains(@class,'message-out')][last()]",
		"(//div[contains(@data-testid,'msg-container')])[last()]",
	]
	for sel in selectors:
		try:
			el = driver.find_element(By.XPATH, sel)
			return el
		except Exception:
			continue
	try:
		elems = driver.find_elements(By.XPATH, "//span[contains(@class,'selectable-text')]")
		if elems:
			return elems[-1]
	except Exception:
		return None
	return None


def get_last_message(driver: webdriver.Chrome) -> Tuple[str, bool, str]:
	try:
		time.sleep(0.5)
		el = _find_last_message_element(driver)
		if el is None:
			return ("", False, "")

		text = el.text.strip()
		data_attr = None
		try:
			data_attr = el.get_attribute("data-pre-plain-text") or el.get_attribute("data-id")
		except Exception:
			data_attr = None

		raw_id = (data_attr or text)[:500]
		message_id = hashlib.sha256(raw_id.encode("utf-8")).hexdigest()

		cls = el.get_attribute("class") or ""
		is_from_me = "message-out" in cls or "_1Ww5q" in cls

		return (message_id, is_from_me, text)
	except Exception:
		logging.exception("get_last_message error: %s", traceback.format_exc())
		return ("", False, "")


def send_message(driver: webdriver.Chrome, message: str) -> bool:
	try:
		possible = [
			"//div[@contenteditable='true' and @data-tab='10']",
			"//div[@contenteditable='true' and @data-tab='6']",
			"//div[@role='textbox' and @contenteditable='true']",
		]
		inp = None
		for p in possible:
			try:
				inp = driver.find_element(By.XPATH, p)
				if inp:
					break
			except Exception:
				continue

		if inp is None:
			logging.warning("Could not find message input box")
			return False

		inp.click()
		time.sleep(0.2)
		inp.send_keys(message)
		time.sleep(0.2)
		inp.send_keys(Keys.ENTER)
		return True
	except Exception:
		logging.exception("send_message error: %s", traceback.format_exc())
		return False

