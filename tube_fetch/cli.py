"""Command line interface for TubeFetch."""

from __future__ import annotations

import argparse
import logging
import pathlib
import sys
from typing import Any, Dict, Optional

from .core import VideoDownloader, extract_video_info

LOGGER = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download or inspect YouTube videos using yt-dlp",
    )
    parser.add_argument("url", help="The YouTube video URL to process")
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        help="Directory to store downloaded files (default: current directory)",
    )
    parser.add_argument(
        "--audio-only",
        action="store_true",
        help="Download only the audio stream",
    )
    parser.add_argument(
        "--format",
        help="yt-dlp format selector expression to use",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Only show metadata without downloading",
    )
    parser.add_argument(
        "--proxy",
        help="Proxy URL to use when contacting YouTube",
    )
    parser.add_argument(
        "--extra-option",
        action="append",
        metavar="KEY=VALUE",
        help="Additional yt-dlp options to merge into the configuration",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit metadata as JSON when using --info",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging output",
    )
    return parser


def _parse_extra_options(pairs: Optional[list[str]]) -> Dict[str, Any]:
    if not pairs:
        return {}

    options: Dict[str, Any] = {}
    for pair in pairs:
        if "=" not in pair:
            raise argparse.ArgumentTypeError(
                f"Invalid --extra-option '{pair}'. Expected KEY=VALUE format."
            )
        key, value = pair.split("=", 1)
        options[key] = value
    return options


def main(argv: Optional[list[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

    try:
        extra_options = _parse_extra_options(args.extra_option)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
        return 2  # pragma: no cover - parser.error exits

    if args.info:
        info = extract_video_info(args.url, proxy=args.proxy)
        if args.json:
            print(info.to_json())
        else:
            print(f"Title: {info.title}")
            if info.uploader:
                print(f"Uploader: {info.uploader}")
            if info.duration is not None:
                print(f"Duration: {info.duration} seconds")
            if info.view_count is not None:
                print(f"Views: {info.view_count}")
            print(f"URL: {info.webpage_url}")
        return 0

    downloader = VideoDownloader(output_dir=args.output, proxy=args.proxy)

    try:
        downloaded_path = downloader.download(
            args.url,
            audio_only=args.audio_only,
            format=args.format,
            extra_options=extra_options,
        )
    except Exception as exc:  # pragma: no cover - top level CLI error handling
        LOGGER.error("Failed to download video: %s", exc)
        return 1

    print(str(downloaded_path))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
