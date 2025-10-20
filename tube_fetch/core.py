"""Core download utilities for TubeFetch."""

from __future__ import annotations

import dataclasses
import json
import logging
import pathlib
from typing import Any, Dict, Iterable, Optional

try:
    import yt_dlp  # type: ignore
except Exception as exc:  # pragma: no cover - import guard
    yt_dlp = None  # type: ignore
    _IMPORT_ERROR = exc
else:  # pragma: no cover - import guard
    _IMPORT_ERROR = None

LOGGER = logging.getLogger(__name__)


class YTDLPNotInstalledError(RuntimeError):
    """Raised when :mod:`yt_dlp` is not installed."""

    def __init__(self) -> None:
        message = (
            "The 'yt_dlp' package is required to use TubeFetch. "
            "Install it via `pip install yt-dlp` or add it to your environment."
        )
        super().__init__(message)


@dataclasses.dataclass(slots=True)
class VideoInfo:
    """A lightweight structure representing the extracted video metadata."""

    id: str
    title: str
    uploader: Optional[str]
    duration: Optional[int]
    webpage_url: str
    description: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    upload_date: Optional[str] = None

    def to_json(self) -> str:
        """Serialize the :class:`VideoInfo` to a JSON string."""

        return json.dumps(dataclasses.asdict(self), ensure_ascii=False, indent=2)


_DEFAULT_FORMAT = "bestvideo+bestaudio/best"
_DEFAULT_AUDIO_FORMAT = "bestaudio/best"


def _ensure_backend() -> None:
    if yt_dlp is None:
        raise YTDLPNotInstalledError() from _IMPORT_ERROR


def _build_options(
    output_dir: Optional[pathlib.Path] = None,
    *,
    audio_only: bool = False,
    format: Optional[str] = None,
    proxy: Optional[str] = None,
    extra_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    options: Dict[str, Any] = {
        "outtmpl": str((output_dir or pathlib.Path.cwd()) / "%(title)s.%(ext)s"),
        "format": format
        or (_DEFAULT_AUDIO_FORMAT if audio_only else _DEFAULT_FORMAT),
        "noplaylist": True,
        "quiet": True,
        "nocheckcertificate": True,
    }

    if proxy:
        options["proxy"] = proxy

    if extra_options:
        options.update(extra_options)

    return options


def extract_video_info(url: str, *, proxy: Optional[str] = None) -> VideoInfo:
    """Extract metadata for a YouTube video.

    Parameters
    ----------
    url:
        The YouTube video URL to extract information from.
    proxy:
        Optional proxy string to use for the request.
    """

    _ensure_backend()

    options = _build_options(proxy=proxy)

    with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore[attr-defined]
        LOGGER.debug("Extracting information for %s", url)
        info = ydl.extract_info(url, download=False)

    return VideoInfo(
        id=info.get("id", ""),
        title=info.get("title", ""),
        uploader=info.get("uploader"),
        duration=info.get("duration"),
        webpage_url=info.get("webpage_url", url),
        description=info.get("description"),
        view_count=info.get("view_count"),
        like_count=info.get("like_count"),
        upload_date=info.get("upload_date"),
    )


def download_video(
    url: str,
    output_dir: Optional[pathlib.Path] = None,
    *,
    audio_only: bool = False,
    format: Optional[str] = None,
    proxy: Optional[str] = None,
    extra_options: Optional[Dict[str, Any]] = None,
) -> pathlib.Path:
    """Download a YouTube video or audio track.

    Returns the path to the downloaded file."""

    _ensure_backend()

    options = _build_options(
        output_dir=output_dir,
        audio_only=audio_only,
        format=format,
        proxy=proxy,
        extra_options=extra_options,
    )

    with yt_dlp.YoutubeDL(options) as ydl:  # type: ignore[attr-defined]
        LOGGER.debug("Downloading %s with options %s", url, options)
        result = ydl.extract_info(url, download=True)

    if "requested_downloads" in result:
        # When using newer yt-dlp releases the return value may be a dict
        # containing multiple downloads; pick the first produced file.
        downloads: Iterable[Dict[str, Any]] = result["requested_downloads"]
        for download in downloads:
            filename = download.get("_filename")
            if filename:
                return pathlib.Path(filename)

    filename = result.get("_filename")
    if not filename:
        raise RuntimeError("yt-dlp did not report a download filename")

    return pathlib.Path(filename)


class VideoDownloader:
    """High level API for downloading videos and metadata."""

    def __init__(
        self,
        *,
        output_dir: Optional[pathlib.Path] = None,
        proxy: Optional[str] = None,
    ) -> None:
        self.output_dir = output_dir
        self.proxy = proxy

    def fetch_info(self, url: str) -> VideoInfo:
        return extract_video_info(url, proxy=self.proxy)

    def download(
        self,
        url: str,
        *,
        audio_only: bool = False,
        format: Optional[str] = None,
        extra_options: Optional[Dict[str, Any]] = None,
    ) -> pathlib.Path:
        return download_video(
            url,
            self.output_dir,
            audio_only=audio_only,
            format=format,
            proxy=self.proxy,
            extra_options=extra_options,
        )
