"""
test_unit_frontend.py
======================
Unit tests for KHT frontend JavaScript logic mirrored in Python.
Covers every function in KHT_Homepage_Deploy:

  index.js              — getCurrentTime
  get_data.js           — getVillageData logic, fetchInitialVillageData,
                          getWaterAreas, getWaterLines, getRoads,
                          getHospitals, getSchools, getDistricts,
                          getSubDistricts, fetchVillagebByYear,
                          fetchVillagebByStartAndEndYear,
                          fetchVillagebyProjectType, fetchVillageByDistance,
                          getRoute
  routingMode.js        — toggleRoutingMode, isInRoutingMode,
                          handleRoutingVillageClick, resetRouting
  onEachFeatureFunction.js — resetClickedLayer, onEachFeatureFunction
                             (property extraction logic)
  tourMaps/imageMapList.js — availableMaps structure

Group Members: [Fill in your names]
Project: KHT Mae Hong Son Map — Frontend

Run with:
    pytest test_unit_frontend.py -v --tb=short
"""

import pytest
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# Shared constants
# ─────────────────────────────────────────────────────────────

HOST     = "ailurophile.xyz"
PORT     = "2546"
PROTOCOL = "https"
TIME     = "14-30-00"
KEY      = "abc123"
MINIMUM_YEAR = 2000
CURRENT_YEAR = datetime.now().year

# ─────────────────────────────────────────────────────────────
# Python mirrors of every JS function
# ─────────────────────────────────────────────────────────────

# ── index.js ─────────────────────────────────────────────────

def get_current_time(hours, minutes, seconds):
    """Mirror of index.js getCurrentTime()."""
    return f"{hours:02d}-{minutes:02d}-{seconds:02d}"


# ── get_data.js — URL builders ────────────────────────────────

def build_village_url(host, port, protocol, time_str, key,
                      year="", start_year="", end_year="",
                      project_type="", distance="", facility_type=""):
    """Mirrors URL construction in fetchVillagebByYear,
    fetchVillagebByStartAndEndYear, fetchVillagebyProjectType,
    fetchVillageByDistance, and fetchInitialVillageData."""
    base = f"{protocol}://{host}:{port}/api/village/"
    params = [f"time={time_str}", f"key={key}"]
    if year:
        params.insert(0, f"year={year}")
    elif start_year and end_year:
        params.insert(0, f"start_year={start_year}&end_year={end_year}")
    elif project_type:
        params.insert(0, f"project_type={project_type}")
    elif facility_type and distance:
        params.insert(0, f"distance={distance}&facility_type={facility_type}")
    return base + "?" + "&".join(params)


def build_layer_url(host, port, protocol, time_str, key, endpoint):
    """Mirrors URL construction in getWaterAreas, getWaterLines, getRoads,
    getHospitals, getSchools, getDistricts, getSubDistricts."""
    return f"{protocol}://{host}:{port}/api/{endpoint}/?time={time_str}&key={key}"


def build_route_url(host, port, protocol, start, end, time_str, key):
    """Mirrors URL built in getRoute()."""
    return f"{protocol}://{host}:{port}/api/route/?start={start}&end={end}&time={time_str}&key={key}"


# ── get_data.js — pure logic ──────────────────────────────────

PROJECT_TYPE_MAPPING = {
    "WASH":                          "WASH",
    "Further Education Scholarship": "Further%20Education%20Scholarships",
    "Irrigation":                    "Irrigation",
    "Dormitory Meals":               "Dormitory%20Meals",
}

def map_project_type(raw_type):
    """Mirrors projectTypeMapping lookup in fetchVillagebyProjectType."""
    return PROJECT_TYPE_MAPPING.get(raw_type)


def should_alert_no_data(features, first_load):
    """Mirrors alert condition in getVillageData:
    data_length == 0 and firstLoad == false → alert."""
    return len(features) == 0 and not first_load


def get_point_color(is_initial_load):
    """Mirrors villagePointColor choice:
    fetchInitialVillageData → 'blue', filtered → 'green'."""
    return "blue" if is_initial_load else "green"


def get_route_has_features(features):
    """Mirrors getRoute check: alert if features empty."""
    return len(features) > 0


# ── index.js — year validation ────────────────────────────────

def validate_year_range(start_year_str, end_year_str):
    """Mirrors radio2 year-range validation in index.js."""
    try:
        start = int(start_year_str)
        end   = int(end_year_str)
    except (ValueError, TypeError):
        return False, "non-integer input"
    if start < MINIMUM_YEAR:
        return False, f"start year below minimum ({MINIMUM_YEAR})"
    if end > CURRENT_YEAR:
        return False, "end year in the future"
    if start > end:
        return False, "start year after end year"
    return True, None


def validate_single_year(year_str):
    """Mirrors radio1 single-year validation in index.js."""
    try:
        year = int(year_str)
    except (ValueError, TypeError):
        return False, "non-integer input"
    if year < MINIMUM_YEAR:
        return False, f"year below minimum ({MINIMUM_YEAR})"
    if year > CURRENT_YEAR:
        return False, "year in the future"
    return True, None


# ── routingMode.js ────────────────────────────────────────────

class RoutingState:
    """
    Python mirror of routingMode.js module state and all four
    exported functions: toggleRoutingMode, isInRoutingMode,
    handleRoutingVillageClick, resetRouting.
    """
    def __init__(self):
        self.is_routing_mode = False
        self.start_village   = None
        self.end_village     = None
        self.start_layer     = None
        self.end_layer       = None
        self.route_requested = None   # records (start, end) when getRoute is called

    def toggle_routing_mode(self):
        """Mirror of toggleRoutingMode()."""
        self.is_routing_mode = not self.is_routing_mode
        self.reset_routing()
        return self.is_routing_mode

    def is_in_routing_mode(self):
        """Mirror of isInRoutingMode()."""
        return self.is_routing_mode

    def reset_routing(self):
        """Mirror of resetRouting()."""
        self.start_village = None
        self.end_village   = None
        self.start_layer   = None
        self.end_layer     = None
        self.route_requested = None

    def handle_routing_village_click(self, feature, layer):
        """Mirror of handleRoutingVillageClick()."""
        if not self.is_routing_mode:
            return False

        node_id = feature.get("properties", {}).get("nearby_node")
        if node_id is None:
            return False

        if self.start_village is None:
            self.start_village = node_id
            self.start_layer   = layer
            return "start_set"

        elif self.end_village is None:
            self.end_village = node_id
            self.end_layer   = layer
            self.route_requested = (self.start_village, self.end_village)
            self.is_routing_mode = False
            return "end_set"

        return False


# ── onEachFeatureFunction.js — property extraction ────────────

def extract_village_properties(feature):
    """
    Mirrors the localStorage.setItem calls in onEachFeatureFunction.
    Extracts all properties a village click would store.
    Returns a dict of key → value (None if missing).
    """
    props = feature.get("properties", {})

    def get(key):
        val = props.get(key)
        return "-" if val is None else val

    return {
        "village-name":          get("village_name"),
        "village-name-th":       get("village_name_th"),
        "road-quality":          get("road_conditions"),
        "distance-pratom":       get("distance_to_pratom_km"),
        "distance-mathayom":     get("distance_to_mathayom_km"),
        "project-name":          get("hosted_kht_projects"),
        "adult-male":            get("adult_males"),
        "adult-female":          get("adult_females"),
        "common-disease":        get("common_diseases"),
        "Households":            get("households"),
        "rice-ratio":            get("population_without_enough_rice"),
        "children":              get("children_aged_0_18"),
        "distance-town":         get("distance_to_town_km"),
        "distance-hospital":     get("distance_to_hospital_km"),
        "nearest-health-center": get("nearest_health_centre"),
        "annual-typhoid":        get("annual_typhoid_cases"),
    }


def reset_clicked_layer_style():
    """
    Mirror of resetClickedLayer() — returns the style that would
    be applied to a previously clicked layer.
    """
    return {"fillColor": "blue", "color": "white"}


# ── tourMaps/imageMapList.js ──────────────────────────────────

AVAILABLE_MAPS = [
    {"name": "Baan Mae Hat",      "filename": "BMH-tour.html"},
    {"name": "Baan Mae Oom Long", "filename": "BMOL-tour.html"},
]


# ═════════════════════════════════════════════════════════════
# Tests
# ═════════════════════════════════════════════════════════════

class TestGetCurrentTime:
    """index.js — getCurrentTime()"""

    def test_normal_format(self):
        assert get_current_time(14, 30, 5) == "14-30-05"

    def test_midnight(self):
        assert get_current_time(0, 0, 0) == "00-00-00"

    def test_end_of_day(self):
        assert get_current_time(23, 59, 59) == "23-59-59"

    def test_single_digit_zero_padded(self):
        assert get_current_time(9, 5, 3) == "09-05-03"

    def test_separator_is_hyphen(self):
        assert len(get_current_time(10, 20, 30).split("-")) == 3

    def test_length_always_8(self):
        assert len(get_current_time(1, 2, 3)) == 8


class TestBuildVillageURL:
    """get_data.js — fetchInitialVillageData / fetchVillagebByYear /
    fetchVillagebByStartAndEndYear / fetchVillagebyProjectType /
    fetchVillageByDistance URL construction."""

    def _build(self, **kwargs):
        return build_village_url(HOST, PORT, PROTOCOL, TIME, KEY, **kwargs)

    def test_initial_load_url(self):
        """fetchInitialVillageData — no filter params."""
        url = self._build()
        assert f"{PROTOCOL}://{HOST}:{PORT}/api/village/" in url
        assert f"time={TIME}" in url
        assert f"key={KEY}" in url

    def test_year_filter(self):
        """fetchVillagebByYear — year param included."""
        assert "year=2022" in self._build(year="2022")

    def test_start_end_year_filter(self):
        """fetchVillagebByStartAndEndYear — both params included."""
        url = self._build(start_year="2020", end_year="2023")
        assert "start_year=2020" in url
        assert "end_year=2023" in url

    def test_project_type_filter(self):
        """fetchVillagebyProjectType — project_type param included."""
        assert "project_type=WASH" in self._build(project_type="WASH")

    def test_distance_filter(self):
        """fetchVillageByDistance — distance and facility_type included."""
        url = self._build(distance="5000", facility_type="school")
        assert "distance=5000" in url
        assert "facility_type=school" in url

    def test_auth_always_present(self):
        url = self._build(year="2021")
        assert "time=" in url and "key=" in url

    def test_uses_https(self):
        assert self._build().startswith("https://")

    def test_uses_correct_port(self):
        assert ":2546/" in self._build()


class TestBuildLayerURL:
    """get_data.js — getWaterAreas, getWaterLines, getRoads,
    getHospitals, getSchools, getDistricts, getSubDistricts URL construction."""

    @pytest.mark.parametrize("endpoint,label", [
        ("mhs_water_areas",  "getWaterAreas"),
        ("mhs_water_lines",  "getWaterLines"),
        ("mhs_roads",        "getRoads"),
        ("hospital",         "getHospitals"),
        ("school",           "getSchools"),
        ("mhs_districts",    "getDistricts"),
        ("mhs_subdistricts", "getSubDistricts"),
    ])
    def test_url_contains_endpoint(self, endpoint, label):
        """Normal: each layer function targets the correct API endpoint."""
        url = build_layer_url(HOST, PORT, PROTOCOL, TIME, KEY, endpoint)
        assert f"/api/{endpoint}/" in url

    def test_auth_params_present(self):
        url = build_layer_url(HOST, PORT, PROTOCOL, TIME, KEY, "hospital")
        assert f"time={TIME}" in url
        assert f"key={KEY}" in url

    def test_uses_https(self):
        assert build_layer_url(HOST, PORT, PROTOCOL, TIME, KEY, "school").startswith("https://")

    def test_uses_correct_port(self):
        assert ":2546/" in build_layer_url(HOST, PORT, PROTOCOL, TIME, KEY, "mhs_roads")


class TestBuildRouteURL:
    """get_data.js — getRoute() URL construction."""

    def test_contains_start_and_end(self):
        url = build_route_url(HOST, PORT, PROTOCOL, 1, 100, TIME, KEY)
        assert "start=1" in url
        assert "end=100" in url

    def test_targets_route_endpoint(self):
        assert "/api/route/" in build_route_url(HOST, PORT, PROTOCOL, 1, 100, TIME, KEY)

    def test_auth_params_present(self):
        url = build_route_url(HOST, PORT, PROTOCOL, 1, 100, TIME, KEY)
        assert f"time={TIME}" in url
        assert f"key={KEY}" in url

    def test_uses_https(self):
        assert build_route_url(HOST, PORT, PROTOCOL, 1, 100, TIME, KEY).startswith("https://")


class TestProjectTypeMapping:
    """get_data.js — fetchVillagebyProjectType projectTypeMapping."""

    @pytest.mark.parametrize("raw,expected", [
        ("WASH",                          "WASH"),
        ("Irrigation",                    "Irrigation"),
        ("Dormitory Meals",               "Dormitory%20Meals"),
        ("Further Education Scholarship", "Further%20Education%20Scholarships"),
    ])
    def test_valid_types(self, raw, expected):
        assert map_project_type(raw) == expected

    def test_unknown_type_returns_none(self):
        assert map_project_type("Unknown") is None

    def test_empty_string_returns_none(self):
        assert map_project_type("") is None

    def test_case_sensitive(self):
        """Edge: lowercase 'wash' does not match 'WASH'."""
        assert map_project_type("wash") is None


class TestShouldAlertNoData:
    """get_data.js — getVillageData empty-result alert logic."""

    def test_empty_on_first_load_no_alert(self):
        """Edge: first load, no data → no alert yet."""
        assert should_alert_no_data([], first_load=True) is False

    def test_empty_after_filter_alerts(self):
        """Normal: filter returned nothing → alert user."""
        assert should_alert_no_data([], first_load=False) is True

    def test_non_empty_no_alert(self):
        assert should_alert_no_data([{"type": "Feature"}], first_load=False) is False

    def test_single_feature_no_alert(self):
        assert should_alert_no_data([{}], first_load=False) is False


class TestGetPointColor:
    """get_data.js — villagePointColor selection."""

    def test_initial_load_is_blue(self):
        assert get_point_color(is_initial_load=True) == "blue"

    def test_filtered_load_is_green(self):
        assert get_point_color(is_initial_load=False) == "green"


class TestGetRouteHasFeatures:
    """get_data.js — getRoute() empty-features alert logic."""

    def test_empty_features_triggers_alert(self):
        """Error: no route found → alert 'no roads between these two points'."""
        assert get_route_has_features([]) is False

    def test_non_empty_features_no_alert(self):
        assert get_route_has_features([{"type": "Feature"}]) is True


class TestYearRangeValidation:
    """index.js — radio2 start_year / end_year validation."""

    def test_valid_range(self):
        ok, err = validate_year_range("2020", "2023")
        assert ok is True and err is None

    def test_same_start_and_end(self):
        ok, _ = validate_year_range("2022", "2022")
        assert ok is True

    def test_start_after_end(self):
        ok, err = validate_year_range("2023", "2020")
        assert ok is False and "start year after end year" in err

    def test_below_minimum(self):
        ok, err = validate_year_range("1999", "2022")
        assert ok is False and "minimum" in err

    def test_future_end_year(self):
        ok, err = validate_year_range("2020", str(CURRENT_YEAR + 1))
        assert ok is False and "future" in err

    def test_non_integer_input(self):
        ok, err = validate_year_range("abc", "2023")
        assert ok is False and "non-integer" in err

    def test_empty_string(self):
        ok, _ = validate_year_range("", "2023")
        assert ok is False

    def test_minimum_year_boundary(self):
        ok, _ = validate_year_range(str(MINIMUM_YEAR), str(MINIMUM_YEAR))
        assert ok is True

    def test_one_below_minimum(self):
        ok, _ = validate_year_range(str(MINIMUM_YEAR - 1), "2022")
        assert ok is False


class TestSingleYearValidation:
    """index.js — radio1 single year validation."""

    def test_valid_year(self):
        ok, _ = validate_single_year("2022")
        assert ok is True

    def test_before_2000(self):
        ok, _ = validate_single_year("1999")
        assert ok is False

    def test_non_numeric(self):
        ok, _ = validate_single_year("twenty-twenty")
        assert ok is False

    def test_future_year(self):
        ok, _ = validate_single_year(str(CURRENT_YEAR + 5))
        assert ok is False

    def test_current_year_valid(self):
        ok, _ = validate_single_year(str(CURRENT_YEAR))
        assert ok is True


class TestToggleRoutingMode:
    """routingMode.js — toggleRoutingMode()."""

    def test_starts_false(self):
        state = RoutingState()
        assert state.is_in_routing_mode() is False

    def test_first_toggle_enables(self):
        state = RoutingState()
        assert state.toggle_routing_mode() is True

    def test_second_toggle_disables(self):
        state = RoutingState()
        state.toggle_routing_mode()
        assert state.toggle_routing_mode() is False

    def test_toggle_resets_routing_state(self):
        """Normal: toggling clears any previously set start/end villages."""
        state = RoutingState()
        state.start_village = 42
        state.end_village   = 99
        state.toggle_routing_mode()
        assert state.start_village is None
        assert state.end_village is None


class TestIsInRoutingMode:
    """routingMode.js — isInRoutingMode()."""

    def test_false_by_default(self):
        assert RoutingState().is_in_routing_mode() is False

    def test_true_after_toggle(self):
        state = RoutingState()
        state.toggle_routing_mode()
        assert state.is_in_routing_mode() is True


class TestHandleRoutingVillageClick:
    """routingMode.js — handleRoutingVillageClick()."""

    def _feature(self, node_id):
        return {"properties": {"nearby_node": node_id, "village_name": "Test Village"}}

    def test_not_in_routing_mode_returns_false(self):
        """Error: called when routing is off → returns False."""
        state = RoutingState()
        assert state.handle_routing_village_click(self._feature(1), "layer") is False

    def test_null_node_id_returns_false(self):
        """Error: village has no nearby_node → invalid, returns False."""
        state = RoutingState()
        state.toggle_routing_mode()
        assert state.handle_routing_village_click(
            {"properties": {"nearby_node": None}}, "layer") is False

    def test_first_click_sets_start(self):
        """Normal: first click sets start village."""
        state = RoutingState()
        state.toggle_routing_mode()
        result = state.handle_routing_village_click(self._feature(10), "layer_a")
        assert result == "start_set"
        assert state.start_village == 10

    def test_second_click_sets_end_and_requests_route(self):
        """Normal: second click sets end village and triggers route request."""
        state = RoutingState()
        state.toggle_routing_mode()
        state.handle_routing_village_click(self._feature(10), "layer_a")
        result = state.handle_routing_village_click(self._feature(20), "layer_b")
        assert result == "end_set"
        assert state.end_village == 20
        assert state.route_requested == (10, 20)

    def test_second_click_deactivates_routing_mode(self):
        """Normal: after both points selected, routing mode turns off."""
        state = RoutingState()
        state.toggle_routing_mode()
        state.handle_routing_village_click(self._feature(10), "layer_a")
        state.handle_routing_village_click(self._feature(20), "layer_b")
        assert state.is_in_routing_mode() is False

    def test_different_node_ids_for_start_and_end(self):
        """Normal: start and end are stored as different node IDs."""
        state = RoutingState()
        state.toggle_routing_mode()
        state.handle_routing_village_click(self._feature(1), "layer_a")
        state.handle_routing_village_click(self._feature(2), "layer_b")
        assert state.route_requested == (1, 2)


class TestResetRouting:
    """routingMode.js — resetRouting()."""

    def test_clears_start_and_end(self):
        state = RoutingState()
        state.start_village = 10
        state.end_village   = 20
        state.reset_routing()
        assert state.start_village is None
        assert state.end_village is None

    def test_clears_layers(self):
        state = RoutingState()
        state.start_layer = "layer_a"
        state.end_layer   = "layer_b"
        state.reset_routing()
        assert state.start_layer is None
        assert state.end_layer is None

    def test_clears_route_request(self):
        state = RoutingState()
        state.route_requested = (10, 20)
        state.reset_routing()
        assert state.route_requested is None

    def test_reset_on_fresh_state_does_not_crash(self):
        """Edge: resetting a fresh state with no villages set → no error."""
        RoutingState().reset_routing()


class TestResetClickedLayer:
    """onEachFeatureFunction.js — resetClickedLayer()."""

    def test_returns_blue_and_white_style(self):
        """Normal: reset style returns blue fill, white border."""
        style = reset_clicked_layer_style()
        assert style["fillColor"] == "blue"
        assert style["color"] == "white"


class TestExtractVillageProperties:
    """onEachFeatureFunction.js — onEachFeatureFunction property extraction."""

    def _feature(self, **props):
        return {"properties": props}

    def test_all_fields_present(self):
        """Normal: all properties present → all extracted correctly."""
        feature = self._feature(
            village_name="Village A",
            village_name_th="หมู่บ้าน เอ",
            road_conditions="Paved",
            distance_to_pratom_km=5,
            distance_to_mathayom_km=10,
            hosted_kht_projects="WASH",
            adult_males=100,
            adult_females=95,
            common_diseases="Malaria",
            households=40,
            population_without_enough_rice=10,
            children_aged_0_18=30,
            distance_to_town_km=20,
            distance_to_hospital_km=15,
            nearest_health_centre="Clinic A",
            annual_typhoid_cases=3,
        )
        result = extract_village_properties(feature)
        assert result["village-name"]          == "Village A"
        assert result["village-name-th"]       == "หมู่บ้าน เอ"
        assert result["road-quality"]          == "Paved"
        assert result["distance-pratom"]       == 5
        assert result["distance-mathayom"]     == 10
        assert result["project-name"]          == "WASH"
        assert result["adult-male"]            == 100
        assert result["adult-female"]          == 95
        assert result["common-disease"]        == "Malaria"
        assert result["Households"]            == 40
        assert result["rice-ratio"]            == 10
        assert result["children"]              == 30
        assert result["distance-town"]         == 20
        assert result["distance-hospital"]     == 15
        assert result["nearest-health-center"] == "Clinic A"
        assert result["annual-typhoid"]        == 3

    def test_null_property_becomes_dash(self):
        """Edge: None property → stored as '-' (mirrors JS null check)."""
        feature = self._feature(village_name=None, road_conditions=None)
        result = extract_village_properties(feature)
        assert result["village-name"] == "-"
        assert result["road-quality"] == "-"

    def test_missing_property_becomes_dash(self):
        """Edge: property not present at all → stored as '-'."""
        result = extract_village_properties({"properties": {}})
        assert result["village-name"]    == "-"
        assert result["distance-town"]   == "-"
        assert result["annual-typhoid"]  == "-"

    def test_returns_all_16_keys(self):
        """Normal: result always contains all 16 expected keys."""
        result = extract_village_properties({"properties": {}})
        expected_keys = {
            "village-name", "village-name-th", "road-quality",
            "distance-pratom", "distance-mathayom", "project-name",
            "adult-male", "adult-female", "common-disease", "Households",
            "rice-ratio", "children", "distance-town", "distance-hospital",
            "nearest-health-center", "annual-typhoid"
        }
        assert set(result.keys()) == expected_keys

    def test_zero_values_not_replaced_with_dash(self):
        """Edge: numeric zero is a valid value, not replaced with '-'."""
        feature = self._feature(households=0, children_aged_0_18=0)
        result = extract_village_properties(feature)
        assert result["Households"] == 0
        assert result["children"]   == 0


class TestAvailableMaps:
    """tourMaps/imageMapList.js — availableMaps constant."""

    def test_contains_two_maps(self):
        """Normal: two tour maps are defined."""
        assert len(AVAILABLE_MAPS) == 2

    def test_each_map_has_name_and_filename(self):
        """Normal: each entry has both name and filename keys."""
        for m in AVAILABLE_MAPS:
            assert "name"     in m
            assert "filename" in m

    def test_baan_mae_hat_present(self):
        names = [m["name"] for m in AVAILABLE_MAPS]
        assert "Baan Mae Hat" in names

    def test_baan_mae_oom_long_present(self):
        names = [m["name"] for m in AVAILABLE_MAPS]
        assert "Baan Mae Oom Long" in names

    def test_filenames_are_html(self):
        """Normal: all filenames end with .html."""
        for m in AVAILABLE_MAPS:
            assert m["filename"].endswith(".html")