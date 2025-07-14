# TheToob

[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg?style=flat)](https://github.com/MD-Wade/The-Toob/pulls) _"Hey bubba, what's on the Toob?"_

`TheToob` is a Python package for uploading videos to YouTube using Selenium. It's a heavily modified and modernized fork of the original [youtube_uploader_selenium by linouk23](https://github.com/linouk23/youtube_uploader_selenium), refactored for robustness, maintainability, and modern features.

Like the original, this tool automates the browser to upload videos, bypassing the daily quota limits of the official YouTube Data API.

---
## ⭐ Key Features & Improvements

* **Modern Architecture:** Fully refactored into an object-oriented structure (`Uploader`, `UploaderPage`, `ToobBrowser`) for better readability and maintenance.
* **Headless Operation:** Run the uploader in the background without a visible browser window, perfect for servers and automation scripts.
* **Robust Error Handling:** Automatically saves a crash report with a screenshot and HTML dump if an operation fails, making debugging significantly easier.
* **Enhanced Stability:** Uses explicit waits and more reliable element locators to prevent common race conditions and timing errors.
* **Updated YouTube Options:** Supports newer metadata fields including:
    * Video `visibility` (`Public`, `Private`, `Unlisted`)
    * `paid_promotion` disclosures
    * `altered_content` disclosures for AI-generated or modified media
* **Simplified Dependencies:** Uses the core `selenium` library directly, removing the need for extra wrappers.

---
## ⚙️ Installation

```bash
pip3 install --upgrade the-toob
```

---
## 🚀 Usage

The package is designed to be used as a library within your Python projects.

### 🤓 First-Time Setup: Creating a Logged-in Profile

Due to Google's security policies, you cannot log in for the first time within the automated browser. You must first create a dedicated Firefox profile and log in manually using a normal browser window.

**This is a one-time setup.**

1.  **Open Firefox**: Launch your regular Mozilla Firefox browser.
2.  **Go to Profiles Page**: Type `about:profiles` into the address bar and press Enter.
3.  **Create a New Profile**: Click the "Create a New Profile" button and follow the wizard.
4.  **Set the Profile Path**: When prompted, click "Choose Folder...". Navigate to your project's folder and select the `profiles/firefox_profile` directory. This is critical for linking the profile to `TheToob`.
    
5.  **Launch and Log In**: Find your new profile in the list and click "Launch profile in new browser". In the new Firefox window that opens, navigate to YouTube and log in to your Google account as you normally would.
6.  **Close the Profile**: Once you are successfully logged in, you can close that Firefox window.
7.  **Run `TheToob` for the First Time**: Now, run the `thetoob` command from your terminal. The script will open the browser you just logged into, pause with a message about saving cookies, and create the `cookies.pkl` file.

After this initial run, all future runs can be fully automated and headless.

### Standard (Headless) Upload

Once authenticated, you can run the uploader in headless mode.

```python
from youtube_uploader_selenium import Uploader
import logging

logging.basicConfig(level=logging.INFO)

# Define your video metadata
# This can also be loaded from a JSON file (see below)
video_metadata = {
    "title": "Mr. Game & Watch: The Secrets of Nair 1, 2, and 3",
    "description": "Sure, the fourth one pops them up, but Ftilt is cool, too...",
    "tags": ["carried"],
    "visibility": "PUBLIC",
    "paid_promotion": False,
    "altered_content": False
}

uploader = Uploader(
    video_path='path/to/your/video.mp4',
    thumbnail_path='path/to/your/thumbnail.jpg', # Optional
    metadata=video_metadata,
    profile_path='path/to/your/firefox_profile',
    headless=True # Headless is now possible
)
was_uploaded, video_id = uploader.upload()
```

---
## 📝 Metadata Guide

You can provide metadata as a dictionary (as shown above) or as a path to a JSON file.

**Example `metadata.json` file:**

```json
video_metadata = {
    "title": "Mr. Game & Watch: The Secrets of Nair 1, 2, and 3",
    "description": "Sure, the fourth one pops them up, but Ftilt is cool, too...",
    "tags": ["carried"],
    "visibility": "PUBLIC",
    "paid_promotion": False,
    "altered_content": False
}
```

### Metadata Fields

* `title` (str): The video title. If not provided, it defaults to the video's filename.
* `description` (str): The video description. `\n` characters are respected.
* `tags` (List[str]): A list of tags for the video.
* `visibility` (str): Sets the video's visibility. Must be one of `PUBLIC`, `PRIVATE`, or `UNLISTED`. Defaults to `PRIVATE` if not specified.
* `paid_promotion` (bool): Set to `True` if the video contains a paid promotion.
* `altered_content` (bool): Set to `True` if the video contains significantly altered or synthetic content that looks realistic.
---

## 💻 Command-Line Usage

Once installed, `TheToob` can be used directly from your terminal.

**Basic Usage:**
```bash
thetoob --video "path/to/my/video.mp4"

# Full Featured Usage:
```bash
thetoob --video "video.mp4" --meta "metadata.json" --thumbnail "thumb.jpg" --headless
```

# Alternative Usage:
You can also run it as a Python module.
```bash
python3 -m the_toob --video "video.mp4"
```

# Available Arguments:
    --video: (Required) The path to the video file you want to upload.

    --meta: (Optional) Path to a .json file containing the video's metadata.

    --thumbnail: (Optional) Path to a custom thumbnail image for the video.

    --profile: (Optional) The directory to use for the Firefox profile and cookies. Defaults to ./firefox_profile.

    --headless: (Optional) A flag to run the browser in headless mode (no visible UI).

---
## 📦 Dependencies & Driver Management

* [**Mozilla Firefox**](https://www.mozilla.org/en-US/firefox/new/): A modern, up-to-date version is recommended.
* [**selenium**](https://pypi.org/project/selenium/): The core automation library.

### A Note on GeckoDriver

Modern versions of Selenium (4.6.0 and newer) include **Selenium Manager**, a tool that automatically downloads and manages the necessary web driver for you.

For most users, this means **you do not need to manually download `geckodriver`**. The first time you run `TheToob`, Selenium will download the correct driver and cache it for future use.

**Manual Override:** If you are behind a strict corporate firewall or run into any driver-related issues, you can still fall back to the manual method. Download the latest `geckodriver` from its [official releases page](https://github.com/mozilla/geckodriver/releases) and ensure the executable is in your system's PATH.

---
## ❤️ Original Project & Credit

`TheToob` is built upon the foundational work of **linouk23**. A huge thank you for creating the original tool and sharing it with the community.

* **Original Author:** [linouk23](https://github.com/linouk23)
* **Original Repository:** [youtube_uploader_selenium](https://github.com/linouk23/youtube_uploader_selenium)

## 🤝 Contributing

This project is maintained on a best-effort basis. While I may not be adding many new features myself, I welcome contributions from the community to help TheToob grow. Feel free to open a pull request!

---
## 📄 License

This project is licensed under the MIT License. Please see the [LICENSE](./LICENSE) file for full details.