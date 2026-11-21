from pathlib import Path

from dotenv import dotenv_values
import pytest

from agent import save_local_configuration


def test_local_config_persists_privately_and_preserves_other_settings(tmp_path):
    (tmp_path / ".gitignore").write_text(".env.*\n")
    (tmp_path / ".env.local").write_text("OTHER_SETTING=keep\n")
    save_local_configuration("test-only-placeholder", "gemini-4-hydrogen", root=tmp_path)
    values = dotenv_values(tmp_path / ".env.local")
    assert values["GEMINI_API_KEY"] == "test-only-placeholder"
    assert values["GEMINI_MODEL"] == "gemini-4-hydrogen"
    assert values["OTHER_SETTING"] == "keep"
    assert (tmp_path / ".env.local").stat().st_mode & 0o777 == 0o600
    assert not list(tmp_path.glob(".key-setup-*"))


def test_save_refuses_unignored_file_and_symlink(tmp_path):
    with pytest.raises(ValueError, match="gitignore"):
        save_local_configuration("test-only-placeholder", "gemini-4-hydrogen", root=tmp_path)
    (tmp_path / ".gitignore").write_text(".env.*\n")
    other = tmp_path / "other"
    other.write_text("unchanged")
    (tmp_path / ".env.local").symlink_to(other)
    with pytest.raises(ValueError, match="symbolic"):
        save_local_configuration("test-only-placeholder", "gemini-4-hydrogen", root=tmp_path)
    assert other.read_text() == "unchanged"
