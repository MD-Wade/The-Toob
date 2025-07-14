import pickle
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


class ToobBrowser:
    """
    A custom browser class to handle Firefox startup and cookie management.
    """

    def __init__(self, profile_path: str, headless: bool = True):
        self.cookie_path = Path(profile_path) / "cookies.pkl"

        if not os.path.exists(profile_path):
            print(
                f"WARNING: The specified profile path does not exist: {profile_path}\n"
                "This is a critical error as you need to create a Firefox profile from within Firefox and then sign in to YouTube, both manually, before running this script.\n"
                "This script cannot create a profile for you, and you cannot sign in to YouTube from it.\n"
                "Please create a profile manually and sign in to YouTube before running this script. Refer to the README for more details.\n"
            )
            raise FileNotFoundError(
                f"WARNING: The existing profile path does not exist: {profile_path}"
            )

        # Configure Firefox to use a specific profile
        options = Options()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.add_argument("-profile")
        options.add_argument(profile_path)

        # The driver is the core Selenium browser object we'll use for everything
        self.driver = webdriver.Firefox(options=options)

    def has_cookies(self) -> bool:
        """Checks if a cookie file exists."""
        return self.cookie_path.exists()

    def load_cookies(self):
        """Loads cookies from the pickle file and adds them to the browser."""
        with open(self.cookie_path, "rb") as f:
            cookies = pickle.load(f)
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    def save_cookies(self):
        """Saves the current session cookies to the pickle file."""
        with open(self.cookie_path, "wb") as f:
            pickle.dump(self.driver.get_cookies(), f)
