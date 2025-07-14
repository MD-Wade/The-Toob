import argparse
from html import parser
import json
from .Uploader import Uploader  # Note the dot for relative import
import logging


def main():
    """The main function for the command-line interface."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="TheToob: A goofy-but-powerful YouTube uploader."
    )

    parser.add_argument("--video", required=True, help="Path to the video file.")
    parser.add_argument("--meta", help="Path to the JSON metadata file.")
    parser.add_argument("--thumbnail", help="Path to the thumbnail image.")
    parser.add_argument(
        "--profile",
        default="./profiles/firefox_profile",
        help="Path to the Firefox profile directory.",
    )
    parser.add_argument(
        "--headless", action="store_true", help="Run Firefox in headless mode."
    )

    args = parser.parse_args()

    metadata = None
    if args.meta:
        try:
            with open(args.meta, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except FileNotFoundError:
            logging.error(f"Metadata file not found: {args.meta}")
            return
        except json.JSONDecodeError:
            logging.error(f"Error decoding JSON from metadata file: {args.meta}")
            return

    uploader = Uploader(
        video_path=args.video,
        thumbnail_path=args.thumbnail,
        profile_path=args.profile,
        metadata=metadata,
        headless_mode=args.headless,
    )

    was_uploaded, video_id = uploader.upload()

    if was_uploaded:
        logging.info(
            f"'{args.video}' was successfully uploaded with video ID: {video_id}"
        )
    else:
        logging.error(f"Failed to upload '{args.video}'")


if __name__ == "__main__":
    main()
