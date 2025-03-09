// get_data.js is the file that stores all of the base API calls and functions that are used to get data from the API
//               Refactored from the work of of the previous team by Sunidhi Pruthikosit 
//               Mar 10, 2025

import { map, layerControl, port, host, protocol, getCurrentTime} from "./index.js"
import { onEachFeatureFunction } from './onEachFeatureFunction.js';

/* for use with getVillageData and fetchInitialVillageData */
var firstLoad = true;
var VillageData;
var done = true; 
var last = [' ', ' '];

/* global variables for storing layers */
var mhsWater;
var mhsWaterlines;
var mhsRoads;
var mhsHospital;
var mhsSchool;
var mhsDistrict;
var mhsSubdistrict;

/* ==========================================
                    MARKER
=============================================*/

var Hospital_Icon = L.icon({
    iconUrl: 'img/hospital_marker.png',
    iconSize: [30, 30],
});

var School_Icon = L.icon({
    iconUrl: 'img/school_marker.png',
    iconSize: [40, 40],
});

/* ==========================================
            Get Village data from api
=============================================*/

async function getVillageData(url, villagePointColor) {
    if (done == true) { 
        done = false;
        // close old village points
        if (VillageData) {
            map.removeLayer(VillageData);
        } 
        const response = await fetch(url);
        const data = await response.json();
        let data_length = data.features.length;
        //if the data is empty, alert the user. after user clicks ok on alert, set done to true and return
        if (data_length == 0 && firstLoad == false) {
            alert("No Villages data found");
            fetchInitialVillageData();
            done = true;
            return;
        }

        VillageData = L.geoJSON(data, {
            pointToLayer: function (feature, latlng) {
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: villagePointColor,
                    color: 'white',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.7
                });
            },
            onEachFeature: onEachFeatureFunction
        }).addTo(map);
        done = true;
        if (last[0] != ' ' && last[1] != ' ') {
            getVillageData(last[0], last[1]);
            last[0] = ' '
            last[1] = ' '
        }
        firstLoad = false; 
    }   
    else {
        last[0] = url;
        last[1] = villagePointColor;
    }
}

async function fetchInitialVillageData() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/village/?time=${time}&key=${hash}`;
        getVillageData(url, 'blue')
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}
fetchInitialVillageData();

/* Call api to get the water areas */
async function getWaterAreas() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_water_areas/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsWater = L.geoJSON(data, {
                    style: function (feature) {
                        return { color: "blue" };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsWater, 'Water Area');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the water lines */
async function getWaterLines() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_water_lines/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsWaterlines = L.geoJSON(data, {
                    style: function (feature) {
                        return { color: "steelblue" };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsWaterlines, 'Water Lines');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the roads */
async function getRoads() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_roads/?time=${time}&key=${hash}`;
        // Add other layers to the map and the layer control
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsRoads = L.geoJSON(data, {
                    style: function (feature) {
                        return {
                            color: "brown",
                            fillOpacity: 0.5
                        };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsRoads, 'Roads');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the hospitals */
async function getHospitals() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/hospital/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsHospital = L.geoJSON(data, {
                    pointToLayer: function (feature, latlng) {
                        return L.marker(latlng, { icon: Hospital_Icon });
                    },
                    onEachFeature: function (feature, layer) {
                        var popupContent = (feature.properties['hospital_name']);
                        layer.bindPopup(popupContent);
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsHospital, 'Hospital');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the schools */
async function getSchools() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/school/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsSchool = L.geoJSON(data, {
                    pointToLayer: function (feature, latlng) {
                        return L.marker(latlng, { icon: School_Icon });
                    },
                    onEachFeature: function (feature, layer) {
                        layer.bindPopup(feature.properties["school_name"]);
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsSchool, 'School');
            })
            .catch(error => console.error('Error:', error));
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the districts */
async function getDistricts() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_districts/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsDistrict = L.geoJSON(data, {
                    style: {
                        color: '#FA8072',
                        opacity: 1,
                        fill: false
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsDistrict, 'Districts');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

/* Call api to get the subdistricts */
async function getSubDistricts() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_subdistricts/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsSubdistrict = L.geoJSON(data, {
                    style: {
                        color: 'pink',
                        opacity: 1,
                        fill: false
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsSubdistrict, 'Subdistricts');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        }
        else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

export default {
    getVillageData,
    fetchInitialVillageData,
    getWaterAreas,
    getWaterLines,
    getRoads,
    getHospitals,
    getSchools,
    getDistricts,
    getSubDistricts
}

