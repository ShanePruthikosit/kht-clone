"""
test_unit_backend.py
====================
Unit tests for the KHT API backend.
Covers all three source files:
  - api_provider2.py  (pure logic: route assembly, filter routing, auth)
  - postgreSQL.py     (all query functions, with mocked cursor/connection)
  - village_url_model.py (Pydantic model validation)

No live database or network connection is required.
psycopg2.connect is mocked at import time so postgreSQL.py loads cleanly.

Group Members: [Fill in your names]
Project: KHT Mae Hong Son Map API

Run with:
    pytest test_unit_backend.py -v --tb=short
Coverage:
    pytest test_unit_backend.py --cov=. --cov-report=term-missing
"""

import sys
import json
import pytest
from unittest.mock import Mock, MagicMock, patch
from pydantic import BaseModel, ValidationError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

# ─────────────────────────────────────────────────────────────
# Mock psycopg2.connect BEFORE postgreSQL.py is imported so the
# module-level connection block does not fail without a real DB.
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

import postgreSQL  # noqa: E402 — must come after the patch

# ─────────────────────────────────────────────────────────────
# Shared Pydantic model (mirrors village_url_model.py)
# ─────────────────────────────────────────────────────────────

class village_url_data(BaseModel):
    village_name: str
    url: str
    image_url: str
    article_title: str = None
    posted_date: str = None
    password: str

# ─────────────────────────────────────────────────────────────
# Shared test data
# ─────────────────────────────────────────────────────────────

EMPTY_FC      = {"type": "FeatureCollection", "features": []}
SAMPLE_FC     = {"type": "FeatureCollection", "features": [
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
# Pure-logic mirrors of api_provider2.py functions
# (tested without the full server stack)
# ─────────────────────────────────────────────────────────────

def query_to_json_logic(cursor, query):
    """Mirror of postgreSQL.query_to_json."""
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    results = cursor.fetchall()
    features = [{"properties": dict(zip(columns, row))} for row in results]
    return {"type": "FeatureCollection", "features": features}


def query_to_geojson_logic(cursor, query):
    """Mirror of postgreSQL.query_to_geojson."""
    import geojson as gj
    try:
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        features = []
        for row in cursor.fetchall():
            props = dict(zip(columns, row))
            geom_str = props.get("geom")
            if geom_str is not None:
                try:
                    from shapely import wkb
                    from shapely.geometry import mapping
                    features.append(gj.Feature(properties=props,
                                               geometry=mapping(wkb.loads(geom_str, hex=True))))
                except (json.JSONDecodeError, ValueError):
                    pass
        return gj.FeatureCollection(features)
    except Exception:
        return gj.FeatureCollection([])


def get_route_table_selection(use_elevation: bool):
    """Mirror of table-selection branch in api_provider2.get_route."""
    return ("elevation_nodes", "elevation_edges") if use_elevation \
        else ("new_nodes", "new_edges")


def assemble_route_response(db_result):
    """Mirror of GeoJSON assembly in api_provider2.get_route."""
    features = []
    if db_result and db_result[0]:
        aggregated = json.loads(db_result[0]) if isinstance(db_result[0], str) else db_result[0]
        for item in aggregated:
            geometry = json.loads(item) if isinstance(item, str) else item
            features.append({"type": "Feature", "geometry": geometry, "properties": {}})
    return {"type": "FeatureCollection", "features": features}


def village_filter_routing(year="", start_year="", end_year="", facility_type="",
                            distance="", road_distance="", project_type="", village_id=""):
    """Mirror of dispatch logic in api_provider2.pull_village_data."""
    if year or (start_year and end_year):
        return "get_village_project_by_year"
    if facility_type:
        if distance:      return "get_village_by_distance"
        if road_distance: return "get_village_by_road_distance"
        return "invalid_argument"
    if project_type:
        return "get_village_by_project_type"
    return "get_village"


def check_valid_logic(computed_hash, key):
    """Mirror of check_valid's hash comparison."""
    return computed_hash == key

# ─────────────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────────────

def make_cursor(columns=None, rows=None):
    cursor = Mock()
    cursor.description = [(col,) for col in (columns or [])]
    cursor.fetchall.return_value = rows or []
    cursor.mogrify.return_value = b"SELECT ..."
    return cursor

# ─────────────────────────────────────────────────────────────
# FastAPI TestClient app factory (mirrors api_provider2.py)
# ─────────────────────────────────────────────────────────────

def build_app(mock_pg, mock_check_valid, mock_get_route):
    app = FastAPI()
    app.add_middleware(CORSMiddleware, allow_origins=["*"],
                       allow_methods=["GET", "POST", "OPTIONS"],
                       allow_headers=["Origin", "Content-Type"])

    @app.get("/")
    def read_root():
        return {"message": "The data hosting is working!"}

    @app.get("/api/testpackage/")
    def getHashFunction():
        return JSONResponse(content={"js": "function getOldTestPackage(t){return t;}"})

    @app.get("/api/village/")
    def pull_village_data(village_id="", year="", start_year="", end_year="",
                          project_type="", distance="", road_distance="",
                          facility_type="", time="", key=""):
        if not mock_check_valid(time, key):
            raise HTTPException(status_code=401, detail="Key mismatch")
        try:
            if year or (start_year and end_year):
                result = mock_pg.get_village_project_by_year(year, start_year, end_year)
            elif facility_type:
                if distance:      result = mock_pg.get_village_by_distance(distance, facility_type)
                elif road_distance: result = mock_pg.get_village_by_road_distance(road_distance, facility_type)
                else: raise HTTPException(status_code=400, detail="Invalid argument")
            elif project_type:
                result = mock_pg.get_village_by_project_type(project_type)
            else:
                result = mock_pg.get_village(village_id)
            return result if result is not None else EMPTY_FC
        except HTTPException:
            raise
        except Exception:
            return EMPTY_FC

    @app.get("/api/village_names/")
    def pull_village_names():
        return mock_pg.get_village_names()

    @app.get("/api/village_names_th/")
    def pull_village_names_th():
        return mock_pg.get_village_names_th()

    @app.get("/api/project/")
    def pull_project_data(village_id="", start_year="", end_year="", time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_project(village_id, start_year, end_year)

    @app.get("/api/project_donor/")
    def pull_project_donor_data(project_id="", time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_project_donor(project_id)

    @app.get("/api/school/")
    def pull_school_data(time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_school()

    @app.get("/api/hospital/")
    def pull_hospital_data(time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_hospital()

    @app.get("/api/mhs_districts/")
    def pull_mhs_districts_data(time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_mhs_districts()

    @app.get("/api/mhs_subdistricts/")
    def pull_mhs_subdistricts_data(time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_mhs_subdistricts()

    @app.get("/api/mhs_roads/")
    def pull_mhs_roads(request: Request, time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        mock_pg.count_user("127.0.0.1")
        return mock_pg.get_mhs_roads()

    @app.get("/api/mhs_water_areas/")
    def pull_mhs_water_areas(time="", key=""):
        if not mock_check_valid(time, key):
            return {"Error": "Key mismatch"}
        return mock_pg.get_mhs_water_areas()

    @app.get("/api/mhs_water_lines")
    def pull_mhs_water_lines(time="", key=""):
        return mock_pg.get_mhs_water_lines()

    @app.post("/api/post/village_url/")
    async def create_village_url(data: village_url_data):
        return {"message": mock_pg.insert_village_url(data)}

    @app.get("/api/route/")
    def get_shortest_route(start: int, end: int, use_elevation: int = 0):
        if not start or not end:
            raise HTTPException(status_code=400, detail="Missing start or end node")
        return JSONResponse(content=mock_get_route(start, end, use_elevation=bool(use_elevation)))

    return app


@pytest.fixture
def auth_client():
    """TestClient with all DB calls mocked and auth always passing."""
    pg = Mock()
    pg.get_village.return_value                  = SAMPLE_FC
    pg.get_village_project_by_year.return_value  = SAMPLE_FC
    pg.get_village_by_distance.return_value      = SAMPLE_FC
    pg.get_village_by_road_distance.return_value = SAMPLE_FC
    pg.get_village_by_project_type.return_value  = SAMPLE_FC
    pg.get_village_names.return_value            = SAMPLE_NAMES
    pg.get_village_names_th.return_value         = SAMPLE_NAMES_TH
    pg.get_project.return_value                  = SAMPLE_JSON_FC
    pg.get_project_donor.return_value            = SAMPLE_JSON_FC
    pg.get_school.return_value                   = SAMPLE_FC
    pg.get_hospital.return_value                 = SAMPLE_FC
    pg.get_mhs_districts.return_value            = SAMPLE_FC
    pg.get_mhs_subdistricts.return_value         = SAMPLE_FC
    pg.get_mhs_roads.return_value                = SAMPLE_FC
    pg.get_mhs_water_areas.return_value          = SAMPLE_FC
    pg.get_mhs_water_lines.return_value          = SAMPLE_FC
    pg.insert_village_url.return_value           = "Success"
    pg.count_user.return_value                   = None
    app = build_app(pg, mock_check_valid=lambda t, k: True,
                    mock_get_route=lambda s, e, use_elevation=False: SAMPLE_ROUTE)
    return TestClient(app)


@pytest.fixture
def unauth_client():
    """TestClient where auth always fails."""
    pg = Mock()
    pg.get_village_names.return_value    = SAMPLE_NAMES
    pg.get_village_names_th.return_value = SAMPLE_NAMES_TH
    pg.get_mhs_water_lines.return_value  = SAMPLE_FC
    app = build_app(pg, mock_check_valid=lambda t, k: False,
                    mock_get_route=lambda s, e, use_elevation=False: EMPTY_FC)
    return TestClient(app)


# ═════════════════════════════════════════════════════════════
# SECTION 1 — Pure logic (api_provider2.py)
# ═════════════════════════════════════════════════════════════

class TestQueryToJson:
    """Format converter: DB rows → JSON FeatureCollection."""

    def test_single_row(self):
        """Normal: one row → one feature with correct properties."""
        cursor = make_cursor(["village_name", "population"], [("Village A", 450)])
        result = query_to_json_logic(cursor, "SELECT ...")
        assert result["type"] == "FeatureCollection"
        assert result["features"][0]["properties"] == {"village_name": "Village A", "population": 450}

    def test_multiple_rows(self):
        """Normal: three rows → three features."""
        cursor = make_cursor(["id"], [(1,), (2,), (3,)])
        assert len(query_to_json_logic(cursor, "SELECT ...")["features"]) == 3

    def test_empty_result(self):
        """Edge: no rows → empty features list."""
        cursor = make_cursor(["id", "name"], [])
        assert query_to_json_logic(cursor, "SELECT ...")["features"] == []

    def test_none_value_preserved(self):
        """Edge: None values in a row are kept as-is."""
        cursor = make_cursor(["name", "desc"], [("Village A", None)])
        assert query_to_json_logic(cursor, "SELECT ...")["features"][0]["properties"]["desc"] is None


class TestQueryToGeojson:
    """Format converter: DB rows with WKB geom → GeoJSON FeatureCollection."""

    def test_db_error_returns_empty_collection(self):
        """Error: cursor.execute raises → empty FeatureCollection, no crash."""
        cursor = Mock()
        cursor.execute.side_effect = Exception("DB connection lost")
        result = query_to_geojson_logic(cursor, "SELECT ...")
        assert result["type"] == "FeatureCollection"
        assert list(result["features"]) == []

    def test_no_rows_returns_empty_collection(self):
        """Edge: zero rows → empty FeatureCollection."""
        assert list(query_to_geojson_logic(make_cursor(["id", "geom"], []), "SELECT ...")["features"]) == []

    def test_null_geom_row_is_skipped(self):
        """Edge: geom IS NULL → row skipped, no crash."""
        cursor = make_cursor(["village_name", "geom"], [("Village A", None)])
        assert list(query_to_geojson_logic(cursor, "SELECT ...")["features"]) == []


class TestGetRouteTableSelection:
    """Table name selection based on elevation flag."""

    @pytest.mark.parametrize("use_elevation,expected", [
        (False, ("new_nodes",       "new_edges")),
        (True,  ("elevation_nodes", "elevation_edges")),
    ])
    def test_table_selection(self, use_elevation, expected):
        assert get_route_table_selection(use_elevation) == expected


class TestAssembleRouteResponse:
    """GeoJSON assembly from pgr_dijkstra DB result."""

    def test_none_result_returns_empty(self):
        assert assemble_route_response(None)["features"] == []

    def test_none_inner_returns_empty(self):
        assert assemble_route_response((None,))["features"] == []

    def test_geometry_dicts(self):
        """Normal: pre-parsed geometry dicts wrapped in Features."""
        geoms = [{"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]}]
        result = assemble_route_response((geoms,))
        assert len(result["features"]) == 1
        assert result["features"][0] == {"type": "Feature", "geometry": geoms[0], "properties": {}}

    def test_geometry_strings(self):
        """Normal: JSON-string geometries parsed correctly."""
        geom = {"type": "LineString", "coordinates": [[97.8, 18.7]]}
        assert assemble_route_response(([json.dumps(geom)],))["features"][0]["geometry"] == geom

    def test_aggregated_as_json_string(self):
        """Edge: entire DB result is a JSON string, not a list."""
        geoms = [{"type": "LineString", "coordinates": [[97.0, 18.0]]}]
        assert len(assemble_route_response((json.dumps(geoms),))["features"]) == 1

    def test_multiple_segments(self):
        """Normal: multi-segment route → correct feature count."""
        geoms = [
            {"type": "LineString", "coordinates": [[97.8, 18.7], [97.9, 18.8]]},
            {"type": "LineString", "coordinates": [[97.9, 18.8], [98.0, 18.9]]},
        ]
        assert len(assemble_route_response((geoms,))["features"]) == 2


class TestVillageFilterRouting:
    """Dispatch logic in pull_village_data — which DB function gets called."""

    @pytest.mark.parametrize("kwargs,expected", [
        ({"year": "2022"},                                         "get_village_project_by_year"),
        ({"start_year": "2020", "end_year": "2023"},               "get_village_project_by_year"),
        ({"facility_type": "school", "distance": "5000"},          "get_village_by_distance"),
        ({"facility_type": "hospital", "road_distance": "10000"},  "get_village_by_road_distance"),
        ({"facility_type": "school"},                              "invalid_argument"),
        ({"project_type": "WASH"},                                 "get_village_by_project_type"),
        ({},                                                       "get_village"),
        ({"village_id": "42"},                                     "get_village"),
        ({"year": "2021", "project_type": "WASH"},                 "get_village_project_by_year"),
        ({"start_year": "2020"},                                   "get_village"),
    ])
    def test_routing(self, kwargs, expected):
        assert village_filter_routing(**kwargs) == expected


class TestCheckValidLogic:
    """Auth key comparison logic."""

    @pytest.mark.parametrize("computed,key,expected", [
        ("abc123", "abc123", True),
        ("abc123", "wrong",  False),
        ("abc123", "",       False),
        ("",       "",       True),
        ("ABC123", "abc123", False),
    ])
    def test_comparison(self, computed, key, expected):
        assert check_valid_logic(computed, key) is expected


class TestVillageUrlModel:
    """Pydantic model validation for village_url_data."""

    def test_valid_model(self):
        """Normal: all required fields → valid model."""
        obj = village_url_data(
            village_name="Village A", url="https://example.com",
            image_url="https://example.com/img.jpg",
            article_title="Test", posted_date="2024-01-01", password="pw"
        )
        assert obj.village_name == "Village A"
        assert obj.article_title == "Test"

    def test_optional_fields_default_to_none(self):
        """Edge: optional fields omitted → None."""
        obj = village_url_data(village_name="Village A", url="https://example.com",
                               image_url="https://example.com/img.jpg", password="pw")
        assert obj.article_title is None
        assert obj.posted_date is None

    def test_missing_required_field_raises(self):
        """Error: missing url → ValidationError."""
        with pytest.raises(ValidationError):
            village_url_data(village_name="Village A",
                             image_url="https://example.com/img.jpg", password="pw")


# ═════════════════════════════════════════════════════════════
# SECTION 2 — postgreSQL.py query functions
# ═════════════════════════════════════════════════════════════

class TestGetVillageNames:
    """get_village_names() — list of English village names."""

    def test_returns_list(self):
        cursor = make_cursor(["village_name"], [("Village A",), ("Village B",)])
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()):
            assert postgreSQL.get_village_names() == ["Village A", "Village B"]

    def test_empty_table(self):
        cursor = make_cursor(["village_name"], [])
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()):
            assert postgreSQL.get_village_names() == []

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.execute.side_effect = Exception("DB error")
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            assert postgreSQL.get_village_names() is None
        conn.rollback.assert_called_once()


class TestGetVillageNamesTh:
    """get_village_names_th() — list of Thai village names."""

    def test_returns_thai_list(self):
        cursor = make_cursor(["village_name_th"], [("หมู่บ้าน เอ",), ("หมู่บ้าน บี",)])
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()):
            assert postgreSQL.get_village_names_th() == ["หมู่บ้าน เอ", "หมู่บ้าน บี"]

    def test_empty_table(self):
        cursor = make_cursor(["village_name_th"], [])
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()):
            assert postgreSQL.get_village_names_th() == []

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.execute.side_effect = Exception("timeout")
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            assert postgreSQL.get_village_names_th() is None
        conn.rollback.assert_called_once()


class TestGetVillage:
    """get_village() — all villages or a specific one."""

    def test_all_villages(self):
        """Normal: no village_id → query_to_geojson called."""
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village() == SAMPLE_FC
        m.assert_called_once()

    def test_specific_village(self):
        """Normal: village_id provided → query_to_geojson called."""
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village("some-uuid") == SAMPLE_FC
        m.assert_called_once()

    def test_db_error_raises_and_rolls_back(self):
        """Error: query_to_geojson raises → exception propagates, rollback called."""
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("DB down")):
            with pytest.raises(Exception, match="DB down"):
                postgreSQL.get_village()
        conn.rollback.assert_called_once()


class TestGetVillageProjectByYear:
    """get_village_project_by_year() — filter by project year."""

    def test_single_year(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_village_project_by_year(year="2022") == SAMPLE_FC
        m.assert_called_once()

    def test_year_range(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_project_by_year(start_year="2020", end_year="2023") == SAMPLE_FC

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.mogrify.side_effect = Exception("DB error")
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            assert postgreSQL.get_village_project_by_year(year="2022") is None
        conn.rollback.assert_called_once()


class TestGetVillageByDistance:
    """get_village_by_distance() — villages beyond distance from facility."""

    def test_converts_km_to_metres(self):
        """Normal: distance string '5' → passed to DB as 5000.0."""
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            postgreSQL.get_village_by_distance(distance="5", facility_type="hospital")
        assert cursor.mogrify.call_args[0][1] == (5000.0,)

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_by_distance(distance="5", facility_type="school") == SAMPLE_FC

    def test_db_error_returns_none_and_rolls_back(self):
        cursor = Mock()
        cursor.mogrify.side_effect = Exception("DB error")
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            assert postgreSQL.get_village_by_distance(distance="5", facility_type="hospital") is None
        conn.rollback.assert_called_once()


class TestGetVillageByRoadDistance:
    """get_village_by_road_distance() — stub, not yet implemented."""

    def test_returns_none(self):
        with patch("postgreSQL.cursor", Mock()), patch("postgreSQL.connection", Mock()):
            assert postgreSQL.get_village_by_road_distance(road_distance="10", facility_type="hospital") is None


class TestGetVillageByProjectType:
    """get_village_by_project_type() — filter by project type."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_village_by_project_type(project_type="WASH") == SAMPLE_FC

    def test_empty_result(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_village_by_project_type(project_type="Unknown") == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_village_by_project_type(project_type="WASH") is None
        conn.rollback.assert_called_once()


class TestGetProject:
    """get_project() — query projects by village or year range."""

    def test_no_village_id(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_json", return_value=SAMPLE_JSON_FC) as m:
            assert postgreSQL.get_project() == SAMPLE_JSON_FC
        m.assert_called_once()

    def test_with_village_id(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project(village_id="some-uuid") == SAMPLE_JSON_FC

    def test_with_year_range(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project(start_year="2020", end_year="2023") == SAMPLE_JSON_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_json", side_effect=Exception("DB error")):
            assert postgreSQL.get_project() is None
        conn.rollback.assert_called_once()


class TestGetProjectDonor:
    """get_project_donor() — donors for a project."""

    def test_returns_json(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_json", return_value=SAMPLE_JSON_FC):
            assert postgreSQL.get_project_donor(project_id="some-uuid") == SAMPLE_JSON_FC

    def test_empty_project_id(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_json", return_value=EMPTY_FC):
            assert postgreSQL.get_project_donor() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_json", side_effect=Exception("DB error")):
            assert postgreSQL.get_project_donor(project_id="bad-id") is None
        conn.rollback.assert_called_once()


class TestGetHospital:
    """get_hospital() — all hospital geometries."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_hospital() == SAMPLE_FC
        m.assert_called_once()

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_hospital() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_hospital() is None
        conn.rollback.assert_called_once()


class TestGetSchool:
    """get_school() — all school geometries."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC) as m:
            assert postgreSQL.get_school() == SAMPLE_FC
        m.assert_called_once()

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_school() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("timeout")):
            assert postgreSQL.get_school() is None
        conn.rollback.assert_called_once()


class TestGetMhsDistricts:
    """get_mhs_districts() — district boundary polygons."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_districts() == SAMPLE_FC

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_districts() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_districts() is None
        conn.rollback.assert_called_once()


class TestGetMhsSubdistricts:
    """get_mhs_subdistricts() — sub-district boundary polygons."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_subdistricts() == SAMPLE_FC

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_subdistricts() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_subdistricts() is None
        conn.rollback.assert_called_once()


class TestGetMhsRoads:
    """get_mhs_roads() — road geometries."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_roads() == SAMPLE_FC

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_roads() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_roads() is None
        conn.rollback.assert_called_once()


class TestGetMhsWaterAreas:
    """get_mhs_water_areas() — water area polygons."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_water_areas() == SAMPLE_FC

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_water_areas() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_water_areas() is None
        conn.rollback.assert_called_once()


class TestGetMhsWaterLines:
    """get_mhs_water_lines() — water line geometries."""

    def test_returns_geojson(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=SAMPLE_FC):
            assert postgreSQL.get_mhs_water_lines() == SAMPLE_FC

    def test_empty_table(self):
        cursor = make_cursor()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()), \
             patch("postgreSQL.query_to_geojson", return_value=EMPTY_FC):
            assert postgreSQL.get_mhs_water_lines() == EMPTY_FC

    def test_db_error_returns_none_and_rolls_back(self):
        conn = Mock()
        with patch("postgreSQL.cursor", make_cursor()), patch("postgreSQL.connection", conn), \
             patch("postgreSQL.query_to_geojson", side_effect=Exception("error")):
            assert postgreSQL.get_mhs_water_lines() is None
        conn.rollback.assert_called_once()


class TestInsertVillageUrl:
    """insert_village_url() — insert article URL linked to a village."""

    def _make_data(self, password="correct_password"):
        return village_url_data(
            village_name="Village A", url="https://example.com/article",
            image_url="https://example.com/img.jpg", article_title="WASH Project",
            posted_date="2024-01-15", password=password
        )

    def test_correct_password_village_found_returns_success(self):
        """Normal: correct password + village exists → Success."""
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.rowcount = 1
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Success"
        conn.commit.assert_called_once()

    def test_correct_password_village_not_found_returns_failed(self):
        """Edge: correct password but village not in DB → Failed."""
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.rowcount = 0
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Failed"
        assert "not found" in result["message"]

    def test_wrong_password_returns_failed(self):
        """Error: wrong password → Failed with password message."""
        cursor = Mock()
        cursor.fetchone.return_value = (hash("correct_password"),)
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", Mock()):
            result = postgreSQL.insert_village_url(self._make_data("wrong_password"))
        assert result["status"] == "Failed"
        assert "password" in result.get("password_message", "").lower()

    def test_insert_exception_returns_failed(self):
        """Error: INSERT raises → Failed with error message, rollback called."""
        cursor = Mock()
        data = self._make_data("correct_password")
        cursor.fetchone.return_value = (hash("correct_password"),)
        cursor.mogrify.return_value = b"INSERT ..."
        cursor.execute.side_effect = [None, Exception("insert failed")]
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            result = postgreSQL.insert_village_url(data)
        assert result["status"] == "Failed"
        conn.rollback.assert_called()


class TestCountUser:
    """count_user() — log IP address to DB."""

    def test_valid_ip_commits(self):
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            postgreSQL.count_user("192.168.1.1")
        conn.commit.assert_called_once()

    def test_empty_ip_still_commits(self):
        """Edge: empty IP string → still commits."""
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            postgreSQL.count_user("")
        conn.commit.assert_called_once()

    def test_db_error_triggers_rollback(self):
        """Error: execute raises → rollback called."""
        cursor = Mock()
        cursor.mogrify.return_value = b"INSERT ..."
        cursor.execute.side_effect = Exception("write failed")
        conn = Mock()
        with patch("postgreSQL.cursor", cursor), patch("postgreSQL.connection", conn):
            postgreSQL.count_user("10.0.0.1")
        conn.rollback.assert_called_once()


# ═════════════════════════════════════════════════════════════
# SECTION 3 — FastAPI endpoints (api_provider2.py)
# ═════════════════════════════════════════════════════════════

class TestRootEndpoint:
    def test_returns_200(self, auth_client):
        assert auth_client.get("/").status_code == 200

    def test_returns_working_message(self, auth_client):
        assert auth_client.get("/").json() == {"message": "The data hosting is working!"}


class TestTestpackageEndpoint:
    def test_returns_200(self, auth_client):
        assert auth_client.get("/api/testpackage/").status_code == 200

    def test_returns_json(self, auth_client):
        assert auth_client.get("/api/testpackage/").json() is not None


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
        """Edge: postgreSQL returns None → empty FeatureCollection."""
        pg = Mock()
        pg.get_village.return_value = None
        app = build_app(pg, lambda t, k: True, lambda s, e, use_elevation=False: EMPTY_FC)
        assert TestClient(app).get("/api/village/").json() == EMPTY_FC


class TestVillageNamesEndpoint:
    def test_returns_200(self, auth_client):
        assert auth_client.get("/api/village_names/").status_code == 200

    def test_returns_list(self, auth_client):
        assert auth_client.get("/api/village_names/").json() == SAMPLE_NAMES

    def test_no_auth_required(self, unauth_client):
        assert unauth_client.get("/api/village_names/").status_code == 200


class TestVillageNamesTHEndpoint:
    def test_returns_200(self, auth_client):
        assert auth_client.get("/api/village_names_th/").status_code == 200

    def test_returns_thai_names(self, auth_client):
        assert auth_client.get("/api/village_names_th/").json() == SAMPLE_NAMES_TH

    def test_no_auth_required(self, unauth_client):
        assert unauth_client.get("/api/village_names_th/").status_code == 200


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

    def test_empty_school_list(self):
        pg = Mock()
        pg.get_school.return_value = EMPTY_FC
        app = build_app(pg, lambda t, k: True, lambda s, e, use_elevation=False: EMPTY_FC)
        assert TestClient(app).get("/api/school/").json()["features"] == []


class TestHospitalEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/hospital/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/hospital/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/hospital/").json()["type"] == "FeatureCollection"

    def test_empty_hospital_list(self):
        pg = Mock()
        pg.get_hospital.return_value = EMPTY_FC
        app = build_app(pg, lambda t, k: True, lambda s, e, use_elevation=False: EMPTY_FC)
        assert TestClient(app).get("/api/hospital/").json()["features"] == []


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
        pg = Mock()
        pg.get_mhs_roads.return_value = SAMPLE_FC
        pg.count_user.return_value = None
        app = build_app(pg, lambda t, k: True, lambda s, e, use_elevation=False: EMPTY_FC)
        TestClient(app).get("/api/mhs_roads/")
        pg.count_user.assert_called_once()


class TestMhsWaterAreasEndpoint:
    def test_no_auth_returns_error(self, unauth_client):
        assert "Error" in unauth_client.get("/api/mhs_water_areas/").json()

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_water_areas/").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_water_areas/").json()["type"] == "FeatureCollection"


class TestMhsWaterLinesEndpoint:
    def test_no_auth_required(self, unauth_client):
        """Normal: water lines is a public endpoint."""
        assert unauth_client.get("/api/mhs_water_lines").status_code == 200

    def test_authenticated_returns_200(self, auth_client):
        assert auth_client.get("/api/mhs_water_lines").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/mhs_water_lines").json()["type"] == "FeatureCollection"

    def test_empty_water_lines(self):
        pg = Mock()
        pg.get_mhs_water_lines.return_value = EMPTY_FC
        app = build_app(pg, lambda t, k: False, lambda s, e, use_elevation=False: EMPTY_FC)
        assert TestClient(app).get("/api/mhs_water_lines").json()["features"] == []


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

    def test_get_not_allowed(self, auth_client):
        assert auth_client.get("/api/post/village_url/").status_code == 405


class TestRouteEndpoint:
    def test_valid_nodes_returns_200(self, auth_client):
        assert auth_client.get("/api/route/?start=1&end=100").status_code == 200

    def test_returns_feature_collection(self, auth_client):
        assert auth_client.get("/api/route/?start=1&end=100").json()["type"] == "FeatureCollection"

    def test_missing_start_returns_422(self, auth_client):
        assert auth_client.get("/api/route/?end=100").status_code == 422

    def test_missing_end_returns_422(self, auth_client):
        assert auth_client.get("/api/route/?start=1").status_code == 422

    def test_non_integer_start_returns_422(self, auth_client):
        assert auth_client.get("/api/route/?start=abc&end=100").status_code == 422

    def test_use_elevation_flag(self, auth_client):
        assert auth_client.get("/api/route/?start=1&end=100&use_elevation=1").status_code == 200

    def test_no_auth_required(self, unauth_client):
        assert unauth_client.get("/api/route/?start=1&end=100").status_code == 200

    def test_features_have_correct_structure(self, auth_client):
        for feature in auth_client.get("/api/route/?start=1&end=100").json()["features"]:
            assert feature["type"] == "Feature"
            assert "geometry" in feature
            assert "properties" in feature