import pickle
from pathlib import Path
from the_toob.ToobBrowser import ToobBrowser

import pytest

pytestmark = pytest.mark.browser


def test_toob_browser_initialization(mocker):
    """Tests that ToobBrowser initializes the Firefox driver with correct options."""
    mock_webdriver = mocker.patch("the_toob.ToobBrowser.webdriver.Firefox")
    # We mock the class from the module where it's used
    mock_options_class = mocker.patch("the_toob.ToobBrowser.Options")
    # This mock_options object will be the INSTANCE returned by Options()
    mock_options_instance = mock_options_class.return_value

    profile_path = "profiles/firefox_profile"
    browser = ToobBrowser(profile_path=profile_path, headless=True)

    # Assert calls on the instance, not the class
    mock_options_instance.add_argument.assert_any_call("--headless")
    mock_options_instance.add_argument.assert_any_call("-profile")
    mock_options_instance.add_argument.assert_any_call(profile_path)
    # Assert that the driver was instantiated with the correct options instance
    mock_webdriver.assert_called_once_with(options=mock_options_instance)


def test_has_cookies(mocker, tmp_path):
    """Tests the has_cookies method."""
    mock_webdriver = mocker.patch("the_toob.ToobBrowser.webdriver.Firefox")

    # Create a temporary profile directory
    profile_dir = tmp_path / "profile"
    profile_dir.mkdir()

    browser = ToobBrowser(profile_path=str(profile_dir))

    # At first, no cookie file exists
    assert browser.has_cookies() is False

    # Create a fake cookie file
    (profile_dir / "cookies.pkl").touch()

    assert browser.has_cookies() is True


def test_save_cookies(mocker, tmp_path):
    """Tests that save_cookies pickles the current browser cookies."""
    mock_webdriver = mocker.patch("the_toob.ToobBrowser.webdriver.Firefox")
    mock_pickle_dump = mocker.patch("the_toob.ToobBrowser.pickle.dump")

    profile_dir = tmp_path / "profile"
    profile_dir.mkdir()

    browser = ToobBrowser(profile_path=str(profile_dir))

    fake_cookies = [{"name": "cookie1", "value": "value1"}]
    browser.driver.get_cookies.return_value = fake_cookies

    browser.save_cookies()

    # Assert that pickle.dump was called with the correct cookies and file path
    # We need to check the call arguments
    args, _ = mock_pickle_dump.call_args
    assert args[0] == fake_cookies
    assert args[1].name == str(profile_dir / "cookies.pkl")
