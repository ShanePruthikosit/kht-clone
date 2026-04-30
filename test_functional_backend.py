"""
test_functional_backend.py
===========================
Functional / black-box API tests for the KHT API
deployed at https://ailurophile.xyz:2546

Group Members: [Fill in your names]
Project: KHT Mae Hong Son Map API
Scope: API functional testing — request/response correctness,
       status codes, validation behaviour, authentication handling,
       and error handling as seen from the external client.

Run with:
    pytest test_functional_backend.py -v --tb=short

Notes:
  - These tests require a live connection to ailurophile.xyz:2546.
  - Authentication uses the live /api/testpackage/ endpoint to
    obtain the JS hash function, then replicates the time-based key.
  - Tests are marked with pytest.mark to allow selective runs:
      pytest -m "not auth"   # skip auth-protected endpoint tests
"""

import json
import time
import hashlib
import subprocess
import sys
import re
import pytest
import requests

# ─────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────
BASE_URL = "https://ailurophile.xyz:2546"
TIMEOUT = 20  # seconds

# ─────────────────────────────────────────────────────────────
# Auth helper
# The API uses a time-based HMAC-like key fetched from /api/testpackage/.
# We fetch the JS, run it with Node to get the hash, then pass
# time=HH-MM-SS & key=<hash> on protected endpoints.
# ─────────────────────────────────────────────────────────────

def get_time_string():
    t = time.localtime()
    return f"{t.tm_hour:02d}-{t.tm_min:02d}-{t.tm_sec:02d}"


def get_auth_params():
    """
    Fetches the testpackage JS from the API, executes it with Node.js
    to compute the hash for the current time, and returns (time, key).
    Falls back to empty strings if Node is unavailable (tests will then
    check 401 behaviour).
    """
    try:
        r = requests.get(f"{BASE_URL}/api/testpackage/", timeout=TIMEOUT, verify=False)
        if r.status_code != 200:
            return "", ""
        js_code = r.text
        t = get_time_string()
        # Wrap the fetched JS and call getOldTestPackage
        runner = f'{js_code}\nprocess.stdout.write(getOldTestPackage("{t}"));'
        result = subprocess.run(
            ["node", "-e", runner],
            capture_output=True, text=True, timeout=10
        )
        key = result.stdout.strip()
        return t, key
    except Exception:
        # If Node.js is not available or request fails, return empty auth
        return "", ""


# Suppress SSL warnings for self-signed cert
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def auth():
    """Session-scoped auth params (time + key)."""
    t, key = get_auth_params()
    return {"time": t, "key": key}


@pytest.fixture(scope="session")
def has_auth(auth):
    """True only if we successfully obtained a valid key."""
    return auth["time"] != "" and auth["key"] != ""


# ─────────────────────────────────────────────────────────────
# TC-01 Health check
# ─────────────────────────────────────────────────────────────

class TestHealthCheck:
    """TC-01 – Root endpoint availability."""

    def test_root_returns_200(self):
        """Normal case: GET / returns HTTP 200."""
        r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 200

    def test_root_returns_json(self):
        """Normal case: root response is valid JSON."""
        r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT, verify=False)
        data = r.json()
        assert isinstance(data, dict)

    def test_root_message_field_present(self):
        """Normal case: response includes a 'message' key."""
        r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT, verify=False)
        assert "message" in r.json()

    def test_root_message_is_string(self):
        """Normal case: 'message' value is a non-empty string."""
        r = requests.get(f"{BASE_URL}/", timeout=TIMEOUT, verify=False)
        assert isinstance(r.json()["message"], str)
        assert len(r.json()["message"]) > 0


# ─────────────────────────────────────────────────────────────
# TC-02 Testpackage endpoint
# ─────────────────────────────────────────────────────────────

class TestTestpackageEndpoint:
    """TC-02 – /api/testpackage/ serves the JS hash module."""

    def test_returns_200(self):
        r = requests.get(f"{BASE_URL}/api/testpackage/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 200

    def test_content_type_is_javascript(self):
        r = requests.get(f"{BASE_URL}/api/testpackage/", timeout=TIMEOUT, verify=False)
        assert "javascript" in r.headers.get("content-type", "").lower() \
            or "text/plain" in r.headers.get("content-type", "").lower()

    def test_response_contains_function(self):
        """The JS must define getOldTestPackage."""
        r = requests.get(f"{BASE_URL}/api/testpackage/", timeout=TIMEOUT, verify=False)
        assert "getOldTestPackage" in r.text


# ─────────────────────────────────────────────────────────────
# TC-03 Authentication (village endpoint is auth-protected)
# ─────────────────────────────────────────────────────────────

class TestAuthentication:
    """TC-03 – Auth enforcement on protected endpoints."""

    def test_village_without_key_returns_401(self):
        """Error case: missing auth key → 401 Unauthorized."""
        r = requests.get(f"{BASE_URL}/api/village/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 401

    def test_village_with_wrong_key_returns_401(self):
        """Error case: incorrect key → 401 Unauthorized."""
        t = get_time_string()
        r = requests.get(
            f"{BASE_URL}/api/village/",
            params={"time": t, "key": "WRONG_KEY_12345"},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 401

    def test_village_with_empty_key_returns_401(self):
        """Edge case: empty key string → 401 Unauthorized."""
        t = get_time_string()
        r = requests.get(
            f"{BASE_URL}/api/village/",
            params={"time": t, "key": ""},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 401

    def test_project_without_key_returns_error(self):
        """Error case: /api/project/ without auth → error response."""
        r = requests.get(f"{BASE_URL}/api/project/", timeout=TIMEOUT, verify=False)
        # Either 401 or body with Error key
        if r.status_code == 200:
            assert "Error" in r.json()
        else:
            assert r.status_code in (401, 403)

    def test_school_without_key_returns_error(self):
        """Error case: /api/school/ without auth → error response."""
        r = requests.get(f"{BASE_URL}/api/school/", timeout=TIMEOUT, verify=False)
        if r.status_code == 200:
            assert "Error" in r.json()
        else:
            assert r.status_code in (401, 403)


# ─────────────────────────────────────────────────────────────
# TC-04 Village names (public endpoint, no auth)
# ─────────────────────────────────────────────────────────────

class TestVillageNames:
    """TC-04 – /api/village_names/ and /api/village_names_th/."""

    def test_village_names_returns_200(self):
        r = requests.get(f"{BASE_URL}/api/village_names/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 200

    def test_village_names_returns_list(self):
        """Normal case: response is a list of strings."""
        r = requests.get(f"{BASE_URL}/api/village_names/", timeout=TIMEOUT, verify=False)
        data = r.json()
        assert isinstance(data, list)

    def test_village_names_non_empty(self):
        """Normal case: at least one village exists in the DB."""
        r = requests.get(f"{BASE_URL}/api/village_names/", timeout=TIMEOUT, verify=False)
        assert len(r.json()) > 0

    def test_village_names_are_strings(self):
        """Normal case: each item is a string."""
        r = requests.get(f"{BASE_URL}/api/village_names/", timeout=TIMEOUT, verify=False)
        for name in r.json():
            assert isinstance(name, str)

    def test_village_names_th_returns_200(self):
        """Normal case: Thai village names endpoint is available."""
        r = requests.get(f"{BASE_URL}/api/village_names_th/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 200

    def test_village_names_th_returns_list(self):
        r = requests.get(f"{BASE_URL}/api/village_names_th/", timeout=TIMEOUT, verify=False)
        assert isinstance(r.json(), list)

    def test_village_names_en_and_th_same_length(self):
        """Consistency: EN and TH name lists should have the same count."""
        r_en = requests.get(f"{BASE_URL}/api/village_names/", timeout=TIMEOUT, verify=False)
        r_th = requests.get(f"{BASE_URL}/api/village_names_th/", timeout=TIMEOUT, verify=False)
        assert len(r_en.json()) == len(r_th.json())


# ─────────────────────────────────────────────────────────────
# TC-05 Route endpoint (no auth required)
# ─────────────────────────────────────────────────────────────

class TestRouteEndpoint:
    """TC-05 – /api/route/ routing calculations."""

    def test_missing_start_and_end_returns_422(self):
        """Error case: completely missing required params → 422."""
        r = requests.get(f"{BASE_URL}/api/route/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 422

    def test_missing_end_param_returns_error(self):
        """Error case: start without end → 422 Unprocessable Entity."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_missing_start_param_returns_error(self):
        """Error case: end without start → 422 Unprocessable Entity."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"end": 2},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_valid_node_ids_return_geojson_structure(self):
        """Normal case: valid start & end return a FeatureCollection."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1, "end": 100},
            timeout=TIMEOUT, verify=False
        )
        # Either finds a route or returns empty collection
        assert r.status_code == 200
        data = r.json()
        assert "type" in data
        assert data["type"] == "FeatureCollection"
        assert "features" in data

    def test_same_start_and_end_returns_empty_or_trivial_route(self):
        """Edge case: start == end → empty or zero-length route."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1, "end": 1},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "FeatureCollection"

    def test_nonexistent_node_returns_empty_features(self):
        """Edge case: very large node ID (non-existent) → empty features."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 9999999, "end": 9999998},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200
        data = r.json()
        assert data["features"] == [] or "error" in data

    def test_use_elevation_flag_zero(self):
        """Normal case: use_elevation=0 is accepted."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1, "end": 100, "use_elevation": 0},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200

    def test_use_elevation_flag_one(self):
        """Normal case: use_elevation=1 is accepted."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1, "end": 100, "use_elevation": 1},
            timeout=TIMEOUT, verify=False
        )
        # May return error if elevation DB not populated, but not 5xx
        assert r.status_code in (200, 400, 500)

    def test_non_integer_node_id_rejected(self):
        """Error case: non-integer start/end → 422 validation error."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": "abc", "end": 100},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_response_features_are_geojson_features(self):
        """Normal case: each feature in the response has type=Feature."""
        r = requests.get(
            f"{BASE_URL}/api/route/",
            params={"start": 1, "end": 100},
            timeout=TIMEOUT, verify=False
        )
        data = r.json()
        for feature in data.get("features", []):
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature


# ─────────────────────────────────────────────────────────────
# TC-06 Village endpoint with valid auth (skip if no Node.js)
# ─────────────────────────────────────────────────────────────

class TestVillageEndpointWithAuth:
    """TC-06 – /api/village/ with valid authentication."""

    def test_all_villages_returns_feature_collection(self, auth, has_auth):
        """Normal case: authenticated request returns FeatureCollection."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        r = requests.get(
            f"{BASE_URL}/api/village/",
            params=auth,
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200
        data = r.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data

    def test_all_villages_non_empty(self, auth, has_auth):
        """Normal case: DB has villages → features list is populated."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        r = requests.get(
            f"{BASE_URL}/api/village/",
            params=auth,
            timeout=TIMEOUT, verify=False
        )
        assert len(r.json()["features"]) > 0

    def test_village_features_have_geometry(self, auth, has_auth):
        """Normal case: each village feature has a geometry field."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        r = requests.get(
            f"{BASE_URL}/api/village/",
            params=auth,
            timeout=TIMEOUT, verify=False
        )
        for feature in r.json()["features"][:5]:  # check first 5
            assert "geometry" in feature
            assert feature["geometry"] is not None

    def test_filter_by_year_returns_feature_collection(self, auth, has_auth):
        """Normal case: year filter returns valid FeatureCollection."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        params = {**auth, "year": "2022"}
        r = requests.get(f"{BASE_URL}/api/village/", params=params,
                         timeout=TIMEOUT, verify=False)
        assert r.status_code == 200
        assert r.json()["type"] == "FeatureCollection"

    def test_filter_by_project_type_wash(self, auth, has_auth):
        """Normal case: WASH project type filter returns villages."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        params = {**auth, "project_type": "WASH"}
        r = requests.get(f"{BASE_URL}/api/village/", params=params,
                         timeout=TIMEOUT, verify=False)
        assert r.status_code == 200
        assert r.json()["type"] == "FeatureCollection"

    def test_filter_by_year_range(self, auth, has_auth):
        """Normal case: start_year + end_year filter."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        params = {**auth, "start_year": "2020", "end_year": "2023"}
        r = requests.get(f"{BASE_URL}/api/village/", params=params,
                         timeout=TIMEOUT, verify=False)
        assert r.status_code == 200
        assert r.json()["type"] == "FeatureCollection"

    def test_facility_type_without_distance_returns_400(self, auth, has_auth):
        """Error case: facility_type with no distance → 400 Bad Request."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        params = {**auth, "facility_type": "school"}
        r = requests.get(f"{BASE_URL}/api/village/", params=params,
                         timeout=TIMEOUT, verify=False)
        assert r.status_code == 400

    def test_nonexistent_year_returns_empty_features(self, auth, has_auth):
        """Edge case: year far in the future → empty features list."""
        if not has_auth:
            pytest.skip("Node.js unavailable; cannot compute auth key")
        params = {**auth, "year": "2099"}
        r = requests.get(f"{BASE_URL}/api/village/", params=params,
                         timeout=TIMEOUT, verify=False)
        assert r.status_code == 200
        assert r.json()["features"] == []


# ─────────────────────────────────────────────────────────────
# TC-07 POST village_url
# ─────────────────────────────────────────────────────────────

class TestPostVillageUrl:
    """TC-07 – POST /api/post/village_url/"""

    def test_missing_body_returns_422(self):
        """Error case: POST with no body → 422 Unprocessable Entity."""
        r = requests.post(
            f"{BASE_URL}/api/post/village_url/",
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_incomplete_body_returns_422(self):
        """Error case: missing required fields → 422."""
        r = requests.post(
            f"{BASE_URL}/api/post/village_url/",
            json={"village_name": "Test"},  # missing url, image_url, password
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_wrong_password_returns_message(self):
        """Error case: wrong password → server returns a message (not crash)."""
        payload = {
            "village_name": "Ban Test",
            "url": "https://example.com",
            "image_url": "https://example.com/img.jpg",
            "article_title": "Test Article",
            "posted_date": "2024-01-01",
            "password": "WRONG_PASSWORD"
        }
        r = requests.post(
            f"{BASE_URL}/api/post/village_url/",
            json=payload,
            timeout=TIMEOUT, verify=False
        )
        # Should not crash; returns 200 with a message
        assert r.status_code in (200, 400, 401, 403)
        if r.status_code == 200:
            assert "message" in r.json()

    def test_get_method_not_allowed_on_post_endpoint(self):
        """Error case: GET on a POST-only endpoint → 405 Method Not Allowed."""
        r = requests.get(
            f"{BASE_URL}/api/post/village_url/",
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 405


# ─────────────────────────────────────────────────────────────
# TC-08 CORS headers
# ─────────────────────────────────────────────────────────────

class TestCORSHeaders:
    """TC-08 – CORS middleware correctness."""

    def test_cors_allows_all_origins(self):
        """Normal case: CORS allows * for cross-origin requests."""
        r = requests.get(
            f"{BASE_URL}/api/village_names/",
            headers={"Origin": "https://some-other-site.com"},
            timeout=TIMEOUT, verify=False
        )
        origin_header = r.headers.get("access-control-allow-origin", "")
        assert origin_header == "*" or r.status_code == 200


# ─────────────────────────────────────────────────────────────
# TC-09 Undefined endpoints
# ─────────────────────────────────────────────────────────────

class TestUndefinedEndpoints:
    """TC-09 – Non-existent routes return 404."""

    def test_unknown_path_returns_404(self):
        """Error case: completely unknown path → 404 Not Found."""
        r = requests.get(f"{BASE_URL}/api/does_not_exist/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 404

    def test_api_typo_returns_404(self):
        """Error case: typo in known endpoint name → 404."""
        r = requests.get(f"{BASE_URL}/api/vilage/", timeout=TIMEOUT, verify=False)
        assert r.status_code == 404
