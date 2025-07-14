import json
from pathlib import Path
from the_toob import Uploader

# Mark all tests in this file as being for the 'uploader' component
import pytest

pytestmark = pytest.mark.uploader


def test_uploader_initialization(mocker):
    """Tests that the Uploader class initializes correctly."""
    # Capture the mocked class
    mock_browser_class = mocker.patch("the_toob.Uploader.ToobBrowser")

    video_path = "video.mp4"
    profile_path = "/fake/profile"
    metadata = {"title": "Test Title"}

    uploader = Uploader(
        video_path=video_path,
        profile_path=profile_path,
        metadata=metadata,
        headless_mode=False,
    )

    assert uploader.video_path == video_path
    assert uploader.metadata_dict["title"] == "Test Title"
    # Assert that the mocked class was instantiated with the correct parameters
    mock_browser_class.assert_called_with(profile_path=profile_path, headless=False)


def test_title_fallback_if_metadata_is_missing(mocker):
    """Tests that the title defaults to the filename if no metadata is provided."""
    mocker.patch("the_toob.Uploader.ToobBrowser")

    video_path = "path/to/my_awesome_video.mp4"
    uploader = Uploader(video_path=video_path, metadata=None)

    assert uploader.metadata_dict["title"] == "my_awesome_video"


def test_metadata_loading_from_file(mocker, tmp_path):
    """Tests that metadata is correctly loaded from a JSON file."""
    mocker.patch("the_toob.Uploader.ToobBrowser")

    # Create a temporary directory and a fake metadata file
    metadata_dir = tmp_path / "metadata"
    metadata_dir.mkdir()
    metadata_file = metadata_dir / "meta.json"
    metadata_content = {"title": "Title From File", "description": "Desc from file"}
    metadata_file.write_text(json.dumps(metadata_content))

    uploader = Uploader(video_path="video.mp4", metadata=str(metadata_file))

    assert uploader.metadata_dict["title"] == "Title From File"
    assert uploader.metadata_dict["description"] == "Desc from file"


def test_upload_orchestration(mocker):
    """Tests that the main upload() method calls login and perform_upload."""
    mocker.patch("the_toob.Uploader.ToobBrowser")
    # Correct the patch targets to point to the methods on the CLASS
    mock_login = mocker.patch("the_toob.Uploader.Uploader._login")
    mock_perform = mocker.patch(
        "the_toob.Uploader.Uploader._perform_upload",
        return_value="fake_video_id",
    )
    mock_quit = mocker.patch("the_toob.Uploader.Uploader._quit")

    uploader = Uploader(video_path="video.mp4")
    success, video_id = uploader.upload()

    mock_login.assert_called_once()
    mock_perform.assert_called_once()
    mock_quit.assert_called_once()
    assert success is True
    assert video_id == "fake_video_id"
