import json
from unittest.mock import MagicMock, patch

import pytest
import requests

import sitecheck


def fake_response(status=200):
    resp = MagicMock()
    resp.status_code = status
    return resp


def test_healthy_site():
    with patch("sitecheck.requests.get", return_value=fake_response(200)), \
         patch("sitecheck.get_cert_days_left", return_value=90):
        r = sitecheck.check_url("https://example.com")
    assert r.ok and r.status_code == 200 and r.cert_days_left == 90


def test_bad_status_flagged():
    with patch("sitecheck.requests.get", return_value=fake_response(500)), \
         patch("sitecheck.get_cert_days_left", return_value=90):
        r = sitecheck.check_url("https://example.com")
    assert not r.ok and "bad status 500" in r.problems[0]


def test_timeout_does_not_crash():
    with patch("sitecheck.requests.get", side_effect=requests.exceptions.Timeout), \
         patch("sitecheck.get_cert_days_left", return_value=90):
        r = sitecheck.check_url("https://example.com")
    assert not r.ok and "timed out" in r.problems[0]


def test_connection_error_does_not_crash():
    with patch("sitecheck.requests.get", side_effect=requests.exceptions.ConnectionError), \
         patch("sitecheck.get_cert_days_left", side_effect=OSError("no route")):
        r = sitecheck.check_url("https://example.com")
    assert not r.ok and len(r.problems) == 1  # no duplicate cert problem


def test_cert_expiring_soon_flagged():
    with patch("sitecheck.requests.get", return_value=fake_response(200)), \
         patch("sitecheck.get_cert_days_left", return_value=5):
        r = sitecheck.check_url("https://example.com")
    assert not r.ok and "expires in 5 days" in r.problems[0]


def test_expired_cert_flagged():
    with patch("sitecheck.requests.get", return_value=fake_response(200)), \
         patch("sitecheck.get_cert_days_left", return_value=-3):
        r = sitecheck.check_url("https://example.com")
    assert "expired" in r.problems[0]


def test_http_url_skips_cert_check():
    with patch("sitecheck.requests.get", return_value=fake_response(200)), \
         patch("sitecheck.get_cert_days_left") as cert:
        r = sitecheck.check_url("http://example.com")
    cert.assert_not_called()
    assert r.ok and r.cert_days_left is None


def test_load_config_valid(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"sites": ["https://a.com"]}))
    assert sitecheck.load_config(str(p))["sites"] == ["https://a.com"]


@pytest.mark.parametrize("content", ["not json", "{}", '{"sites": []}', '{"sites": ["ftp://x"]}'])
def test_load_config_invalid(tmp_path, content):
    p = tmp_path / "c.json"
    p.write_text(content)
    with pytest.raises(ValueError):
        sitecheck.load_config(str(p))


def test_exit_codes(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"sites": ["https://a.com"]}))
    with patch("sitecheck.requests.get", return_value=fake_response(200)), \
         patch("sitecheck.get_cert_days_left", return_value=90):
        assert sitecheck.main([str(p)]) == 0
    with patch("sitecheck.requests.get", return_value=fake_response(503)), \
         patch("sitecheck.get_cert_days_left", return_value=90):
        assert sitecheck.main([str(p)]) == 1
    assert sitecheck.main([str(tmp_path / "missing.json")]) == 2
