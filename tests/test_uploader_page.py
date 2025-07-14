from the_toob.UploaderPage import UploaderPage
from unittest.mock import MagicMock

import pytest

pytestmark = pytest.mark.page


@pytest.fixture
def mock_driver():
    """Creates a mock driver object for testing page interactions."""
    return MagicMock()


@pytest.fixture
def uploader_page(mock_driver):
    """Creates an instance of UploaderPage with a mocked driver."""
    logger = MagicMock()
    metadata = {
        "title": "My Test Title",
        "description": "My test description.",
        "tags": ["tag1", "tag2"],
    }
    return UploaderPage(mock_driver, logger, metadata)


def test_set_title_and_description(uploader_page, mocker):
    """Tests that the title and description are set correctly."""
    mock_title_field = MagicMock()
    mock_desc_field = MagicMock()
    # Correctly mock the 'until' method on the WebDriverWait class
    mocker.patch(
        "selenium.webdriver.support.ui.WebDriverWait.until",
        return_value=[mock_title_field, mock_desc_field],
    )

    uploader_page._write_in_field = MagicMock()
    uploader_page.set_title_and_description()

    uploader_page._write_in_field.assert_any_call(
        mock_title_field, "My Test Title", select_all=True
    )
    uploader_page._write_in_field.assert_any_call(
        mock_desc_field, "My test description.", select_all=True
    )


def test_set_audience(uploader_page):
    """Tests that the 'not for kids' radio button is clicked."""
    # Mock the helper method to isolate our test
    uploader_page._click_if_not_selected = MagicMock()

    uploader_page.set_audience()

    # Assert that the helper was called with the correct locator
    args, _ = uploader_page._click_if_not_selected.call_args
    locator, _ = args
    assert locator[1] == "VIDEO_MADE_FOR_KIDS_NOT_MFK"  # Check the name of the element
