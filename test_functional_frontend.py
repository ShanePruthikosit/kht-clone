"""
test_functional_frontend.py
============================
Functional / black-box tests for the KHT Map frontend
deployed at https://ailurophile.xyz

Group Members: [Fill in your names]
Project: KHT Mae Hong Son Map — Frontend
Scope: UI functional testing via HTTP requests. Tests verify the
       observable behavior of the frontend as a user/browser would
       experience it: page loading, resource availability, HTML
       structure, API calls the page initiates, and end-to-end
       data flows visible from the external interface.

       Note: Full browser automation (Selenium/Playwright) is not used
       here to keep setup minimal. Tests verify HTTP-level behavior
       that is equivalent to what a user sees in a browser. Browser
       automation tests can be added as an extension.

Run with:
    pytest test_functional_frontend.py -v --tb=short
"""

import re
import time
import pytest
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://ailurophile.xyz"
TIMEOUT = 20

# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def get(path, **kwargs):
    return requests.get(f"{BASE}{path}", timeout=TIMEOUT, verify=False, **kwargs)


# ─────────────────────────────────────────────────────────────
# TC-F01 Page availability
# ─────────────────────────────────────────────────────────────

class TestPageAvailability:
    """TC-F01 – Main pages load successfully."""

    def test_root_page_returns_200(self):
        """Normal case: homepage returns HTTP 200."""
        r = get("/")
        assert r.status_code == 200

    def test_root_page_is_html(self):
        """Normal case: response Content-Type contains text/html."""
        r = get("/")
        assert "text/html" in r.headers.get("content-type", "").lower()

    def test_map_html_returns_200(self):
        """Normal case: /map.html is accessible."""
        r = get("/map.html")
        assert r.status_code == 200

    def test_village_map_returns_200(self):
        """Normal case: /village-map.html is accessible."""
        r = get("/village-map.html")
        assert r.status_code == 200

    def test_tour_html_returns_200(self):
        """Normal case: /tour.html is accessible."""
        r = get("/tour.html")
        assert r.status_code == 200


# ─────────────────────────────────────────────────────────────
# TC-F02 HTML structure / required elements
# ─────────────────────────────────────────────────────────────

class TestHtmlStructure:
    """TC-F02 – Critical HTML elements are present in page source."""

    def test_page_has_title(self):
        """Normal case: page has a <title> tag."""
        r = get("/")
        assert "<title>" in r.text.lower()

    def test_page_has_map_element(self):
        """Normal case: map container div is present in the HTML."""
        r = get("/map.html")
        assert 'id="map"' in r.text

    def test_page_references_leaflet_css(self):
        """Normal case: Leaflet CSS is linked."""
        r = get("/map.html")
        assert "leaflet" in r.text.lower()

    def test_page_references_leaflet_js(self):
        """Normal case: Leaflet JS is included."""
        r = get("/map.html")
        assert "leaflet" in r.text.lower() and ".js" in r.text

    def test_index_js_is_referenced(self):
        """Normal case: main JS module is referenced in map.html."""
        r = get("/map.html")
        assert "index.js" in r.text

    def test_bootstrap_is_referenced(self):
        """Normal case: Bootstrap CSS/JS is referenced in index.html."""
        r = get("/")
        assert "bootstrap" in r.text.lower()

    def test_search_button_present_in_index(self):
        """Normal case: search button exists in the sidebar HTML."""
        r = get("/")
        assert "searchButton" in r.text or "search" in r.text.lower()

    def test_tour_button_present(self):
        """Normal case: virtual tour button is in index.html."""
        r = get("/")
        assert "tourButton" in r.text or "tour" in r.text.lower()

    def test_kht_title_or_branding(self):
        """Normal case: KHT branding present in the page."""
        r = get("/")
        assert "KHT" in r.text or "Mae Hong Son" in r.text or "kht" in r.text.lower()


# ─────────────────────────────────────────────────────────────
# TC-F03 Static assets load correctly
# ─────────────────────────────────────────────────────────────

class TestStaticAssets:
    """TC-F03 – Static JS / CSS / image files are served."""

    def test_index_js_returns_200(self):
        """Normal case: main JS file is served."""
        r = get("/index.js")
        assert r.status_code == 200

    def test_get_data_js_returns_200(self):
        """Normal case: get_data.js module is served."""
        r = get("/get_data.js")
        assert r.status_code == 200

    def test_stylesheet_css_returns_200(self):
        """Normal case: stylesheet.css is served."""
        r = get("/stylesheet.css")
        assert r.status_code == 200

    def test_index_stylesheet_css_returns_200(self):
        """Normal case: index_stylesheet.css is served."""
        r = get("/index_stylesheet.css")
        assert r.status_code == 200

    def test_routing_mode_js_returns_200(self):
        """Normal case: routingMode.js is served."""
        r = get("/routingMode.js")
        assert r.status_code == 200

    def test_kht_image_returns_200(self):
        """Normal case: KHT logo image is served."""
        r = get("/img/KHT.jpg")
        assert r.status_code == 200

    def test_hospital_marker_image_returns_200(self):
        """Normal case: hospital map marker image is served."""
        r = get("/img/hospital_marker.png")
        assert r.status_code == 200

    def test_school_marker_image_returns_200(self):
        """Normal case: school map marker image is served."""
        r = get("/img/school_marker.png")
        assert r.status_code == 200

    def test_missing_asset_returns_404(self):
        """Error case: non-existent file returns 404."""
        r = get("/img/does_not_exist.png")
        assert r.status_code == 404

    def test_js_content_type_correct(self):
        """Normal case: JS files have a JavaScript content-type."""
        r = get("/index.js")
        ct = r.headers.get("content-type", "").lower()
        assert "javascript" in ct or "text/plain" in ct or "application/octet" in ct

    def test_css_content_type_correct(self):
        """Normal case: CSS file has text/css content type."""
        r = get("/stylesheet.css")
        ct = r.headers.get("content-type", "").lower()
        assert "css" in ct or "text/plain" in ct


# ─────────────────────────────────────────────────────────────
# TC-F04 JavaScript content — logic validation
# ─────────────────────────────────────────────────────────────

class TestJavaScriptContent:
    """TC-F04 – JS source code contains expected logic."""

    def test_get_data_js_exports_get_village_data(self):
        """Normal case: getVillageData function is defined."""
        r = get("/get_data.js")
        assert "getVillageData" in r.text

    def test_get_data_js_exports_get_hospitals(self):
        """Normal case: getHospitals function is defined."""
        r = get("/get_data.js")
        assert "getHospitals" in r.text

    def test_get_data_js_exports_get_schools(self):
        """Normal case: getSchools function is defined."""
        r = get("/get_data.js")
        assert "getSchools" in r.text

    def test_get_data_js_references_api_route(self):
        """Normal case: routing API call is referenced."""
        r = get("/get_data.js")
        assert "/api/route/" in r.text

    def test_get_data_js_references_api_village(self):
        """Normal case: village API call is referenced."""
        r = get("/get_data.js")
        assert "/api/village/" in r.text

    def test_index_js_has_year_slider(self):
        """Normal case: year slider component exists in source."""
        r = get("/index.js")
        assert "year" in r.text.lower() and ("slider" in r.text.lower() or "range" in r.text.lower())

    def test_index_js_has_radio_buttons(self):
        """Normal case: radio filter buttons are defined."""
        r = get("/index.js")
        assert "radio" in r.text.lower()

    def test_project_type_mapping_present(self):
        """Normal case: WASH project type is mapped in get_data.js."""
        r = get("/get_data.js")
        assert "WASH" in r.text

    def test_fetch_initial_village_data_called(self):
        """Normal case: initial village fetch is invoked."""
        r = get("/index.js")
        assert "fetchInitialVillageData" in r.text

    def test_cors_origin_not_hardcoded_to_localhost(self):
        """Security: JS does not hardcode localhost as the API host."""
        r = get("/get_data.js")
        # Should use config-based host, not hardcoded localhost
        assert "localhost" not in r.text


# ─────────────────────────────────────────────────────────────
# TC-F05 End-to-end data flow (frontend → API → response)
# ─────────────────────────────────────────────────────────────

class TestEndToEndDataFlow:
    """
    TC-F05 – End-to-end: replicate the browser's API calls and verify
    the data returned matches what the UI would display.
    Village names endpoint is public; used to test the full data path.
    """

    def test_village_names_api_reachable_from_frontend_host(self):
        """Normal case: API that frontend calls is reachable."""
        # The frontend calls https://kht-map.org:2546 (or ailurophile.xyz:2546)
        # We verify the public village_names endpoint is accessible
        r = requests.get(
            "https://ailurophile.xyz:2546/api/village_names/",
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200

    def test_village_names_non_empty_list(self):
        """Normal case: village names list populates the autocomplete."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/village_names/",
            timeout=TIMEOUT, verify=False
        )
        data = r.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_thai_village_names_accessible(self):
        """Normal case: Thai names endpoint works (used in village detail panel)."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/village_names_th/",
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_testpackage_js_loaded_by_map_page(self):
        """
        Normal case: map.html references /api/testpackage/ as a <script>.
        This is the hash function the frontend loads to authenticate API calls.
        """
        r = get("/map.html")
        assert "testpackage" in r.text.lower()

    def test_route_api_reachable(self):
        """Normal case: routing API endpoint responds (used by routing mode)."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/route/?start=1&end=100",
            timeout=TIMEOUT, verify=False
        )
        # Should get a response (200 with data or 200 with empty collection)
        assert r.status_code in (200, 400, 422)


# ─────────────────────────────────────────────────────────────
# TC-F06 Input validation / negative cases (user perspective)
# ─────────────────────────────────────────────────────────────

class TestInputValidationUserPerspective:
    """
    TC-F06 – What a user sees when they submit invalid input.
    These replicate what the browser would send to the API.
    """

    def test_api_rejects_non_integer_route_node(self):
        """Error case: user enters text in routing start field."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/route/",
            params={"start": "invalid", "end": 100},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_api_rejects_missing_route_end(self):
        """Error case: user provides only one routing node."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/route/",
            params={"start": 1},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_village_api_rejects_missing_auth(self):
        """Error case: user somehow accesses village endpoint without auth."""
        r = requests.get(
            "https://ailurophile.xyz:2546/api/village/",
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 401

    def test_post_village_url_with_missing_fields(self):
        """Error case: form submitted with missing required fields."""
        r = requests.post(
            "https://ailurophile.xyz:2546/api/post/village_url/",
            json={"village_name": "Test"},
            timeout=TIMEOUT, verify=False
        )
        assert r.status_code == 422

    def test_nonexistent_page_shows_error(self):
        """Error case: user navigates to a page that doesn't exist."""
        r = get("/nonexistent-page.html")
        assert r.status_code == 404

    def test_deep_nonexistent_path_returns_error(self):
        """Error case: deep invalid path → error response."""
        r = get("/some/deep/path/that/does/not/exist")
        assert r.status_code in (404, 403)


# ─────────────────────────────────────────────────────────────
# TC-F07 Performance / response time
# ─────────────────────────────────────────────────────────────

class TestResponseTime:
    """TC-F07 – Page and API response times are within acceptable bounds."""

    def test_homepage_loads_within_5_seconds(self):
        """Normal case: homepage responds in under 5 seconds."""
        start = time.time()
        r = get("/")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 5.0, f"Homepage took {elapsed:.2f}s"

    def test_village_names_api_responds_within_10_seconds(self):
        """Normal case: village names API (on first cold call) responds within 10s."""
        start = time.time()
        r = requests.get(
            "https://ailurophile.xyz:2546/api/village_names/",
            timeout=TIMEOUT, verify=False
        )
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 10.0, f"Village names API took {elapsed:.2f}s"

    def test_static_js_serves_quickly(self):
        """Normal case: static JS file serves within 3 seconds."""
        start = time.time()
        r = get("/index.js")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 3.0, f"index.js took {elapsed:.2f}s"
