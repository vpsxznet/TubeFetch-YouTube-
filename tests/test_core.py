from __future__ import annotations

import pathlib
from unittest import mock

import pytest

from tube_fetch import core


@pytest.fixture(autouse=True)
def patch_backend(monkeypatch):
    fake_module = mock.MagicMock()
    fake_context = fake_module.YoutubeDL.return_value.__enter__.return_value
    fake_context.extract_info = mock.Mock()
    monkeypatch.setattr(core, "yt_dlp", fake_module)
    monkeypatch.setattr(core, "_IMPORT_ERROR", None)
    yield fake_module, fake_context


def test_extract_video_info(patch_backend):
    _, fake_context = patch_backend
    info_payload = {
        "id": "abc123",
        "title": "Sample Video",
        "uploader": "Uploader",
        "duration": 120,
        "webpage_url": "https://youtu.be/abc123",
        "description": "A demo",
        "view_count": 1000,
        "like_count": 50,
        "upload_date": "20240101",
    }

    fake_context.extract_info.return_value = info_payload

    info = core.extract_video_info("https://youtu.be/abc123")

    assert info.id == "abc123"
    assert info.title == "Sample Video"
    assert info.duration == 120
    assert info.to_json().startswith("{\n  \"id\": \"abc123\"")


def test_download_video_returns_path(patch_backend):
    _, fake_context = patch_backend
    fake_context.extract_info.return_value = {"_filename": "/tmp/video.mp4"}

    path = core.download_video("https://youtu.be/abc123")

    assert path == pathlib.Path("/tmp/video.mp4")


def test_download_video_handles_requested_downloads(patch_backend):
    _, fake_context = patch_backend
    fake_context.extract_info.return_value = {
        "requested_downloads": [{"_filename": "/tmp/audio.m4a"}]
    }

    path = core.download_video("https://youtu.be/abc123")

    assert path == pathlib.Path("/tmp/audio.m4a")


def test_download_video_raises_when_no_filename(patch_backend):
    _, fake_context = patch_backend
    fake_context.extract_info.return_value = {}

    with pytest.raises(RuntimeError):
        core.download_video("https://youtu.be/abc123")


def test_video_downloader_wrapper(patch_backend):
    fake_module, fake_context = patch_backend
    fake_context.extract_info.return_value = {"_filename": "/tmp/video.mp4"}

    downloader = core.VideoDownloader(output_dir=pathlib.Path("/videos"), proxy="http://proxy")

    downloader.fetch_info("https://youtu.be/abc123")
    downloader.download("https://youtu.be/abc123", audio_only=True, format="best")

    assert fake_module.YoutubeDL.call_count == 2
    fake_context.extract_info.assert_any_call("https://youtu.be/abc123", download=False)
    fake_context.extract_info.assert_any_call("https://youtu.be/abc123", download=True)
