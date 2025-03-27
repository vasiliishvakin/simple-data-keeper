import pytest

from app.utils.helpers import safe_join


def test_safe_join(tmp_path):
    base_dir = tmp_path

    # 1. Valid relative path
    relative_path = "test/file.txt"
    expected = tmp_path / relative_path
    assert safe_join(str(base_dir), relative_path) == str(expected)

    # 2. Empty path
    assert safe_join(str(base_dir), "") == str(base_dir)

    # 3. Current directory
    assert safe_join(str(base_dir), ".") == str(base_dir)

    # 4. Path traversal with '..'
    with pytest.raises(ValueError, match="Path escapes base directory"):
        safe_join(str(base_dir), "../outside.txt")

    # 5. Absolute path
    with pytest.raises(ValueError, match="Path escapes base directory"):
        safe_join(str(base_dir), "/absolute/path.txt")

    # 6. Symlink that escapes base
    outside_dir = base_dir.parent / "outside"
    outside_dir.mkdir()
    symlink = base_dir / "symlink"
    symlink.symlink_to(outside_dir)

    with pytest.raises(ValueError, match="Path escapes base directory"):
        safe_join(str(base_dir), "symlink/../outside.txt")
