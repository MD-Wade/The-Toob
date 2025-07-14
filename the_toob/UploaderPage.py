from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from pathlib import Path
import re
import platform
import time
import datetime

from .Constant import *


class UploaderPage:
    """
    This class represents the YouTube upload page and contains methods
    for all interactions with the page elements.
    """

    def __init__(self, driver, logger, metadata: dict):
        self.driver = driver
        self.logger = logger
        self.metadata = metadata
        self.wait = WebDriverWait(self.driver, 20)

    # --- CORE HELPER METHODS ---

    def _save_crash_report(self, operation_name: str):
        """Saves a screenshot and HTML dump into a unique crash directory."""
        base_crash_dir = Path("crash")
        base_crash_dir.mkdir(exist_ok=True)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        crash_dir_name = f"{operation_name}_{timestamp}"
        crash_event_path = base_crash_dir / crash_dir_name
        crash_event_path.mkdir()

        try:
            # Save screenshot inside the new directory
            screenshot_path = crash_event_path / "crash_screenshot.png"
            self.driver.save_screenshot(str(screenshot_path))

            # Save HTML source inside the new directory
            html_path = crash_event_path / "crash_page.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)

            self.logger.error(f"Crash report saved to: {crash_event_path}")
        except Exception as e:
            self.logger.error(f"Failed to save crash report: {e}")

    def _find_element(
        self, by, value, condition=EC.presence_of_element_located, timeout: int = None
    ) -> WebElement:
        """
        A central method to find elements with a built-in try/except block
        that generates a crash report on failure. Can accept a custom timeout.
        """
        # Use the custom timeout if provided, otherwise use the default self.wait
        wait = self.wait if timeout is None else WebDriverWait(self.driver, timeout)

        try:
            return wait.until(condition((by, value)))
        except TimeoutException as e:
            operation_name = (
                f"find_element_timeout_{value.replace('//', '').replace('/', '_')[:50]}"
            )
            self.logger.error(f"TimeoutException while trying to find element: {value}")
            self._save_crash_report(operation_name)
            raise e

    def _click_if_not_selected(self, locator: tuple, log_message: str):
        """
        A central method for radio buttons and checkboxes that first checks
        if the element is already selected before clicking.
        """
        element = self._find_element(locator[0], locator[1])

        if element.get_attribute("checked") is not None:
            self.logger.debug(f"'{log_message}' is already selected. No action needed.")
            return

        self.driver.execute_script("arguments[0].click();", element)
        self.logger.debug(f"Successfully selected '{log_message}'")

    # --- PAGE INTERACTION METHODS ---

    def attach_video(self, video_path: str):
        """Finds the file input and sends the video path."""
        file_input = self._find_element(By.XPATH, Constant.INPUT_FILE_VIDEO)
        absolute_video_path = str(Path.cwd() / video_path)
        file_input.send_keys(absolute_video_path)
        self.logger.debug(f"Attached video: {video_path}")

    def wait_for_upload_to_complete(self):
        """
        Waits for the initial video upload to finish by monitoring the progress text.
        """
        self.logger.debug("Waiting for the video to finish uploading...")
        short_timeout = 10

        while True:
            try:
                # Find the element containing the progress text
                progress_element = self._find_element(
                    By.XPATH, Constant.UPLOADING_STATUS_CONTAINER, timeout=short_timeout
                )

                # Get the text (e.g., "Uploading 32% ...")
                progress_text = progress_element.text

                # Use a regular expression to find the percentage
                match = re.search(r"(\d+)%", progress_text)

                if match:
                    # If we found a percentage, log it
                    progress_value = match.group(1)
                    self.logger.debug(f"Upload progress: {progress_value}%")
                else:
                    # If no percentage, log the whole status (e.g., "Processing HD version")
                    self.logger.debug(f"Upload status: {progress_text}")

                # If the text indicates checks are complete, we can exit
                progress_text_compare = progress_text.lower()
                if (
                    "upload complete" in progress_text_compare
                    or "checks complete" in progress_text_compare
                ):
                    self.logger.debug("Upload and processing finished.")
                    break

                time.sleep(Constant.USER_WAITING_TIME)

            except TimeoutException:
                # This exception means the progress element is no longer visible.
                # More often than not, this is actually an issue.
                # We can try and continue anyway, but we should log it.
                self.logger.warning(
                    "Upload progress element not found. This might indicate an issue."
                )
                break  # Exit the loop

    def set_title_and_description(self):
        """Waits for the textboxes to appear and sets the title and description."""
        try:
            textboxes = self.wait.until(
                EC.presence_of_all_elements_located((By.ID, Constant.TEXTBOX_ID))
            )
            if len(textboxes) < 2:
                raise RuntimeError("Could not find title and description textboxes.")

            title_field, description_field = textboxes[0], textboxes[1]
            self._write_in_field(
                title_field, self.metadata[Constant.VIDEO_TITLE], select_all=True
            )
            self.logger.debug(
                f'The video title was set to "{self.metadata[Constant.VIDEO_TITLE]}"'
            )

            description = self.metadata[Constant.VIDEO_DESCRIPTION].replace(
                "\n", Keys.ENTER
            )
            if description:
                self._write_in_field(description_field, description, select_all=True)
                self.logger.debug("Description filled.")
        except Exception as e:
            self._save_crash_report("set_title_and_description_error")
            raise e

    def set_thumbnail(self, thumbnail_path: str):
        """
        Makes the thumbnail input visible and attaches the thumbnail.
        """
        self.logger.debug("Setting thumbnail...")

        # 1. Wait for the visible placeholder button to be ready.
        #    We don't need to click it, just ensure it's loaded.
        self._find_element(By.ID, Constant.THUMBNAIL_PLACEHOLDER_ID)

        # 2. Use JavaScript to make the hidden file input element visible.
        thumbnail_input_id = Constant.INPUT_FILE_THUMBNAIL_ID
        self.driver.execute_script(
            f"document.getElementById('{thumbnail_input_id}').style.display = 'block';"
        )

        # 3. Find the now-visible input element and send the file path.
        thumbnail_input = self._find_element(By.ID, thumbnail_input_id)
        absolute_thumbnail_path = str(Path.cwd() / thumbnail_path)
        thumbnail_input.send_keys(absolute_thumbnail_path)

        self.logger.debug(f"Attached thumbnail: {thumbnail_path}")

    def set_audience(self):
        """Selects 'No, it's not made for kids' if not already selected."""
        locator = (By.NAME, Constant.NOT_MADE_FOR_KIDS_LABEL)
        self._click_if_not_selected(locator, "Not made for kids")

    def disclose_advanced_options(self):
        """Clicks the 'Show More' button to reveal advanced options."""
        show_more_button = self._find_element(
            By.ID, Constant.ADVANCED_BUTTON_ID, condition=EC.element_to_be_clickable
        )
        self.driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
        show_more_button.click()
        self.logger.debug('Clicked "Show More"')

    def set_paid_promotion(self):
        """Checks the 'Paid promotion' box if specified and not already checked."""
        if self.metadata.get(Constant.VIDEO_PAID_PROMOTION):
            locator = (By.ID, Constant.PAID_PROMOTION_CHECKBOX)
            self._click_if_not_selected(locator, "Paid promotion")

    def set_altered_content(self):
        """Selects the 'Altered content' option if specified."""
        is_altered = self.metadata.get(Constant.VIDEO_ALTERED_CONTENT)
        if is_altered is None:
            return

        xpath = (
            Constant.ALTERED_CONTENT_YES_RADIO
            if is_altered
            else Constant.ALTERED_CONTENT_NO_RADIO
        )
        log_message = f'Altered content: {"Yes" if is_altered else "No"}'
        self._click_if_not_selected((By.XPATH, xpath), log_message)

    def set_tags(self):
        """Adds tags to the video."""
        tags = self.metadata.get(Constant.VIDEO_TAGS)
        if tags:
            tags_container = self._find_element(By.ID, Constant.TAGS_CONTAINER_ID)
            tags_input = tags_container.find_element(By.ID, Constant.TAGS_INPUT)
            self._write_in_field(tags_input, ",".join(tags))
            self.logger.debug(f"Set tags to: {tags}")

    def navigate_to_visibility_page(self):
        """Clicks the 'Next' button three times."""
        for i in range(3):
            next_button = self._find_element(
                By.ID, Constant.NEXT_BUTTON, condition=EC.element_to_be_clickable
            )
            next_button.click()
            self.logger.debug(f'Clicked "Next" button {i + 1}')
            time.sleep(0.5)  # Short wait to allow page transition

    def set_visibility(self):
        """Sets the video visibility if not already selected."""
        visibility_name = self.metadata.get(
            Constant.VIDEO_VISIBILITY, Constant.PRIVATE_BUTTON
        )
        visibility_name = visibility_name.upper()
        xpath = f"//tp-yt-paper-radio-button[@name='{visibility_name}']"
        self._click_if_not_selected((By.XPATH, xpath), f"Visibility: {visibility_name}")

    def get_video_id(self) -> str | None:
        """Retrieves the video ID from the upload page."""
        video_url_element = self._find_element(By.XPATH, Constant.VIDEO_URL_ELEMENT)
        if video_url_element:
            return video_url_element.get_attribute("href").split("/")[-1]
        return None

    def publish_video(self):
        """Waits for processing and clicks the final publish button."""
        done_button = self._find_element(
            By.ID,
            Constant.DONE_BUTTON,
            condition=EC.element_to_be_clickable,
            timeout=7200,
        )

        try:
            error_dialog = self.driver.find_element(By.XPATH, Constant.ERROR_CONTAINER)
            if error_dialog.is_displayed():
                raise RuntimeError(f"Upload failed with error: {error_dialog.text}")
        except:
            pass

        done_button.click()
        self.logger.debug("Publish button clicked")

    def _clear_field(self, field: WebElement):
        """Helper to clear a text field."""
        field.click()
        time.sleep(Constant.ACTION_WAIT_TIME)
        if platform.system() == "Darwin":
            field.send_keys(Keys.COMMAND + "a")
        else:
            field.send_keys(Keys.CONTROL + "a")
        time.sleep(Constant.ACTION_WAIT_TIME)
        field.send_keys(Keys.BACKSPACE)

    def _write_in_field(self, field: WebElement, text: str, select_all=False):
        """Helper to write text into a field."""
        if select_all:
            self._clear_field(field)
        else:
            field.click()
            time.sleep(Constant.ACTION_WAIT_TIME)
        field.send_keys(text)
