class Constant:
    """A class for storing constants for the Uploader."""

    # --- URLs ---
    YOUTUBE_URL = "https://www.youtube.com"
    YOUTUBE_UPLOAD_URL = "https://www.youtube.com/upload"

    # --- TIMEOUTS ---
    USER_WAITING_TIME = 1
    ACTION_WAIT_TIME = 0.5

    # --- METADATA KEYS ---
    VIDEO_TITLE = "title"
    VIDEO_DESCRIPTION = "description"
    VIDEO_TAGS = "tags"
    VIDEO_VISIBILITY = "visibility"
    VIDEO_PAID_PROMOTION = "paid_promotion"
    VIDEO_ALTERED_CONTENT = "altered_content"

    # --- ELEMENT SELECTORS (LOCATORS) ---

    # Common
    TEXTBOX_ID = "textbox"
    NEXT_BUTTON_ID = "next-button"
    DONE_BUTTON_ID = "done-button"
    HREF_ATTRIBUTE = "href"
    ERROR_CONTAINER_XPATH = '//*[@id="error-message"]'
    UPLOADING_STATUS_XPATH = "//span[contains(@class, 'progress-label')]"

    # Video & Thumbnail Inputs
    INPUT_FILE_VIDEO_XPATH = "//input[@type='file']"
    INPUT_FILE_THUMBNAIL_ID = "file-loader"
    THUMBNAIL_PLACEHOLDER_ID = "select-button"
    VIDEO_URL_ELEMENT_XPATH = "//a[@class='style-scope ytcp-video-info']"

    # Audience Section
    NOT_MADE_FOR_KIDS_NAME = "VIDEO_MADE_FOR_KIDS_NOT_MFK"

    # Advanced Options Section
    ADVANCED_BUTTON_ID = "toggle-button"
    PAID_PROMOTION_XPATH = (
        "//*[@id='checkbox' and contains(@aria-label, 'paid promotion')]"
    )
    ALTERED_CONTENT_YES_XPATH = "(//tp-yt-paper-radio-button)[5]"
    ALTERED_CONTENT_NO_XPATH = "(//tp-yt-paper-radio-button)[6]"
    TAGS_CONTAINER_ID = "tags-container"
    TAGS_INPUT_ID = "text-input"

    # Visibility Section
    PUBLIC_BUTTON_NAME = "PUBLIC"
    PRIVATE_BUTTON_NAME = "PRIVATE"
    UNLISTED_BUTTON_NAME = "UNLISTED"
