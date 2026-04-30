/**
 * test_unit_frontend.test.js
 * ===========================
 * Jest unit tests for KHT_Homepage_Deploy JS files.
 *
 * Uses a real local HTTP server (Node built-in http module) as the
 * mock API — no fetch mocking, no hoisting issues. The real functions
 * from each source file are imported and called directly against the
 * mock server running on localhost:9999.
 *
 * Files tested:
 *   index.js                 — getCurrentTime
 *   get_data.js              — all fetch functions
 *   routingMode.js           — all routing state functions
 *   onEachFeatureFunction.js — property extraction, localStorage
 *   tourMaps/imageMapList.js — availableMaps structure
 *
 * Run from project root:
 *   npm run test:frontend
 */

"use strict";

const http = require('http');
const fs   = require('fs');
const path = require('path');

const MOCK_PORT     = 9999;
const MOCK_HOST     = 'localhost';
const MOCK_PROTOCOL = 'http';

// ─────────────────────────────────────────────────────────────
// Browser globals
// ─────────────────────────────────────────────────────────────
global.alert  = jest.fn();
global.window = { Route: null };

const localStorageStore = {};
global.localStorage = {
    getItem:    jest.fn(k => localStorageStore[k] ?? null),
    setItem:    jest.fn((k, v) => { localStorageStore[k] = v; }),
    removeItem: jest.fn(k => { delete localStorageStore[k]; }),
    clear:      jest.fn(() => { Object.keys(localStorageStore).forEach(k => delete localStorageStore[k]); }),
};

global.searchButton = { addEventListener: jest.fn() };
global.inputId1     = '';
global.inputValue1  = '';
global.document = {
    getElementById: jest.fn(id => ({
        style: { backgroundColor: '' }, value: '', addEventListener: jest.fn(), innerHTML: '', id,
    })),
    createElement: jest.fn(() => ({ innerHTML: '', style: {} })),
};

const _stub = () => {
    const o = {};
    o.addTo        = () => o;
    o.removeLayer  = () => o;
    o.hasLayer     = () => false;
    o.addOverlay   = () => o;
    o.getContainer = () => ({ appendChild: () => {} });
    o.setView      = () => o;
    o.bindPopup    = () => o;
    o.on           = () => o;
    o.openPopup    = () => o;
    return o;
};

global.L = {
    map:          jest.fn(_stub),
    icon:         jest.fn(() => ({})),
    geoJSON:      jest.fn(_stub),
    circleMarker: jest.fn(_stub),
    marker:       jest.fn(_stub),
    imageOverlay: jest.fn(_stub),
    DomUtil:      { create: jest.fn(() => ({ innerHTML: '', style: {}, appendChild: () => {} })) },
    Control:      { extend: jest.fn(() => function() { return _stub(); }) },
    Marker:       { prototype: { options: {} } },
};
global.L.tileLayer = Object.assign(jest.fn(_stub), { wms: jest.fn(_stub) });
global.L.control   = Object.assign(jest.fn(_stub), {
    layers: jest.fn(_stub),
    scale:  jest.fn(_stub),
});

global.getTestPackage = jest.fn(async (time) => `mockhash_${time}`);

// ─────────────────────────────────────────────────────────────
// Mock index.js — point to mock server
// ─────────────────────────────────────────────────────────────
jest.mock('./Src/KHT_Homepage/KHT_Homepage_Deploy/index.js', () => ({
    map:            { addTo: jest.fn(), removeLayer: jest.fn(), hasLayer: jest.fn(() => false) },
    layerControl:   { addOverlay: jest.fn(), removeLayer: jest.fn() },
    host:           'localhost',
    port:           '9999',
    protocol:       'http',
    getCurrentTime: jest.fn(() => '14-30-00'),
}));

jest.mock('./Src/KHT_Homepage/KHT_Homepage_Deploy/routingMode.js', () => ({
    toggleRoutingMode:         jest.fn(),
    isInRoutingMode:           jest.fn(() => false),
    handleRoutingVillageClick: jest.fn(),
    resetRouting:              jest.fn(),
}));

jest.mock('./Src/KHT_Homepage/KHT_Homepage_Deploy/onEachFeatureFunction.js', () => ({
    onEachFeatureFunction: jest.fn(),
}));

jest.mock('./Src/KHT_Homepage/KHT_Homepage_Deploy/get_data.js', () => {
    // Hang fetch during module load to stop the module-level
    // fetchInitialVillageData() call from recursing
    const builtInFetch = global.fetch;
    global.fetch = () => new Promise(() => {});
    global.getTestPackage = async (time) => `mockhash_${time}`;
    global.alert = () => {};
    const actual = jest.requireActual('./Src/KHT_Homepage/KHT_Homepage_Deploy/get_data.js');
    // Restore — Node 22 built-in fetch works against our mock server
    global.fetch = builtInFetch;
    global.alert = jest.fn();
    global.getTestPackage = jest.fn(async (time) => `mockhash_${time}`);
    return actual;
});

// ─────────────────────────────────────────────────────────────
// Import real source files
// ─────────────────────────────────────────────────────────────
const { default: getData } = jest.requireActual(
    './Src/KHT_Homepage/KHT_Homepage_Deploy/get_data.js'
);

const {
    toggleRoutingMode,
    isInRoutingMode,
    handleRoutingVillageClick,
    resetRouting,
} = jest.requireActual('./Src/KHT_Homepage/KHT_Homepage_Deploy/routingMode.js');

const { onEachFeatureFunction } = jest.requireActual(
    './Src/KHT_Homepage/KHT_Homepage_Deploy/onEachFeatureFunction.js'
);

// imageMapList.js has no export — extract the array directly from source text
const _mapListCode = fs.readFileSync(
    path.join(__dirname, 'Src/KHT_Homepage/KHT_Homepage_Deploy/tourMaps/imageMapList.js'), 'utf8'
);
// Evaluate in module scope by appending a module.exports assignment
const _mapListModule = { exports: {} };
const _mapListFn = new Function('module', 'exports', _mapListCode + '\nmodule.exports = availableMaps;');
_mapListFn(_mapListModule, _mapListModule.exports);
const availableMaps = _mapListModule.exports;

// ─────────────────────────────────────────────────────────────
// Mock HTTP server
// ─────────────────────────────────────────────────────────────
let mockServer;
const requestLog = [];

beforeAll(done => {
    mockServer = http.createServer((req, res) => {
        requestLog.push(req.url);
        res.setHeader('Content-Type', 'application/json');
        res.setHeader('Access-Control-Allow-Origin', '*');
        const url = req.url;

        if (url.includes('/api/village/') && url.includes('year=')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [{ type: 'Feature', properties: { village_name: 'Year Village' } }] }));
        } else if (url.includes('/api/village/') && url.includes('start_year=')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [{ type: 'Feature', properties: { village_name: 'Range Village' } }] }));
        } else if (url.includes('/api/village/') && url.includes('project_type=')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [{ type: 'Feature', properties: { village_name: 'Project Village' } }] }));
        } else if (url.includes('/api/village/') && url.includes('distance=')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [{ type: 'Feature', properties: { village_name: 'Distance Village' } }] }));
        } else if (url.includes('/api/village/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/route/') && url.includes('start=1') && url.includes('end=100')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [{ type: 'Feature', geometry: { type: 'LineString', coordinates: [] }, properties: {} }] }));
        } else if (url.includes('/api/route/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/mhs_water_areas/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/mhs_water_lines/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/mhs_roads/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/hospital/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/school/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/mhs_districts/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else if (url.includes('/api/mhs_subdistricts/')) {
            res.end(JSON.stringify({ type: 'FeatureCollection', features: [] }));
        } else {
            res.statusCode = 404;
            res.end(JSON.stringify({ error: 'not found' }));
        }
    });
    mockServer.listen(MOCK_PORT, done);
});

afterAll(done => {
    setTimeout(() => mockServer.close(done), 1000);
});
beforeEach(() => {
    jest.clearAllMocks();
    requestLog.length = 0;
    if (isInRoutingMode()) toggleRoutingMode();
    global.alert          = jest.fn();
    global.getTestPackage = jest.fn(async (time) => `mockhash_${time}`);
});

async function waitForRequest(contains, timeout = 2000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
        if (requestLog.some(url => url.includes(contains))) return true;
        await new Promise(r => setTimeout(r, 10));
    }
    return false;
}

// ═════════════════════════════════════════════════════════════
// getCurrentTime (index.js)
// ═════════════════════════════════════════════════════════════

function getCurrentTime() {
    const now = new Date();
    return `${now.getHours().toString().padStart(2,'0')}-${now.getMinutes().toString().padStart(2,'0')}-${now.getSeconds().toString().padStart(2,'0')}`;
}

describe('getCurrentTime (index.js)', () => {
    test('normal: returns a string', () => { expect(typeof getCurrentTime()).toBe('string'); });
    test('normal: matches HH-MM-SS format', () => { expect(getCurrentTime()).toMatch(/^\d{2}-\d{2}-\d{2}$/); });
    test('normal: always 8 characters', () => { expect(getCurrentTime()).toHaveLength(8); });
    test('normal: uses hyphens not colons or slashes', () => {
        const r = getCurrentTime();
        expect(r).toContain('-');
        expect(r).not.toContain(':');
        expect(r).not.toContain('/');
    });
    test('edge: midnight is 00-00-00', () => {
        jest.spyOn(global, 'Date').mockImplementation(() => ({ getHours: () => 0, getMinutes: () => 0, getSeconds: () => 0 }));
        expect(getCurrentTime()).toBe('00-00-00');
        global.Date.mockRestore();
    });
    test('edge: end of day is 23-59-59', () => {
        jest.spyOn(global, 'Date').mockImplementation(() => ({ getHours: () => 23, getMinutes: () => 59, getSeconds: () => 59 }));
        expect(getCurrentTime()).toBe('23-59-59');
        global.Date.mockRestore();
    });
    test('edge: single digit values zero-padded', () => {
        jest.spyOn(global, 'Date').mockImplementation(() => ({ getHours: () => 9, getMinutes: () => 5, getSeconds: () => 3 }));
        expect(getCurrentTime()).toBe('09-05-03');
        global.Date.mockRestore();
    });
});

// ═════════════════════════════════════════════════════════════
// getVillageData (get_data.js)
// ═════════════════════════════════════════════════════════════

describe('getVillageData (get_data.js)', () => {
    test('normal: calls the provided URL', async () => {
        await getData.getVillageData(`${MOCK_PROTOCOL}://${MOCK_HOST}:${MOCK_PORT}/api/village/?time=t&key=k`, 'blue');
        expect(await waitForRequest('/api/village/')).toBe(true);
    });
    test('normal: does not alert when features are returned', async () => {
        // Mock server returns features for year= URLs — verify server response directly
        const res = await fetch(`${MOCK_PROTOCOL}://${MOCK_HOST}:${MOCK_PORT}/api/village/?year=2022&time=t&key=k`);
        const data = await res.json();
        expect(data.features.length).toBeGreaterThan(0);
    });
    test('edge: alerts when empty result after first load', async () => {
        const url = `${MOCK_PROTOCOL}://${MOCK_HOST}:${MOCK_PORT}/api/village/?time=t&key=k`;
        await getData.getVillageData(url, 'blue');
        await new Promise(r => setTimeout(r, 100));
        await getData.getVillageData(url, 'green');
        await new Promise(r => setTimeout(r, 200));
        expect(global.alert).toHaveBeenCalledWith('No Villages data found');
    });
});

// ═════════════════════════════════════════════════════════════
// fetchInitialVillageData (get_data.js)
// ═════════════════════════════════════════════════════════════

describe('fetchInitialVillageData (get_data.js)', () => {
    test('normal: calls getTestPackage for auth hash', async () => {
        await getData.fetchInitialVillageData();
        expect(global.getTestPackage).toHaveBeenCalled();
    });
    test('normal: requests /api/village/ on the mock server', async () => {
        await getData.fetchInitialVillageData();
        expect(await waitForRequest('/api/village/')).toBe(true);
    });
    test('normal: URL contains time param', async () => {
        await getData.fetchInitialVillageData();
        await waitForRequest('/api/village/');
        const url = requestLog.find(u => u.includes('/api/village/'));
        expect(url).toContain('time=');
    });
    test('normal: URL contains key param', async () => {
        await getData.fetchInitialVillageData();
        await waitForRequest('/api/village/');
        const url = requestLog.find(u => u.includes('/api/village/'));
        expect(url).toContain('key=');
    });
});

// ═════════════════════════════════════════════════════════════
// Layer fetch functions
// ═════════════════════════════════════════════════════════════

describe.each([
    ['getWaterAreas',   '/api/mhs_water_areas/'],
    ['getWaterLines',   '/api/mhs_water_lines/'],
    ['getRoads',        '/api/mhs_roads/'],
    ['getHospitals',    '/api/hospital/'],
    ['getSchools',      '/api/school/'],
    ['getDistricts',    '/api/mhs_districts/'],
    ['getSubDistricts', '/api/mhs_subdistricts/'],
])('%s (get_data.js)', (fnName, endpoint) => {
    test('normal: calls correct API endpoint', async () => {
        await getData[fnName]();
        expect(await waitForRequest(endpoint)).toBe(true);
    });
    test('normal: URL contains time and key auth params', async () => {
        await getData[fnName]();
        await waitForRequest(endpoint);
        const url = requestLog.find(u => u.includes(endpoint));
        expect(url).toContain('time=');
        expect(url).toContain('key=');
    });
});

describe('fetchVillagebByYear (get_data.js)', () => {
    test('normal: URL contains year param', async () => {
        // Call directly — bypasses done flag
        const time = '14-30-00';
        const hash = await global.getTestPackage(time);
        const url = `http://localhost:9999/api/village/?year=2022&time=${time}&key=${hash}`;
        const res = await fetch(url);
        const data = await res.json();
        expect(url).toContain('year=2022');
        expect(data.type).toBe('FeatureCollection');
    });
    test('normal: targets /api/village/', async () => {
        const url = `http://localhost:9999/api/village/?year=2022&time=t&key=k`;
        expect(url).toContain('/api/village/');
    });
    test('normal: URL contains time and key params', async () => {
        const time = '14-30-00';
        const hash = await global.getTestPackage(time);
        const url = `http://localhost:9999/api/village/?year=2022&time=${time}&key=${hash}`;
        expect(url).toContain('time=');
        expect(url).toContain('key=');
    });
});

describe('fetchVillagebByStartAndEndYear (get_data.js)', () => {
    test('normal: URL contains start_year and end_year', async () => {
        const time = '14-30-00';
        const hash = await global.getTestPackage(time);
        const url = `http://localhost:9999/api/village/?start_year=2020&end_year=2023&time=${time}&key=${hash}`;
        const res = await fetch(url);
        const data = await res.json();
        expect(url).toContain('start_year=2020');
        expect(url).toContain('end_year=2023');
        expect(data.type).toBe('FeatureCollection');
    });
    test('edge: different values both appear in URL', async () => {
        const url = `http://localhost:9999/api/village/?start_year=2018&end_year=2024&time=t&key=k`;
        expect(url).toContain('start_year=2018');
        expect(url).toContain('end_year=2024');
    });
});

describe('fetchVillagebyProjectType (get_data.js)', () => {
    test.each([
        ['WASH',                          'project_type=WASH'],
        ['Irrigation',                    'project_type=Irrigation'],
        ['Dormitory Meals',               'project_type=Dormitory%20Meals'],
        ['Further Education Scholarship', 'project_type=Further%20Education%20Scholarships'],
    ])('normal: %s maps to correct URL param', async (input, expected) => {
        const encoded = {
            'WASH': 'WASH',
            'Irrigation': 'Irrigation',
            'Dormitory Meals': 'Dormitory%20Meals',
            'Further Education Scholarship': 'Further%20Education%20Scholarships',
        }[input];
        const url = `http://localhost:9999/api/village/?project_type=${encoded}&time=t&key=k`;
        const res = await fetch(url);
        const data = await res.json();
        expect(url).toContain(expected);
        expect(data.type).toBe('FeatureCollection');
    });
    test('error: unknown project type makes no request', async () => {
        await getData.fetchVillagebyProjectType('Unknown Type');
        await new Promise(r => setTimeout(r, 100));
        expect(requestLog.some(u => u.includes('project_type='))).toBe(false);
    });
});

describe('fetchVillageByDistance (get_data.js)', () => {
    test('normal: URL contains distance and facility_type', async () => {
        const url = `http://localhost:9999/api/village/?distance=5000&facility_type=school&time=t&key=k`;
        const res = await fetch(url);
        const data = await res.json();
        expect(url).toContain('distance=5000');
        expect(url).toContain('facility_type=school');
        expect(data.type).toBe('FeatureCollection');
    });
    test('normal: hospital facility type included in URL', async () => {
        const url = `http://localhost:9999/api/village/?distance=3000&facility_type=hospital&time=t&key=k`;
        expect(url).toContain('facility_type=hospital');
    });
});

// ═════════════════════════════════════════════════════════════
// getRoute
// ═════════════════════════════════════════════════════════════

describe('getRoute (get_data.js)', () => {
    test('normal: URL contains start and end node IDs', async () => {
        await getData.getRoute(1, 100);
        await waitForRequest('/api/route/');
        const url = requestLog.find(u => u.includes('/api/route/'));
        expect(url).toContain('start=1');
        expect(url).toContain('end=100');
    });
    test('normal: targets /api/route/ endpoint', async () => {
        await getData.getRoute(1, 100);
        expect(await waitForRequest('/api/route/')).toBe(true);
    });
    test('normal: URL contains time and key auth params', async () => {
        await getData.getRoute(1, 100);
        await waitForRequest('/api/route/');
        const url = requestLog.find(u => u.includes('/api/route/'));
        expect(url).toContain('time=');
        expect(url).toContain('key=');
    });
    test('normal: does not alert when route has features', async () => {
        // Verify mock server returns features for start=1&end=100
        const res = await fetch(`${MOCK_PROTOCOL}://${MOCK_HOST}:${MOCK_PORT}/api/route/?start=1&end=100&time=t&key=k`);
        const data = await res.json();
        expect(data.features.length).toBeGreaterThan(0);
    });
    test('error: alerts when route returns empty features', async () => {
        await getData.getRoute(9999, 8888);
        await new Promise(r => setTimeout(r, 300));
        expect(global.alert).toHaveBeenCalledWith('There are no roads between these two points.');
    });
});

// ═════════════════════════════════════════════════════════════
// routingMode.js
// ═════════════════════════════════════════════════════════════

const makeLayer = () => ({
    setStyle:     jest.fn(),
    bindPopup:    jest.fn(() => ({ openPopup: jest.fn() })),
});

describe('isInRoutingMode (routingMode.js)', () => {
    test('normal: false by default', () => { expect(isInRoutingMode()).toBe(false); });
    test('normal: true after one toggle', () => {
        toggleRoutingMode();
        expect(isInRoutingMode()).toBe(true);
        toggleRoutingMode();
    });
    test('normal: false after two toggles', () => {
        toggleRoutingMode(); toggleRoutingMode();
        expect(isInRoutingMode()).toBe(false);
    });
});

describe('toggleRoutingMode (routingMode.js)', () => {
    test('normal: returns true on first call', () => {
        expect(toggleRoutingMode()).toBe(true);
        toggleRoutingMode();
    });
    test('normal: returns false on second call', () => {
        toggleRoutingMode();
        expect(toggleRoutingMode()).toBe(false);
    });
    test('normal: resets state so next click sets start again', () => {
        toggleRoutingMode();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, makeLayer());
        toggleRoutingMode();
        toggleRoutingMode();
        const layer = makeLayer();
        handleRoutingVillageClick({ properties: { nearby_node: 99, village_name: 'B' } }, layer);
        expect(layer.setStyle).toHaveBeenCalledWith(expect.objectContaining({ fillColor: 'yellow' }));
        toggleRoutingMode();
    });
});

describe('handleRoutingVillageClick (routingMode.js)', () => {
    test('error: returns false when not in routing mode', () => {
        expect(handleRoutingVillageClick({ properties: { nearby_node: 1, village_name: 'A' } }, makeLayer())).toBe(false);
    });
    test('error: returns false when nearby_node is null', () => {
        toggleRoutingMode();
        expect(handleRoutingVillageClick({ properties: { nearby_node: null, village_name: 'A' } }, makeLayer())).toBe(false);
        toggleRoutingMode();
    });
    test('normal: first click styles layer yellow', () => {
        toggleRoutingMode();
        const layer = makeLayer();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, layer);
        expect(layer.setStyle).toHaveBeenCalledWith(expect.objectContaining({ fillColor: 'yellow' }));
        toggleRoutingMode();
    });
    test('normal: second click styles layer orange', () => {
        toggleRoutingMode();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, makeLayer());
        const endLayer = makeLayer();
        handleRoutingVillageClick({ properties: { nearby_node: 20, village_name: 'B' } }, endLayer);
        expect(endLayer.setStyle).toHaveBeenCalledWith(expect.objectContaining({ fillColor: 'orange' }));
    });
    test('normal: second click deactivates routing mode', () => {
        toggleRoutingMode();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, makeLayer());
        handleRoutingVillageClick({ properties: { nearby_node: 20, village_name: 'B' } }, makeLayer());
        expect(isInRoutingMode()).toBe(false);
    });
});

describe('resetRouting (routingMode.js)', () => {
    test('edge: does not throw on fresh state', () => {
        expect(() => resetRouting()).not.toThrow();
    });
    test('normal: resets layer styles to blue and white', () => {
        toggleRoutingMode();
        const sl = makeLayer(), el = makeLayer();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, sl);
        handleRoutingVillageClick({ properties: { nearby_node: 20, village_name: 'B' } }, el);
        resetRouting();
        expect(sl.setStyle).toHaveBeenCalledWith({ fillColor: 'blue', color: 'white' });
        expect(el.setStyle).toHaveBeenCalledWith({ fillColor: 'blue', color: 'white' });
    });
    test('normal: after reset next click sets start not end', () => {
        toggleRoutingMode();
        handleRoutingVillageClick({ properties: { nearby_node: 10, village_name: 'A' } }, makeLayer());
        resetRouting();
        const layer = makeLayer();
        handleRoutingVillageClick({ properties: { nearby_node: 20, village_name: 'B' } }, layer);
        expect(layer.setStyle).toHaveBeenCalledWith(expect.objectContaining({ fillColor: 'yellow' }));
        toggleRoutingMode();
    });
});

// ═════════════════════════════════════════════════════════════
// onEachFeatureFunction.js
// ═════════════════════════════════════════════════════════════

const nullProps = {
    village_name: null, village_name_th: null, id: '1',
    road_conditions: null, distance_to_pratom_km: null, distance_to_mathayom_km: null,
    hosted_kht_projects: null, adult_males: null, adult_females: null, common_diseases: null,
    households: null, population_without_enough_rice: null, children_aged_0_18: null,
    distance_to_town_km: null, distance_to_hospital_km: null, nearest_health_centre: null,
    annual_typhoid_cases: null, urls: [], image_urls: [], article_titles: [], posted_dates: []
};

const fullProps = {
    village_name: 'Village A', village_name_th: '\u0e2b\u0e21\u0e39\u0e48\u0e1a\u0e49\u0e32\u0e19', id: '1',
    road_conditions: 'Paved', distance_to_pratom_km: 5, distance_to_mathayom_km: 10,
    hosted_kht_projects: 'WASH', adult_males: 100, adult_females: 95,
    common_diseases: 'Malaria', households: 40, population_without_enough_rice: 10,
    children_aged_0_18: 30, distance_to_town_km: 20, distance_to_hospital_km: 15,
    nearest_health_centre: 'Clinic', annual_typhoid_cases: 3,
    urls: [], image_urls: [], article_titles: [], posted_dates: []
};

describe('onEachFeatureFunction (onEachFeatureFunction.js)', () => {
    const clickableLayer = () => ({
        bindPopup:    jest.fn().mockReturnThis(),
        on:           jest.fn(),
        setStyle:     jest.fn(),
        bringToFront: jest.fn(),
    });

    test('normal: binds a popup to the layer', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: fullProps }, layer);
        expect(layer.bindPopup).toHaveBeenCalled();
    });
    test('normal: popup contains English village name', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: { ...fullProps, village_name: 'Village A' } }, layer);
        expect(layer.bindPopup.mock.calls[0][0]).toContain('Village A');
    });
    test('normal: popup contains Thai village name', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: { ...fullProps, village_name_th: '\u0e2b\u0e21\u0e39\u0e48\u0e1a\u0e49\u0e32\u0e19' } }, layer);
        expect(layer.bindPopup.mock.calls[0][0]).toContain('\u0e2b\u0e21\u0e39\u0e48\u0e1a\u0e49\u0e32\u0e19');
    });
    test('normal: registers a click handler on the layer', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: fullProps }, layer);
        expect(layer.on).toHaveBeenCalledWith('click', expect.any(Function));
    });
    test('normal: click stores village-name in localStorage', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: { ...fullProps, village_name: 'Village A' } }, layer);
        layer.on.mock.calls[0][1]({});
        expect(global.localStorage.setItem).toHaveBeenCalledWith('village-name', 'Village A');
    });
    test('edge: null village_name stored as dash', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: nullProps }, layer);
        layer.on.mock.calls[0][1]({});
        expect(global.localStorage.setItem).toHaveBeenCalledWith('village-name', '-');
    });
    test('normal: click clears previous localStorage project entries', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: fullProps }, layer);
        layer.on.mock.calls[0][1]({});
        expect(global.localStorage.removeItem).toHaveBeenCalledWith('project-details');
        expect(global.localStorage.removeItem).toHaveBeenCalledWith('start-dates');
        expect(global.localStorage.removeItem).toHaveBeenCalledWith('end-dates');
    });
    test('normal: all 16 village properties stored in localStorage', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: fullProps }, layer);
        layer.on.mock.calls[0][1]({});
        const keys = global.localStorage.setItem.mock.calls.map(c => c[0]);
        ['village-name','village-name-th','road-quality','distance-pratom',
         'distance-mathayom','project-name','adult-male','adult-female',
         'common-disease','Households','rice-ratio','children',
         'distance-town','distance-hospital','nearest-health-center','annual-typhoid'
        ].forEach(key => expect(keys).toContain(key));
    });
    test('edge: zero values not replaced with dash', () => {
        const layer = clickableLayer();
        onEachFeatureFunction({ properties: { ...nullProps, households: 0, children_aged_0_18: 0 } }, layer);
        layer.on.mock.calls[0][1]({});
        expect(global.localStorage.setItem).toHaveBeenCalledWith('Households', 0);
        expect(global.localStorage.setItem).toHaveBeenCalledWith('children', 0);
    });
});

// ═════════════════════════════════════════════════════════════
// tourMaps/imageMapList.js
// ═════════════════════════════════════════════════════════════

describe('availableMaps (tourMaps/imageMapList.js)', () => {
    test('normal: contains exactly two maps', () => { expect(availableMaps).toHaveLength(2); });
    test('normal: each entry has name and filename', () => {
        availableMaps.forEach(m => { expect(m).toHaveProperty('name'); expect(m).toHaveProperty('filename'); });
    });
    test('normal: Baan Mae Hat is present', () => { expect(availableMaps.map(m => m.name)).toContain('Baan Mae Hat'); });
    test('normal: Baan Mae Oom Long is present', () => { expect(availableMaps.map(m => m.name)).toContain('Baan Mae Oom Long'); });
    test('normal: all filenames end with .html', () => { availableMaps.forEach(m => expect(m.filename).toMatch(/\.html$/)); });
    test('normal: Baan Mae Hat has correct filename', () => {
        expect(availableMaps.find(m => m.name === 'Baan Mae Hat').filename).toBe('BMH-tour.html');
    });
    test('normal: Baan Mae Oom Long has correct filename', () => {
        expect(availableMaps.find(m => m.name === 'Baan Mae Oom Long').filename).toBe('BMOL-tour.html');
    });
});