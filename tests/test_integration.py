import pytest
import os
from pathlib import Path
from the_toob import Uploader

# Mark all tests in this file as 'integration' tests
pytestmark = pytest.mark.integration

# --- Test Configuration ---
# Define the paths to our test assets and the required profile
# This makes them easy to change later if needed.
ASSETS_DIR = Path(__file__).parent / "assets"
TEST_VIDEO_PATH = str(ASSETS_DIR / "test_video.mp4")
TEST_THUMBNAIL_PATH = str(ASSETS_DIR / "test_thumbnail.png")
PROFILE_PATH = os.path.abspath("profiles/firefox_profile")
COOKIE_PATH = os.path.join(PROFILE_PATH, "cookies.pkl")

pytestmark = [
    pytest.mark.integration,
]


# --- The Integration Test ---
def test_full_upload_flow(mocker):
    """
    Tests the entire upload flow from start to finish, using a real browser
    and a pre-existing logged-in profile.
    """
    # Arrange: Define the metadata for our test video
    test_metadata = {
        "title": "TheToob Integration Test Video",
        "description": "This is an automated test video uploaded by TheToob.\n\nPlease ignore.",
        "tags": ["testing", "automation", "thetoob"],
        "visibility": "PRIVATE",  # Always upload tests as private!
        "paid_promotion": True,
        "altered_content": True,
    }

    # We mock the final, irreversible step: clicking the publish button.
    mock_publish = mocker.patch(
        "the_toob.UploaderPage.UploaderPage.publish_video", return_value=None
    )

    # Act: Initialize the Uploader and run the main upload method
    uploader = Uploader(
        video_path=TEST_VIDEO_PATH,
        thumbnail_path=TEST_THUMBNAIL_PATH,
        profile_path=str(PROFILE_PATH),
        metadata=test_metadata,
        headless_mode=False,
    )
    success, video_id = uploader.upload()

    # Assert: Check that the process completed successfully
    assert success is True
    assert video_id is not None

    mock_publish.assert_called_once()

    print(
        f"\nIntegration test successful. Pretended to upload video with ID: {video_id}"
    )
