"""
test_unit_backend.py
====================
Unit tests for the KHT API backend.
Imports and tests the REAL source files:
  - api_provider2.py
  - postgreSQL.py
  - village_url_model.py

External dependencies are mocked:
  - psycopg2.connect  — no real DB needed
  - execjs            — no Node.js needed for most tests
  - psycopg2 routing  — get_route DB calls patched per test

Group Members: [Fill in your names]
Project: KHT Mae Hong Son Map API

Run with:
    pytest test_unit_backend.py -v --tb=short
Coverage:
    pytest test_unit_backend.py --cov=. --cov-report=term-missing

SETUP: postgreSQL.py, api_provider2.py, village_url_model.py and
       testpackage.js must be in the same directory as this test file.
"""

import os
import sys
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError

# ─────────────────────────────────────────────────────────────
# 0. Point to Src/KHT_API/ relative to this file's location so
#    all relative paths in api_provider2.py (e.g. testpackage.js)
#    resolve correctly regardless of where pytest is invoked from.
# ─────────────────────────────────────────────────────────────
_THIS_DIR   = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR    = os.path.join(_THIS_DIR, "Src", "KHT_API")
os.chdir(_SRC_DIR)
sys.path.insert(0, _SRC_DIR)

# ─────────────────────────────────────────────────────────────
# 1. Mock execjs before any import so api_provider2 loads cleanly
# ─────────────────────────────────────────────────────────────
_mock_execjs = Mock()
_mock_execjs.compile.return_value = Mock(eval=Mock(return_value="valid_hash"))
sys.modules["execjs"] = _mock_execjs

# ─────────────────────────────────────────────────────────────
# 2. Mock psycopg2.connect before postgreSQL.py is imported
# ─────────────────────────────────────────────────────────────
_mock_cursor = Mock()
_mock_cursor.mogrify.return_value = b"SELECT ..."
_mock_cursor.fetchall.return_value = []
_mock_cursor.fetchone.return_value = None
_mock_cursor.rowcount = 0
_mock_cursor.description = []

_mock_conn = Mock()
_mock_conn.cursor.return_value = _mock_cursor

_connect_patcher = patch("psycopg2.connect", return_value=_mock_conn)
_connect_patcher.start()

# ─────────────────────────────────────────────────────────────
# 3. Now safe to import real source files
# ─────────────────────────────────────────────────────────────
import postgreSQL
import api_provider2
from api_provider2 import app, get_route, check_valid
from village_url_model import village_url_data
from fastapi.testclient import TestClient

# ─────────────────────────────────────────────────────────────
# Shared test data
# ─────────────────────────────────────────────────────────────

EMPTY_FC = {"type": "FeatureCollection", "features": []}
SAMPLE_FC = {"type": "FeatureCollection", "features": [
    {"type": "Feature", "geometry": None, "properties": {"name": "test"}}
]}
SAMPLE_JSON_FC = {"type": "FeatureCollection", "features": [
    {"properties": {"project_name": "WASH 2022"}}
]}
SAMPLE_NAMES    = ["Village A", "Village B"]
SAMPLE_NAMES_TH = ["หมู่บ้าน เอ", "หมู่บ้าน บี"]
SAMPLE_ROUTE    = {"type": "FeatureCollection", "features": [
    {"type": "Feature",
     "geometry": {"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]},
     "properties": {}}
]}

# ─────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """TestClient using the real FastAPI app from api_provider2.py."""
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def auth_client():
    """TestClient with check_valid patched to always pass."""
    with patch.object(api_provider2, "check_valid", return_value=True):
        with patch.object(postgreSQL, "get_village",                  return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_village_project_by_year",  return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_village_by_distance",      return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_village_by_road_distance", return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_village_by_project_type",  return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_village_names",            return_value=SAMPLE_NAMES), \
             patch.object(postgreSQL, "get_village_names_th",         return_value=SAMPLE_NAMES_TH), \
             patch.object(postgreSQL, "get_project",                  return_value=SAMPLE_JSON_FC), \
             patch.object(postgreSQL, "get_project_donor",            return_value=SAMPLE_JSON_FC), \
             patch.object(postgreSQL, "get_school",                   return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_hospital",                 return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_mhs_districts",            return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_mhs_subdistricts",         return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_mhs_roads",                return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_mhs_water_areas",          return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "get_mhs_water_lines",          return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "insert_village_url",           return_value="Success"), \
             patch.object(postgreSQL, "count_user",                   return_value=None):
            yield TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def unauth_client():
    """TestClient with check_valid patched to always fail."""
    with patch.object(api_provider2, "check_valid", return_value=False), \
         patch.object(postgreSQL, "get_village_names",    return_value=SAMPLE_NAMES), \
         patch.object(postgreSQL, "get_village_names_th", return_value=SAMPLE_NAMES_TH), \
         patch.object(postgreSQL, "get_mhs_water_lines",  return_value=SAMPLE_FC):
        yield TestClient(app, raise_server_exceptions=False)


# ═════════════════════════════════════════════════════════════
# SECTION 1 — Pure logic functions in api_provider2.py
# ═════════════════════════════════════════════════════════════

class TestGetRouteTableSelection:
    """get_route() — table name selection based on use_elevation flag."""

    def test_no_elevation_uses_standard_tables(self):
        """Normal: use_elevation=False → new_nodes / new_edges used in query."""
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            get_route(1, 100, use_elevation=False)

        query = mock_cur.execute.call_args[0][0]
        assert "new_nodes" in query
        assert "new_edges" in query
        assert "elevation_nodes" not in query
        assert "elevation_edges" not in query

    def test_elevation_uses_elevation_tables(self):
        """Normal: use_elevation=True → elevation_nodes / elevation_edges used."""
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            get_route(1, 100, use_elevation=True)

        query = mock_cur.execute.call_args[0][0]
        assert "elevation_nodes" in query
        assert "elevation_edges" in query
        assert "new_nodes" not in query
        assert "new_edges" not in query

    def test_same_start_and_end_node_still_queries(self):
        """Edge: start and end node are the same — query still executes."""
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None

        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            result = get_route(1, 1, use_elevation=False)

        assert mock_cur.execute.called
        assert "type" in result or "error" in result


class TestAssembleRouteResponse:
    """get_route() — GeoJSON assembly from DB result."""

    def _run_get_route(self, db_result):
        """Helper: run get_route with a mocked fetchone return value."""
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = db_result
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            return get_route(1, 100)

    def test_none_result_returns_empty_feature_collection(self):
        """Edge: DB returns None → empty FeatureCollection."""
        result = self._run_get_route((None,))
        assert result["type"] == "FeatureCollection"
        assert result["features"] == []

    def test_geometry_dicts_wrapped_in_features(self):
        """Normal: geometry dicts → each wrapped as a GeoJSON Feature."""
        geom = {"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]}
        result = self._run_get_route(([geom],))
        assert len(result["features"]) == 1
        assert result["features"][0]["type"] == "Feature"
        assert result["features"][0]["geometry"] == geom
        assert result["features"][0]["properties"] == {}

    def test_geometry_strings_parsed_correctly(self):
        """Normal: JSON-string geometries parsed into dicts."""
        geom = {"type": "LineString", "coordinates": [[97.8, 18.7]]}
        result = self._run_get_route(([json.dumps(geom)],))
        assert result["features"][0]["geometry"] == geom

    def test_aggregated_as_json_string(self):
        """Edge: entire result is a JSON string, not a list."""
        geoms = [{"type": "LineString", "coordinates": [[97.0, 18.0]]}]
        result = self._run_get_route((json.dumps(geoms),))
        assert len(result["features"]) == 1

    def test_multiple_segments(self):
        """Normal: multiple geometry segments → multiple features."""
        geoms = [
            {"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]},
            {"type": "LineString", "coordinates": [[97.9, 18.8], [98.0, 18.9]]},
        ]
        result = self._run_get_route((geoms,))
        assert len(result["features"]) == 2

    def test_db_error_returns_error_dict(self):
        """Error: psycopg2.Error raised → returns error dict, no crash."""
        import psycopg2 as real_psycopg2
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.execute.side_effect = real_psycopg2.Error("DB down")
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            result = get_route(1, 100)
        assert "error" in result


class TestVillageFilterRouting:
    """pull_village_data() — which postgreSQL function gets called per filter."""

    def _call(self, **params):
        with patch.object(api_provider2, "check_valid", return_value=True):
            with patch.object(postgreSQL, "get_village",                  return_value=SAMPLE_FC) as m_all, \
                 patch.object(postgreSQL, "get_village_project_by_year",  return_value=SAMPLE_FC) as m_year, \
                 patch.object(postgreSQL, "get_village_by_distance",      return_value=SAMPLE_FC) as m_dist, \
                 patch.object(postgreSQL, "get_village_by_road_distance", return_value=SAMPLE_FC) as m_road, \
                 patch.object(postgreSQL, "get_village_by_project_type",  return_value=SAMPLE_FC) as m_proj:
                c = TestClient(app, raise_server_exceptions=False)
                c.get("/api/village/", params=params)
                return {
                    "get_village":                  m_all.called,
                    "get_village_project_by_year":  m_year.called,
                    "get_village_by_distance":      m_dist.called,
                    "get_village_by_road_distance": m_road.called,
                    "get_village_by_project_type":  m_proj.called,
                }

    def test_no_filter_calls_get_village(self):
        calls = self._call()
        assert calls["get_village"] is True

    def test_year_filter_calls_get_village_project_by_year(self):
        calls = self._call(year="2022")
        assert calls["get_village_project_by_year"] is True
        assert calls["get_village"] is False

    def test_start_end_year_calls_get_village_project_by_year(self):
        calls = self._call(start_year="2020", end_year="2023")
        assert calls["get_village_project_by_year"] is True

    def test_distance_filter_calls_get_village_by_distance(self):
        calls = self._call(distance="5000", facility_type="school")
        assert calls["get_village_by_distance"] is True

    def test_road_distance_calls_get_village_by_road_distance(self):
        calls = self._call(road_distance="10000", facility_type="hospital")
        assert calls["get_village_by_road_distance"] is True

    def test_project_type_calls_get_village_by_project_type(self):
        calls = self._call(project_type="WASH")
        assert calls["get_village_by_project_type"] is True

    def test_year_takes_priority_over_project_type(self):
        """Edge: year + project_type → year branch wins."""
        calls = self._call(year="2021", project_type="WASH")
        assert calls["get_village_project_by_year"] is True
        assert calls["get_village_by_project_type"] is False

    def test_start_year_without_end_year_calls_get_village(self):
        """Edge: only start_year, no end_year → falls through to get_village."""
        calls = self._call(start_year="2020")
        assert calls["get_village"] is True
        assert calls["get_village_project_by_year"] is False

    def test_facility_type_without_distance_returns_400(self, auth_client):
        """Error: facility_type provided without distance → HTTP 400."""
        assert auth_client.get("/api/village/?facility_type=school").status_code == 400


class TestCheckValid:
    """check_valid() — HMAC-style key comparison."""

    def _call(self, message, key, hash_return):
        """Patches execjs.compile so JS eval returns a controlled hash value."""
        mock_ctx = Mock()
        mock_ctx.eval.return_value = hash_return
        _mock_execjs.compile.return_value = mock_ctx
        return check_valid(message, key)

    def test_correct_key_returns_true(self):
        """Normal: execjs returns the same hash as the key → True."""
        assert self._call("12-30-00", "abc123", "abc123") is True

    def test_wrong_key_returns_false(self):
        """Normal: key does not match computed hash → False."""
        assert self._call("12-30-00", "wrongkey", "abc123") is False

    def test_empty_key_returns_false(self):
        """Edge: empty key never matches a real hash → False."""
        assert self._call("12-30-00", "", "abc123") is False

    def test_case_sensitive(self):
        """Edge: hash comparison is case-sensitive."""
        assert self._call("12-30-00", "abc123", "ABC123") is False


class TestVillageUrlModel:
    """village_url_data Pydantic model validation."""

    def test_valid_model(self):
        obj = village_url_data(
            village_name="Village A", url="https://example.com",
            image_url="https://example.com/img.jpg",
            article_title="Test", posted_date="2024-01-01", password="pw"
        )
        assert obj.village_name == "Village A"

    def test_optional_fields_default_to_none(self):
        obj = village_url_data(village_name="Village A", url="https://example.com",
                               image_url="https://example.com/img.jpg", password="pw")
        assert obj.article_title is None
        assert obj.posted_date is None

    def test_missing_required_field_raises(self):
        with pytest.raises(ValidationError):
            village_url_data(village_name="Village A",
                             image_url="https://example.com/img.jpg", password="pw")

    def test_missing_password_raises(self):
        with pytest.raises(ValidationError):
            village_url_data(village_name="Village A", url="https://example.com",
                             image_url="https://example.com/img.jpg")

    def test_missing_image_url_raises(self):
        with pytest.raises(ValidationError):
            village_url_data(village_name="Village A", url="https://example.com",
                             password="pw")

    def test_empty_string_village_name_is_accepted(self):
        """Edge: empty string is a valid value for village_name (Pydantic allows it)."""
        obj = village_url_data(village_name="", url="https://example.com",
                               image_url="https://example.com/img.jpg", password="pw")
        assert obj.village_name == ""


# ═════════════════════════════════════════════════════════════
# SECTION 2 — postgreSQL.py query functions
# ═════════════════════════════════════════════════════════════

class TestGetVillageNames:
    def test_returns_list(self):
        cursor = Mock()
        cursor.description = [("village_name",)]
        cursor.fetchall.return_value = [("Village A",), ("Village B",)]
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_names() == ["Village A", "Village B"]

    def test_empty_table(self):
        cursor = Mock()
        cursor.description = [("village_name",)]
        cursor.fetchall.return_value = []
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_names() == []

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.execute.side_effect = Exception("DB error")
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            assert postgreSQL.get_village_names() is None
        conn.rollback.assert_called_once()


class TestGetVillageNamesTh:
    def test_returns_thai_list(self):
        cursor = Mock()
        cursor.description = [("village_name_th",)]
        cursor.fetchall.return_value = [("หมู่บ้าน เอ",), ("หมู่บ้าน บี",)]
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_names_th() == ["หมู่บ้าน เอ", "หมู่บ้าน บี"]

    def test_empty_table(self):
        cursor = Mock()
        cursor.description = [("village_name_th",)]
        cursor.fetchall.return_value = []
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_names_th() == []

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.execute.side_effect = Exception("timeout")
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            assert postgreSQL.get_village_names_th() is None
        conn.rollback.assert_called_once()


class TestGetVillage:
    def test_all_villages_calls_query_to_geojson(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village() == SAMPLE_FC
        m.assert_called_once()

    def test_specific_village_calls_query_to_geojson(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village("some-uuid") == SAMPLE_FC
        m.assert_called_once()

    def test_db_error_raises_and_rolls_back(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("DB down")):
            with pytest.raises(Exception, match="DB down"):
                postgreSQL.get_village()
        conn.rollback.assert_called_once()


class TestGetVillageProjectByYear:
    def test_single_year_calls_query_to_geojson(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village_project_by_year(year="2022") == SAMPLE_FC
        m.assert_called_once()

    def test_year_range(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_project_by_year(start_year="2020", end_year="2023") == SAMPLE_FC

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.mogrify.side_effect = Exception("DB error")
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            assert postgreSQL.get_village_project_by_year(year="2022") is None
        conn.rollback.assert_called_once()


class TestGetVillageByDistance:
    def test_converts_km_to_metres(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            postgreSQL.get_village_by_distance(distance="5", facility_type="hospital")
        assert cursor.mogrify.call_args[0][1] == (5000.0,)

    def test_returns_geojson(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"SELECT ..."
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_by_distance(distance="5", facility_type="school") == SAMPLE_FC

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.mogrify.side_effect = Exception("DB error")
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            assert postgreSQL.get_village_by_distance(distance="5", facility_type="hospital") is None
        conn.rollback.assert_called_once()


class TestGetVillageByRoadDistance:
    def test_returns_none(self):
        """Stub — not yet implemented."""
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_by_road_distance(road_distance="10", facility_type="hospital") is None

    def test_zero_distance_returns_none(self):
        """Edge: zero road distance still returns None (stub behaviour)."""
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_by_road_distance(road_distance="0", facility_type="school") is None

    def test_empty_facility_type_returns_none(self):
        """Error: empty facility_type still returns None (stub behaviour)."""
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()):
            assert postgreSQL.get_village_by_road_distance(road_distance="5", facility_type="") is None


class TestGetVillageByProjectType:
    def test_returns_geojson(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_by_project_type(project_type="WASH") == SAMPLE_FC

    def test_empty_result(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_village_by_project_type(project_type="Unknown") == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_village_by_project_type(project_type="WASH") is None
        conn.rollback.assert_called_once()


class TestGetProject:
    def test_no_village_id(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_json", return_value=SAMPLE_JSON_FC) as m:
            assert postgreSQL.get_project() == SAMPLE_JSON_FC
        m.assert_called_once()

    def test_with_village_id(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project(village_id="some-uuid") == SAMPLE_JSON_FC

    def test_with_year_range(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project(start_year="2020", end_year="2023") == SAMPLE_JSON_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_json", side_effect=Exception("error")):
            assert postgreSQL.get_project() is None
        conn.rollback.assert_called_once()


class TestGetProjectDonor:
    def test_returns_json(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project_donor(project_id="some-uuid") == SAMPLE_JSON_FC

    def test_empty_project_id(self):
        cursor = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_json", return_value=EMPTY_FC):
            assert postgreSQL.get_project_donor() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_json", side_effect=Exception("error")):
            assert postgreSQL.get_project_donor(project_id="bad") is None
        conn.rollback.assert_called_once()


class TestGetHospital:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_hospital() == SAMPLE_FC
        m.assert_called_once()

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_hospital() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_hospital() is None
        conn.rollback.assert_called_once()


class TestGetSchool:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_school() == SAMPLE_FC
        m.assert_called_once()

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_school() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("timeout")):
            assert postgreSQL.get_school() is None
        conn.rollback.assert_called_once()


class TestGetMhsDistricts:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_districts() == SAMPLE_FC

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_districts() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_districts() is None
        conn.rollback.assert_called_once()


class TestGetMhsSubdistricts:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_subdistricts() == SAMPLE_FC

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_subdistricts() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_subdistricts() is None
        conn.rollback.assert_called_once()


class TestGetMhsRoads:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_roads() == SAMPLE_FC

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_roads() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_roads() is None
        conn.rollback.assert_called_once()


class TestGetMhsWaterAreas:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_water_areas() == SAMPLE_FC

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_water_areas() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_water_areas() is None
        conn.rollback.assert_called_once()


class TestGetMhsWaterLines:
    def test_returns_geojson(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_water_lines() == SAMPLE_FC

    def test_empty_table(self):
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", Mock()), \
             patch.object(postgreSQL, "query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_water_lines() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch.object(postgreSQL, "cursor", Mock()), \
             patch.object(postgreSQL, "connection", conn), \
             patch.object(postgreSQL, "query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_water_lines() is None
        conn.rollback.assert_called_once()


class TestInsertVillageUrl:
    def _make_data(self, password="correct_password"):
        return village_url_data(
            village_name="Village A", url="https://example.com/article",
            image_url="https://example.com/img.jpg", article_title="WASH Project",
            posted_date="2024-01-15", password=password
        )

    def test_correct_password_village_found_returns_success(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.rowcount = 1
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Success"
        conn.commit.assert_called_once()

    def test_correct_password_village_not_found(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.rowcount = 0
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Failed"
        assert "not found" in result["message"]

    def test_wrong_password_returns_failed(self):
        cursor = Mock()
        cursor.fetchone.return_value = (hash("correct_password"),)
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", Mock()):
            result = postgreSQL.insert_village_url(self._make_data("wrong_password"))
        assert result["status"] == "Failed"
        assert "password" in result.get("password_message", "").lower()

    def test_insert_exception_returns_failed_and_rolls_back(self):
        cursor = Mock()
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.mogrify.return_value = b"INSERT ..."
        cursor.execute.side_effect = [None, Exception("insert failed")]
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Failed"
        conn.rollback.assert_called()


class TestCountUser:
    def test_valid_ip_commits(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            postgreSQL.count_user("192.168.1.1")
        conn.commit.assert_called_once()

    def test_empty_ip_still_commits(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            postgreSQL.count_user("")
        conn.commit.assert_called_once()

    def test_db_error_triggers_rollback(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        cursor.execute.side_effect = Exception("write failed")
        conn = Mock()
        with patch.object(postgreSQL, "cursor", cursor), \
             patch.object(postgreSQL, "connection", conn):
            postgreSQL.count_user("10.0.0.1")
        conn.rollback.assert_called_once()


# ═════════════════════════════════════════════════════════════
# SECTION 3 — FastAPI endpoints (real app from api_provider2.py)
# ═════════════════════════════════════════════════════════════

class TestRootEndpoint:
    def test_returns_200(self, client):
        assert client.get("/").status_code == 200

    def test_returns_working_message(self, client):
        assert client.get("/").json() == {"message": "The data hosting is working!"}

    def test_post_not_allowed(self, client):
        """Error: POST method not allowed on root endpoint."""
        assert client.post("/").status_code == 405

    def test_message_key_not_status(self, client):
        """Edge: response uses 'message' key, not 'status'."""
        data = client.get("/").json()
        assert "message" in data
        assert "status" not in data


class TestVillageEndpoint:
    def test_no_auth_returns_401(self, unauth_client):
        assert unauth_client.get("/api/village/").status_code == 401

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/village/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/village/").json()["type"] == "FeatureCollection"

    def test_year_filter(self, auth_client):
        assert auth_client.get("/api/village/?year=2022").status_code == 200

    def test_start_end_year_filter(self, auth_client):
        assert auth_client.get("/api/village/?start_year=2020&end_year=2023").status_code == 200

    def test_project_type_filter(self, auth_client):
        assert auth_client.get("/api/village/?project_type=WASH").status_code == 200

    def test_distance_filter(self, auth_client):
        assert auth_client.get("/api/village/?distance=5000&facility_type=school").status_code == 200

    def test_road_distance_filter(self, auth_client):
        assert auth_client.get("/api/village/?road_distance=10000&facility_type=hospital").status_code == 200

    def test_facility_without_distance_returns_400(self, auth_client):
        assert auth_client.get("/api/village/?facility_type=school").status_code == 400

    def test_none_result_returns_empty_fc(self):
        with patch.object(api_provider2, "check_valid", return_value=True), \
             patch.object(postgreSQL, "get_village", return_value=None):
            c = TestClient(app, raise_server_exceptions=False)
            assert c.get("/api/village/").json() == EMPTY_FC


class TestVillageNamesEndpoint:
    def test_returns_200(self, client):
        with patch.object(postgreSQL, "get_village_names", return_value=SAMPLE_NAMES):
            assert client.get("/api/village_names/").status_code == 200

    def test_returns_list(self, client):
        with patch.object(postgreSQL, "get_village_names", return_value=SAMPLE_NAMES):
            assert client.get("/api/village_names/").json() == SAMPLE_NAMES


    def test_no_auth_required(self, unauth_client):
        assert unauth_client.get("/api/village_names/").status_code == 200

    def test_empty_table_returns_empty_list(self, client):
        """Edge: no villages in DB → returns empty list, not an error."""
        with patch.object(postgreSQL, "get_village_names", return_value=[]):
            assert client.get("/api/village_names/").json() == []

    def test_db_error_returns_500(self, client):
        """Error: DB failure → endpoint returns 500."""
        with patch.object(postgreSQL, "get_village_names", side_effect=Exception("DB down")):
            assert client.get("/api/village_names/").status_code == 500


class TestVillageNamesTHEndpoint:
    def test_returns_200(self, client):
        with patch.object(postgreSQL, "get_village_names_th", return_value=SAMPLE_NAMES_TH):
            assert client.get("/api/village_names_th/").status_code == 200

    def test_returns_thai_names(self, client):
        with patch.object(postgreSQL, "get_village_names_th", return_value=SAMPLE_NAMES_TH):
            assert client.get("/api/village_names_th/").json() == SAMPLE_NAMES_TH

    def test_no_auth_required(self, unauth_client):
        assert unauth_client.get("/api/village_names_th/").status_code == 200

    def test_empty_table_returns_empty_list(self, client):
        """Edge: no villages → returns empty list."""
        with patch.object(postgreSQL, "get_village_names_th", return_value=[]):
            assert client.get("/api/village_names_th/").json() == []

    def test_db_error_returns_500(self, client):
        """Error: DB failure → endpoint returns 500."""
        with patch.object(postgreSQL, "get_village_names_th", side_effect=Exception("DB down")):
            assert client.get("/api/village_names_th/").status_code == 500


class TestProjectEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/project/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/project/").status_code == 200

    def test_village_id_filter(self, auth_client):
        assert auth_client.get("/api/project/?village_id=42").status_code == 200

    def test_year_range_filter(self, auth_client):
        assert auth_client.get("/api/project/?start_year=2020&end_year=2023").status_code == 200


class TestProjectDonorEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/project_donor/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/project_donor/").status_code == 200

    def test_project_id_filter(self, auth_client):
        assert auth_client.get("/api/project_donor/?project_id=10").status_code == 200


class TestSchoolEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/school/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/school/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/school/").json()["type"] == "FeatureCollection"


class TestHospitalEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/hospital/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/hospital/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/hospital/").json()["type"] == "FeatureCollection"


class TestMhsDistrictsEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/mhs_districts/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_districts/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_districts/").json()["type"] == "FeatureCollection"


class TestMhsSubdistrictsEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/mhs_subdistricts/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_subdistricts/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_subdistricts/").json()["type"] == "FeatureCollection"


class TestMhsRoadsEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/mhs_roads/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_roads/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_roads/").json()["type"] == "FeatureCollection"

    def test_count_user_is_called(self):
        with patch.object(api_provider2, "check_valid", return_value=True), \
             patch.object(postgreSQL, "get_mhs_roads", return_value=SAMPLE_FC), \
             patch.object(postgreSQL, "count_user", return_value=None) as m:
            TestClient(app, raise_server_exceptions=False).get("/api/mhs_roads/")
        m.assert_called_once()


class TestMhsWaterAreasEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/mhs_water_areas/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_water_areas/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_water_areas/").json()["type"] == "FeatureCollection"


class TestMhsWaterLinesEndpoint:
    def test_no_auth_required(self, unauth_client):
        """Normal: water lines is a public endpoint — no auth needed."""
        assert unauth_client.get("/api/mhs_water_lines").status_code == 200

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_water_lines").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_water_lines").json()["type"] == "FeatureCollection"


class TestPostVillageUrlEndpoint:
    VALID_PAYLOAD = {
        "village_name": "Village A", "url": "https://example.com/article",
        "image_url": "https://example.com/img.jpg", "article_title": "WASH Project",
        "posted_date": "2024-01-15", "password": "secret"
    }

    def test_valid_payload_returns_200(self, auth_client):
        assert auth_client.post("/api/post/village_url/", json=self.VALID_PAYLOAD).status_code == 200

    def test_valid_payload_returns_success_message(self, auth_client):
        assert auth_client.post("/api/post/village_url/", json=self.VALID_PAYLOAD).json() == {"message": "Success"}

    def test_missing_url_returns_422(self, auth_client):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "url"}
        assert auth_client.post("/api/post/village_url/", json=payload).status_code == 422

    def test_missing_image_url_returns_422(self, auth_client):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "image_url"}
        assert auth_client.post("/api/post/village_url/", json=payload).status_code == 422

    def test_missing_password_returns_422(self, auth_client):
        payload = {k: v for k, v in self.VALID_PAYLOAD.items() if k != "password"}
        assert auth_client.post("/api/post/village_url/", json=payload).status_code == 422

    def test_optional_fields_can_be_omitted(self, auth_client):
        payload = {"village_name": "Village A", "url": "https://example.com",
                   "image_url": "https://example.com/img.jpg", "password": "pw"}
        assert auth_client.post("/api/post/village_url/", json=payload).status_code == 200

    def test_empty_body_returns_422(self, auth_client):
        assert auth_client.post("/api/post/village_url/").status_code == 422

    def test_get_not_allowed(self, client):
        assert client.get("/api/post/village_url/").status_code == 405


class TestRouteEndpoint:
    def test_valid_nodes_returns_200(self, client):
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            assert client.get("/api/route/?start=1&end=100").status_code == 200

    def test_returns_feature_collection(self, client):
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            assert client.get("/api/route/?start=1&end=100").json()["type"] == "FeatureCollection"

    def test_missing_start_returns_422(self, client):
        assert client.get("/api/route/?end=100").status_code == 422

    def test_missing_end_returns_422(self, client):
        assert client.get("/api/route/?start=1").status_code == 422

    def test_non_integer_start_returns_422(self, client):
        assert client.get("/api/route/?start=abc&end=100").status_code == 422

    def test_use_elevation_flag(self, client):
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            assert client.get("/api/route/?start=1&end=100&use_elevation=1").status_code == 200

    def test_no_auth_required(self, unauth_client):
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = None
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            assert unauth_client.get("/api/route/?start=1&end=100").status_code == 200

    def test_features_have_correct_structure(self, client):
        geom = {"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]}
        mock_conn = Mock()
        mock_cur  = Mock()
        mock_conn.cursor.return_value = mock_cur
        mock_cur.fetchone.return_value = ([geom],)
        with patch("api_provider2.psycopg2.connect", return_value=mock_conn):
            data = client.get("/api/route/?start=1&end=100").json()
        for feature in data["features"]:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature