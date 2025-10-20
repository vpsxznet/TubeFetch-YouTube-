from __future__ import annotations

from unittest import mock

import pytest

from tube_fetch import cli


@pytest.fixture(autouse=True)
def patch_downloader(monkeypatch):
    fake_extract = mock.Mock()
    fake_downloader_cls = mock.Mock()
    fake_downloader = fake_downloader_cls.return_value
    fake_downloader.download.return_value = "video.mp4"
    monkeypatch.setattr(cli, "extract_video_info", fake_extract)
    monkeypatch.setattr(cli, "VideoDownloader", fake_downloader_cls)
    yield fake_extract, fake_downloader


def test_cli_info_mode_json(capsys, patch_downloader):
    fake_extract, _ = patch_downloader
    fake_extract.return_value.to_json.return_value = "{}"

    exit_code = cli.main([
        "https://youtu.be/demo",
        "--info",
        "--json",
    ])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "{}"


def test_cli_download_mode(capsys, patch_downloader):
    _, fake_downloader = patch_downloader

    exit_code = cli.main(["https://youtu.be/demo"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out.strip() == "video.mp4"
    fake_downloader.download.assert_called_once()


def test_cli_extra_option_validation(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["https://youtu.be/demo", "--extra-option", "invalid"])
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "Invalid --extra-option" in captured.err
