"""This module contains the main Uploader class."""

# System
from typing import DefaultDict, Optional, Tuple, Union
from collections import defaultdict
import json
import time
from pathlib import Path
import logging
import os
import platform
import subprocess

# Local
from .Constant import *
from .ToobBrowser import ToobBrowser
from .UploaderPage import UploaderPage

logging.basicConfig()


class Uploader:
    """
    A class to manage the YouTube upload process.
    It handles browser setup, login, and orchestrates the upload flow.
    """

    def __init__(
        self,
        video_path: str,
        thumbnail_path: Optional[str] = None,
        profile_path: str = str(Path.cwd() / "profiles" / "firefox_profile"),
        metadata: Optional[Union[dict, str]] = None,
        headless_mode: bool = True,
    ):
        """
        Initializes the Uploader.

        Args:
            video_path (str): The path to the video file to upload.
            metadata (Optional[Union[dict, str]]): The metadata for the video.
                Can be a dictionary or a path to a JSON file. Defaults to None.
            thumbnail_path (Optional[str]): The path to the thumbnail image. Defaults to None.
            profile_path (str): The path to the Firefox profile directory. Defaults to "./profile".

        Note:
            The metadata dictionary or JSON file should have the following structure:
            {
                "title": "Your Video Title",
                "description": "Your video description.",
                "tags": ["tag1", "tag2", "another tag"],
                "visibility": "PUBLIC" | "PRIVATE" | "UNLISTED",
                "paid_promotion": true | false,
                "altered_content": true | false
            }
        """
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path
        self.logger = logging.getLogger(__name__)
        self.metadata_dict = self._load_metadata(metadata)
        self.browser = ToobBrowser(profile_path=profile_path, headless=headless_mode)
        self.logger.setLevel(logging.DEBUG)

        self._validate_inputs()
        self.logger.debug(f"Using profile path: {profile_path}")

    @staticmethod
    def get_metadata_template() -> dict:
        """Returns a dictionary with the expected metadata structure."""
        return {
            Constant.VIDEO_TITLE: "Example Title",
            Constant.VIDEO_DESCRIPTION: "Example description.",
            Constant.VIDEO_TAGS: ["tag1", "tag2", "tag3"],
            Constant.VIDEO_VISIBILITY: f"'{Constant.PUBLIC_BUTTON}', '{Constant.PRIVATE_BUTTON}', or '{Constant.UNLISTED_BUTTON}'",
            Constant.VIDEO_PAID_PROMOTION: False,
            Constant.VIDEO_ALTERED_CONTENT: False,
        }

    def _load_metadata(
        self, metadata: Optional[Union[dict, str]]
    ) -> DefaultDict[str, str]:
        """Loads metadata from either a dictionary or a JSON file path."""
        if isinstance(metadata, str):
            self.logger.debug(f"Loading metadata from file: {metadata}")
            with open(metadata, encoding="utf-8") as f:
                return defaultdict(str, json.load(f))
        elif isinstance(metadata, dict):
            self.logger.debug("Loading metadata from dictionary.")
            return defaultdict(str, metadata)
        else:
            self.logger.debug("No metadata provided.")
            return defaultdict(str)

    def _validate_inputs(self):
        """Sets video title from filename if not provided in metadata."""
        if not self.metadata_dict[Constant.VIDEO_TITLE]:
            self.logger.warning("The video title was not found in metadata.")
            title = Path(self.video_path).stem
            self.metadata_dict[Constant.VIDEO_TITLE] = title
            self.logger.warning(f"Video title set to filename: {title}")

    def upload(self) -> Tuple[bool, Optional[str]]:
        """
        Executes the entire upload process.
        Returns a tuple of (success_status, video_id).
        """
        try:
            self._login()
            video_id = self._perform_upload()
            self._quit()
            return True, video_id
        except Exception as e:
            self.logger.error(e, exc_info=True)
            self._quit()
            raise

    def _login(self):
        """Navigates to YouTube and ensures the session is authenticated."""
        self.browser.driver.get(Constant.YOUTUBE_URL)
        time.sleep(Constant.USER_WAITING_TIME)

        if self.browser.has_cookies():
            self.logger.debug("Loading cookies...")
            self.browser.load_cookies()
            self.browser.driver.refresh()
            self.logger.debug("Loaded cookies and refreshed page.")
        else:
            self.logger.info(
                "Cookies not found. If this is your first run, and you have already logged in to YouTube, you may disregard this message."
            )
            time.sleep(Constant.USER_WAITING_TIME)
            self.logger.debug("Saving cookies...")
            self.browser.save_cookies()
            self.logger.debug("Saved cookies.")
        time.sleep(Constant.USER_WAITING_TIME)

    def _perform_upload(self) -> Optional[str]:
        """Orchestrates the upload by using the UploaderPage object."""
        self.browser.driver.get(Constant.YOUTUBE_UPLOAD_URL)
        page = UploaderPage(self.browser.driver, self.logger, self.metadata_dict)

        # Details Page
        time.sleep(Constant.USER_WAITING_TIME)
        page.attach_video(self.video_path)
        time.sleep(Constant.USER_WAITING_TIME)
        page.set_title_and_description()

        if self.thumbnail_path:
            time.sleep(Constant.USER_WAITING_TIME)
            page.set_thumbnail(self.thumbnail_path)

        time.sleep(Constant.USER_WAITING_TIME)
        page.set_audience()
        time.sleep(Constant.USER_WAITING_TIME)
        page.disclose_advanced_options()
        time.sleep(Constant.USER_WAITING_TIME)
        page.set_paid_promotion()
        time.sleep(Constant.USER_WAITING_TIME)
        page.set_altered_content()
        time.sleep(Constant.USER_WAITING_TIME)
        page.set_tags()
        time.sleep(Constant.USER_WAITING_TIME)

        # Navigation and Finalization
        page.navigate_to_visibility_page()
        page.set_visibility()

        video_id = page.get_video_id()

        page.wait_for_upload_to_complete()
        page.publish_video()

        self.logger.debug(f"Successfully published video with ID: {video_id}")
        time.sleep(Constant.USER_WAITING_TIME * 5)

        return video_id

    def _quit(self):
        """Closes the browser and forcefully kills any lingering processes."""
        self.logger.debug("Attempting to quit browser and all related processes...")

        if not self.browser or not self.browser.driver:
            self.logger.debug("Browser not found, nothing to quit.")
            return

        try:
            # Get the process IDs before trying to quit
            browser_pid = self.browser.driver.service.process.pid

            # Attempt a graceful shutdown first
            self.browser.driver.quit()

            # On Windows, os.kill with SIGKILL is not available.
            # We use the 'taskkill' command instead.
            if platform.system() == "Windows":
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/PID", str(browser_pid)],
                        check=True,
                        capture_output=True,
                    )
                    self.logger.debug(
                        f"Force-killed lingering geckodriver process {browser_pid} on Windows."
                    )
                except subprocess.CalledProcessError as e:
                    # This error often means the process was already gone, which is fine.
                    if "not found" not in e.stderr.decode(errors="ignore").lower():
                        self.logger.error(
                            f"Failed to kill process {browser_pid} on Windows: {e.stderr.decode(errors='ignore')}"
                        )

            # For macOS and Linux, we use the original SIGKILL method
            else:
                from signal import SIGKILL

                try:
                    os.kill(browser_pid, SIGKILL)
                    self.logger.debug(
                        f"Force-killed lingering geckodriver process {browser_pid}."
                    )
                except ProcessLookupError:
                    # This is expected if the process quit gracefully
                    pass

        except Exception as e:
            self.logger.error(
                f"An error occurred during quit: {e}. Processes may be orphaned."
            )
