from pathlib import Path


def test_developer_tools_uses_public_entry_attribute():
    source = Path("custom_components/btdoor_security_plus/developer.py").read_text()
    assert "dict(self._entry.options)" not in source
    assert "visibility_for_entry(self._entry)" not in source
    assert "dict(self.entry.options)" in source
    assert "visibility_for_entry(self.entry)" in source


def test_canonical_english_device_names():
    source = Path("custom_components/btdoor_security_plus/device_model/factory.py").read_text()
    source += Path("custom_components/btdoor_security_plus/device_model/names.py").read_text()
    for name in (
        "Cloud Status",
        "SIP Monitor",
        "Call Manager",
        "Multimedia Monitor",
        "Advanced Diagnostics",
    ):
        assert name in source
