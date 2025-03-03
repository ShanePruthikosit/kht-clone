// index.js is the main file that contains the code for the KHT homepage. 
// It imports the necessary libraries and components, and renders the main App component.
//  It also contains the code for the map and the sidebar.
//               Created by Krittin Kamolpornwijit & Ittiphat Kijpaisansak & Tatchphol Charoensupthaworn
//                       Oct 6, 2023 

/* ==========================================
    Imports
=============================================*/
import getData from './get_data.js'

/* ==========================================
    Prevent leaflet default marker showing up on the map
=============================================*/

 // Create a custom transparent icon
 var transparentIcon = L.icon({
    iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/wcAAwAB/olEf4sAAAAASUVORK5CYII=', // 1x1 transparent image
    iconSize: [1, 1], 
});

// Override the default icon
L.Marker.prototype.options.icon = transparentIcon;

/* ==========================================
    Function - Generate time stamp
=============================================*/
function getCurrentTime() {
    const now = new Date();
    const hours = now.getHours().toString().padStart(2, '0');
    const minutes = now.getMinutes().toString().padStart(2, '0');
    const seconds = now.getSeconds().toString().padStart(2, '0');
    return `${hours}-${minutes}-${seconds}`;
}
const globalDate = new Date();
const minimumYear = 2000;
const currentYear = globalDate.getFullYear();

/* ==========================================
            Endpoint url configuration
=============================================*/
const host = 'kht-map.org';
const port = '2546';
const protocol = 'https';
// const url = `${protocol}://${host}:${port}/api/option/?time=${time}&key=${hash}` for testing

var map = L.map('map').setView([18.7370, 97.8722], 9.45);
var scale = L.control.scale({
    position: 'bottomleft',
    imperial: true
}).addTo(map);

/* ==========================================
            TILE LAYER and WMS
=============================================*/

// osm layer
var osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);
osm.addTo(map);

// water color
var watercolor = L.tileLayer('https://tiles.stadiamaps.com/tiles/stamen_watercolor/{z}/{x}/{y}.{ext}', {
    attribution: '&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> &copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> &copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    subdomains: 'abcd',
    minZoom: 1,
    maxZoom: 16,
    ext: 'jpg'
});
// watercolor.addTo(map)

// dark map
var dark = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
});
// dark.addTo(map)

var nexrad = L.tileLayer.wms("http://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi", {
    layers: 'nexrad-n0r-900913',
    format: 'image/png',
    transparent: true,
    attribution: "Weather data © 2012 IEM Nexrad"
});

/* ==========================================
     Toggle Instruction, legend, and Layers
=============================================*/

document.addEventListener("DOMContentLoaded", function() {
    // Toggle Instruction //
    const toggleButton = document.querySelector('.toggle-instruction');
    // Called from the iframe
    let insExpanded = true;
    if (toggleButton != null) {
        toggleButton.addEventListener('click', function() {
            const img = toggleButton.querySelector('img');
            if (insExpanded) {
                img.style.transform = 'rotate(0deg)';
                let message = JSON.stringify({
                    message: insExpanded,
                });
                window.parent.postMessage(message, '*');
                insExpanded = false;
            } else {
                img.style.transform = 'rotate(180deg)';
                let message = JSON.stringify({
                    message: insExpanded,
                });
                window.parent.postMessage(message, '*');
                insExpanded = true;
            }
        });
    }

    // Toggle Legend -  old version with arrow*
    // const legendButton = document.querySelector('.toggle-legend');
    // const legendDiv = document.querySelector('.leaflet-bottom.leaflet-right');
    // let legExpanded = true;
    // if (legendButton != null) {
    //     legendButton.addEventListener('click', function() {
    //         const img = legendButton.querySelector('img');
    //         if (legExpanded) {
    //             img.style.transform = 'rotate(270deg)';
    //             legendDiv.style = "bottom: -350px"
    //             legExpanded = false;
    //         } else {
    //             img.style.transform = 'rotate(90deg)';
    //             legendDiv.style = "bottom: "
    //             legExpanded = true;
    //         }
    //     });
    // }

    const legendButton = document.querySelector('.toggle-legend');
    const legendDiv = document.querySelector('.legend'); 
    const bottomright = document.querySelector('.leaflet-bottom.leaflet-right');
    const newLegendbutton = document.createElement("button");
    newLegendbutton.className =  "leaflet-control-layers-toggle leaflet-control";
    bottomright.appendChild(newLegendbutton);
    
    // Initialize the visibility states
    legendDiv.style.visibility = 'visible';
    newLegendbutton.style.visibility = 'hidden';
    newLegendbutton.style.top = '70%';
    
    if (legendButton) {
        legendButton.addEventListener('click', function() {
            if (legendDiv.style.visibility === 'visible') {
                legendDiv.style.visibility = 'hidden';
                newLegendbutton.style.visibility = 'visible';
            } else {
                legendDiv.style.visibility = 'visible';
                newLegendbutton.style.visibility = 'hidden';
            }
        });
    }
    
    if (newLegendbutton) {
        newLegendbutton.addEventListener('click', function() {
            legendDiv.style.visibility = 'visible';
            newLegendbutton.style.visibility = 'hidden';
        }); 
    }
    // Toggle Layer //
    const layerButton = document.querySelector('.toggleLayerControlButton');
    const layerControlContainer = layerControl.getContainer(); 
    const topright = document.querySelector('.leaflet-top.leaflet-right');
    const newLayerbutton = document.createElement("button");
    newLayerbutton.className = "leaflet-control-layers-toggle leaflet-control newLayerButtonStyle";
    if (topright.firstChild) { //add new layer button to the top of the layer control
        topright.insertBefore(newLayerbutton, topright.firstChild); 
    } else {
        topright.appendChild(newLayerbutton); //
    }
    if (layerButton != null)
    {
        layerButton.addEventListener('click', function() {
            layerControlContainer.style = "visibility: hidden;"
            newLayerbutton.style = "visibility: visible;"
        });
    }
    if (newLayerbutton != null)
    {
        newLayerbutton.addEventListener('click', function() {
            layerControlContainer.style = "visibility: visible;"
            newLayerbutton.style = "visibility: hidden;"
        }); 
    }
    // Create a new layer control that is collapsible
    // layerControl = L.control.layers(baseMaps, overlayMaps, { collapsed: true }).addTo(map);
});

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
                    GEOJSON
=============================================*/

// This is the working layer but it need to be in the data file which is js file
var baseMaps = {
    "OSM": osm,
    'Dark': dark,
};

var layerControl = L.control.layers(baseMaps, overlayMaps, { collapsed: false }).addTo(map);
var legendControl = L.control({ position: 'bottomright' });
var layerControlContainer = layerControl.getContainer(); // Get the layer control's HTML container

// Create a new div for the title
var titleDiv = L.DomUtil.create('div', 'layer-control-title');
titleDiv.textContent = 'Layers';
layerControlContainer.insertBefore(titleDiv, layerControlContainer.firstChild);

legendControl.onAdd = function (map) {
    var div = L.DomUtil.create('div', 'legend');
    // div.style = "width: 150px; font-size: 10px; height:340px";
    div.innerHTML +=
        '<div style="width: 100%; height: 10%; display: flex;"><div style="width: 85%; align-items: center; display: flex;"><strong>Legend</strong></div>' +
        // '<button class="toggle-legend"><img src="img/next-single-arrow.png" width = "100%" height = "70%" style="transform: rotate(90deg);"></button></div>' +
       '<button class="toggle-legend" style="width: 20%; height: 65%; font-size: 115%; border-radius: 20%; border: 1px solid grey; color: black; background-color: paleturquoise; margin: 5px;"">X</button></div>' +
        '<img src="img/DEM.png" alt="Elevation" height="5%"> Terrain<br>' +
        '<img src="img/elevation.png" alt="Monochrome Elevation" height="5%"> Terrain (Monochrome)<br>' +
        '<svg height="2vw" width="2vw"><circle cx="1vw" cy="1vw" r="0.8vw" stroke-width: 0.5vw; style="fill: blue; stroke: white;"></circle></svg> Village<br>' +
        '<svg height="2vw" width="2vw"><circle cx="1vw" cy="1vw" r="0.8vw" stroke-width: 0.5vw; style="fill: red; stroke: white;"></circle></svg> Village Clicked<br>' +
        '<svg height="2vw" width="2vw"><circle cx="1vw" cy="1vw" r="0.8vw" stroke-width: 0.5vw; style="fill: green; stroke: white;"></circle></svg> Village from search result<br>' +
        '<svg height="20" width="20"><line x1="0" y1="10" x2="20" y2="10" style="stroke:pink;stroke-width:2"></line></svg> Subdistrict<br>' +
        '<svg height="20" width="20"><line x1="0" y1="10" x2="20" y2="10" style="stroke:#FA8072;stroke-width:2"></line></svg> District<br>' +
        '<img src="img/school_marker.png" alt="School" height="5%"> School<br>' +
        '<img src="img/hospital_marker.png" alt="Hospital" height="5%"> Hospital<br>' +
        '<svg height="20" width="20"><line x1="0" y1="10" x2="20" y2="10" style="stroke:brown;stroke-width:2"></line></svg> Road<br>' +
        '<svg height="20" width="20"><line x1="0" y1="10" x2="20" y2="10" style="stroke:steelblue;stroke-width:2"></line></svg> Water Line<br>' +
        '<svg height="20" width="20"><line x1="0" y1="10" x2="20" y2="10" style="stroke:blue;stroke-width:2"></line></svg> Water Area<br>' +
        '<div style="width: 10vw height: 20vw" class="logo-container"><a href="https://www.cmkl.ac.th/" target="_blank"><img width="100%" height="10%" src="img/LogoCMKL.png" alt="Logo" class="logo"></a></div>';
    return div;
};  

// Add the legend control to the map
legendControl.addTo(map);

// Wait for the layer control to be added to the map
setTimeout(function () {
    // Get the layer control's HTML container
    var layerControlContainer = layerControl.getContainer();

    // Create a new button element
    var button = document.createElement('button');
    button.className = 'toggleLayerControlButton';
    button.textContent = 'X';

// Assuming layerControlContainer and button are valid DOM elements
layerControlContainer.style.position = 'relative';




layerControlContainer.appendChild(button);
}, 0);

// var elevation = L.imageOverlay('img/elevation.png', [[19.815284943, 97.343636681], [17.636673832, 98.651692237]], { interactive: false, opacity: 0.7 }).addTo(map);
var elevationColor = L.imageOverlay('img/DEM.png', [[19.815284943, 97.343636681], [17.636673832, 98.651692237]], { interactive: false, opacity: 0.4 }).addTo(map);
var elevavtionMono = L.imageOverlay('img/elevation.png', [[19.815284943, 97.343636681], [17.636673832, 98.651692237]], { interactive: false, opacity: 0.7 }).addTo(map);

// Add the new layers to the layer control
layerControl.addOverlay(elevationColor, 'Terrain');
layerControl.addOverlay(elevavtionMono, 'Terrain (Monochrome)');
// layerControl.addOverlay(subdistrict, 'Subdistrict');

var layers = {};

// /* Call api to get the water areas */
// async function getWaterAreas() {
//     try {
//         const time = getCurrentTime();
//         const hash = await getTestPackage(time);
//         const url = `${protocol}://${host}:${port}/api/mhs_water_areas/?time=${time}&key=${hash}`;
//         fetch(url)
//             .then(response => response.json())
//             .then(data => {
//                 mhswater = L.geoJSON(data, {
//                     style: function (feature) {
//                         return { color: "blue" };
//                     }
//                 }).addTo(map);

//                 // Add the new layer to the layer control
//                 layerControl.addOverlay(mhswater, 'Water Area');
//             });
//     } catch (error) {
//         if (error.name === 'AbortError') {
//             console.log('Fetch aborted');
//         } else {
//             console.error('Error fetching GeoJSON:', error);
//         }
//     }
// }
// getWaterAreas();

/* Call api to get the water lines */
async function getWaterLines() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_water_lines/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhswaterlines = L.geoJSON(data, {
                    style: function (feature) {
                        return { color: "steelblue" };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhswaterlines, 'Water Lines');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}
getWaterLines();

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
                mhsroads = L.geoJSON(data, {
                    style: function (feature) {
                        return {
                            color: "brown",
                            fillOpacity: 0.5
                        };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsroads, 'Roads');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}
getRoads();

/* Call api to get the hospitals */
async function getHospitals() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/hospital/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                hospital = L.geoJSON(data, {
                    pointToLayer: function (feature, latlng) {
                        return L.marker(latlng, { icon: Hospital_Icon });
                    },
                    onEachFeature: function (feature, layer) {
                        var popupContent = (feature.properties['hospital_name']);
                        layer.bindPopup(popupContent);
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(hospital, 'Hospital');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}
getHospitals()

/* Call api to get the districts */
async function getDistricts() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_districts/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhsdistrict = L.geoJSON(data, {
                    style: {
                        color: '#FA8072',
                        opacity: 1,
                        fill: false
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhsdistrict, 'Districts');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}
getDistricts();

/* Call api to get the subdistricts */
async function getSubDistricts() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_subdistricts/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhssubdistrict = L.geoJSON(data, {
                    style: {
                        color: 'pink',
                        opacity: 1,
                        fill: false
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(mhssubdistrict, 'Subdistricts');
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
getSubDistricts();

/* Call api to get the schools */
async function getSchools() {
    try {
        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/school/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                schoolLayer = L.geoJSON(data, {
                    pointToLayer: function (feature, latlng) {
                        return L.marker(latlng, { icon: School_Icon });
                    },
                    onEachFeature: function (feature, layer) {
                        layer.bindPopup(feature.properties["school_name"]);
                    }
                });

                // Add the new layer to the layer control
                layerControl.addOverlay(schoolLayer, 'School');
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
getSchools();

/*
Function - to get info to display on the left sidebar 
every time a village is clicked
Arguments:
    feature - the feature that is clicked
    layer - the layer that is clicked
*/
function onEachFeatureFunction(feature, layer) {
    layer.bindPopup(feature.properties.village_name);
    layer.on('click', function (e) {
        // Reset the style of the previously clicked layer
        resetClickedLayer();
        // Clear the relevant localStorage items
        localStorage.removeItem('project-details');
        localStorage.removeItem('start-dates');
        localStorage.removeItem('end-dates');
        localStorage.removeItem('project-types');
        localStorage.removeItem('status-names');
        localStorage.removeItem('url');
        localStorage.removeItem('image_urls');
        localStorage.removeItem('article_titles');
        localStorage.removeItem('posted_dates');

        // Change the marker color to red
        layer.setStyle({ fillColor: 'red', color: 'white' });

        // Bring the clicked layer to the front
        layer.bringToFront();

        // Store the currently clicked layer
        clickedLayer = layer;
        const id = feature.properties["id"];
        localStorage.setItem('id', id);

        /* Call api to get the project data */
        async function fetchProjectDataWithVillageID(id) {
            try {
                const time = getCurrentTime();
                const hash = await getTestPackage(time);
                const url = `${protocol}://${host}:${port}/api/project/?village_id=${id}&time=${time}&key=${hash}`;
                const response = await fetch(url);
                // const response = await fetch("https://172.105.120.121:443/api/project/?village_id=" + id); old version
                const data = await response.json();

                data.features.forEach(feature => {
                    const projectDetail = feature.properties.project_name_en;
                    // Get the existing data from local storage
                    let projectDetails = JSON.parse(localStorage.getItem('project-details')) || [];

                    // Add the new project detail to the array
                    projectDetails.push(projectDetail);

                    // Store the updated array in local storage
                    localStorage.setItem('project-details', JSON.stringify(projectDetails));
                    const startDate = feature.properties.start_date;

                    // Get the existing data from local storage
                    let startDates = JSON.parse(localStorage.getItem('start-dates')) || [];
                    // Add the new start date to the array
                    startDates.push(startDate);

                    // Store the updated array in local storage
                    localStorage.setItem('start-dates', JSON.stringify(startDates));

                    const endDate = feature.properties.end_date;
                    // Get the existing data from local storage
                    let endDates = JSON.parse(localStorage.getItem('end-dates')) || [];

                    // Add the new end date to the array
                    endDates.push(endDate);

                    // Store the updated array in local storage
                    localStorage.setItem('end-dates', JSON.stringify(endDates));

                    const projectType = feature.properties.project_type;
                    // Get the existing data from local storage
                    let projectTypes = JSON.parse(localStorage.getItem('project-types')) || [];
                    // Add the new project type to the array
                    projectTypes.push(projectType);
                    // Store the updated array in local storage
                    localStorage.setItem('project-types', JSON.stringify(projectTypes));

                    const statusName = feature.properties.status_name;
                    // Get the existing data from local storage
                    let statusNames = JSON.parse(localStorage.getItem('status-names')) || [];
                    // Add the new status name to the array
                    statusNames.push(statusName);
                    // Store the updated array in local storage
                    localStorage.setItem('status-names', JSON.stringify(statusNames));
                });
            } catch (error) {
                console.error('Error:', error);
            }
        }
        fetchProjectDataWithVillageID(id);

        const villageName = feature.properties["village_name"];
        localStorage.setItem('village-name', villageName === null ? '-' : villageName);

        const roadQuality = feature.properties["road_conditions"];
        localStorage.setItem('road-quality', roadQuality === null ? '-' : roadQuality);

        const distancePratom = feature.properties["distance_to_pratom_km"];
        localStorage.setItem('distance-pratom', distancePratom === null ? '-' : distancePratom);

        const distanceMathayom = feature.properties["distance_to_mathayom_km"];
        localStorage.setItem('distance-mathayom', distanceMathayom === null ? '-' : distanceMathayom);

        const projectName = feature.properties["hosted_kht_projects"];
        localStorage.setItem('project-name', projectName === null ? '-' : projectName);

        const adultmale = feature.properties["adult_males"];
        localStorage.setItem('adult-male', adultmale === null ? '-' : adultmale);

        const adultfemale = feature.properties["adult_females"];
        localStorage.setItem('adult-female', adultfemale === null ? '-' : adultfemale);

        const commonDisease = feature.properties["common_diseases"];
        localStorage.setItem('common-disease', commonDisease === null ? '-' : commonDisease);

        const Households = feature.properties["households"];
        localStorage.setItem('Households', Households === null ? '-' : Households);

        const riceRatio = feature.properties["population_without_enough_rice"];
        localStorage.setItem('rice-ratio', riceRatio === null ? '-' : riceRatio);

        const children = feature.properties["children_aged_0_18"];
        localStorage.setItem('children', children === null ? '-' : children);

        const distanceTown = feature.properties["distance_to_town_km"];
        localStorage.setItem('distance-town', distanceTown === null ? '-' : distanceTown);

        const distanceHospital = feature.properties["distance_to_hospital_km"];
        localStorage.setItem('distance-hospital', distanceHospital === null ? '-' : distanceHospital);

        const nearestHealthCenter = feature.properties["nearest_health_centre"];
        localStorage.setItem('nearest-health-center', nearestHealthCenter === null ? '-' : nearestHealthCenter);

        const annualTyphoid = feature.properties["annual_typhoid_cases"];
        localStorage.setItem('annual-typhoid', annualTyphoid === null ? '-' : annualTyphoid);
        
        const urls = feature.properties["urls"];
        const imageUrls = feature.properties["image_urls"];
        const articleTitles = feature.properties["article_titles"];
        const postedDates = feature.properties["posted_dates"];
        localStorage.setItem('url', JSON.stringify(urls));
        localStorage.setItem('image_urls', JSON.stringify(imageUrls));
        localStorage.setItem('article_titles', JSON.stringify(articleTitles));
        localStorage.setItem('posted_dates', JSON.stringify(postedDates));

    });
}


// Variable to store the currently clicked layer
var clickedLayer;

// Function to reset the style of the previously clicked layer
function resetClickedLayer() {
    if (clickedLayer) {
        clickedLayer.setStyle({ fillColor: 'blue', color: 'white' });
    }
}

// Define a new control
var RecenterControl = L.Control.extend({
    options: {
        position: 'topleft' // Position of the control
    },

    onAdd: function (map) {
        // Create an img element
        var img = L.DomUtil.create('img');

        // Set the source of the image
        img.src = 'img/re-center.png';

        // Set the width and height of the image
        img.style.width = '32px';
        img.style.height = '32px';

        img.style.borderRadius = '10%';

        // Add a border to the image
        img.style.border = '1.1px white';

        // Attach the onclick event to the image
        img.onclick = function () {
            map.setView([18.7370, 97.8722], 9.45); // Recenter the map
        }

        return img;
    }
});


// Add the control to the map
new RecenterControl().addTo(map);

// Create a new control
// Global most usable object
var YearBoxControl = L.control({ position: 'topleft' });
var rangeInput = null;
var yearSliderContainer = null;
var yearText = null;
// When the control is added to the map
YearBoxControl.onAdd = function (map) {
    // Create a div for the control
    var div = L.DomUtil.create('div', 'year-box-control');
    div.className = "leaflet-control-layers leaflet-control-layers-expanded";
    div.id = "year-slider-container";
    div.style = "width: 30%; font-size: 1.7vw; visibility: hidden;";
    // Create element inside
    var container = L.DomUtil.create('div', 'slidecontainer', div);
    rangeInput = L.DomUtil.create('input', 'year-slider', container);
    rangeInput.type = "range";
    rangeInput.min = "1992";
    rangeInput.max = "2000";
    rangeInput.value = "1992";
    rangeInput.style.width = "100%";
    var paragraph = L.DomUtil.create('p', '', container);
    paragraph.textContent = "Year: ";
    var yearSpan = L.DomUtil.create('span', '', paragraph);
    yearSpan.id = "yearText";
    yearSpan.textContent = "1992";
    // var closeCenter = L.DomUtil.create('center', '', container);
    // var closeButton = L.DomUtil.create('button', 'closeYear', closeCenter);
    // closeButton.style.width = "70%";
    // closeButton.style.height = "20%";
    // closeButton.style.fontSize = "1.7vw";
    // closeButton.textContent = "Close";

    // Add event listeners directly to the control's DOM elements
    rangeInput.addEventListener('mouseover', function () {
        map.dragging.disable();
    });

    rangeInput.addEventListener('mouseout', function () {
        map.dragging.enable();
    });
    var targetYear
    rangeInput.oninput = function() {
        yearSpan.innerHTML = this.value;
        targetYear = parseInt(this.value);
        /* Call api to get the village data */
        async function fetchVillagebByYear() {
            // Remove the VillageData layer
            map.removeLayer(VillageData);
            
            try {
                const time = getCurrentTime();
                const hash = await getTestPackage(time);
                const url = `${protocol}://${host}:${port}/api/village/?year=${targetYear}&time=${time}&key=${hash}`;
                getData.getVillageData(url, 'green')
            } catch (error) {
                console.error('Error:', error);
            }
        }
        fetchVillagebByYear();
    }

    // closeButton.addEventListener('click', function() {
    //     div.style.visibility = "hidden";
    // });
    yearSliderContainer = div;
    yearText = yearSpan;
    return div;
};

YearBoxControl.addTo(map);

/* ==========================================
        Search Button Control
=============================================*/
var radioButtonControl = L.control({ position: 'topleft' });

// When the control is added to the map
radioButtonControl.onAdd = function (map) {
    // Create a div for the control
    var div = L.DomUtil.create('div', 'radio-button-control');
    // Add a radio button to the div and initially hide them
    div.innerHTML = `
        <div id="radioContainer" style="display: none;">
        <strong><p>Search for Village by</p></strong><br>

        <input type="radio" id="radio1" name="radio" value="radio1">
        <label for="radio1">Year</label>
        <input type="number" size="10" style="margin-left: 20px; width: 30%;" id="input1"><br style="margin-bottom: 20px;">
        
        <input type="radio" id="radio2" name="radio" value="radio2">
        <label for="radio2">Start Year - End Year</label><input type="number" size="10" style="margin-left: 20px; width: 20%;" id="input2">
        <input type="number" size="10" style="margin-left: 20px; width: 20%;" id="input3"><br style="margin-bottom: 20px;">
        
        <input type="radio" id="radio3" name="radio" value="radio3">
        <label for="radio3">Project Type</label>
        <select id="input4" style="margin-left: 20px; margin-bottom: 20px; width: 80%">
        <option value=" ">Select a project type</option>
        <option value="WASH">WASH</option>
        <option value="Further Education Scholarship">Further Education Scholarship</option>
        <option value="Irrigation">Irrigation</option>
        <option value="Dormitory Meals">Dormitory Meals</option>
        </select><br style="margin-bottom: 20px;">

        <input type="radio" id="radio4" name="radio" value="radio4">
        <label for="radio4">Minimum Distance(Km)</label>
        <input type="number" size="10" style="margin-left: 20px; width: 20%;" id="input5"><br style="margin-bottom: 20px;">
        <label for="radio4" style="margin-left: 20px;">Facility Type</label>
        <select id="input6" style="margin-left: 20px; margin-bottom: 20px;">
        <option value=" ">Select a facility Type</option>
        <option value="school">School</option>
        <option value="hospital">Hospital</option>
        </select><br style="margin-bottom: 20px;">
        <button id="searchButton" style="margin-left: 80px;">Search</button>
        <button id="cancelButton" style="margin-left: 10px;">Cancel</button>
        <button id="clearButton" style="margin-left: 10px;">Clear</button>
        </div>
    `;
   
    // Attach event listener to the clear button
    div.querySelector('#clearButton').addEventListener('click', function () {
        // Clear the input fields
        document.getElementById('input1').value = '';
        document.getElementById('input2').value = '';
        document.getElementById('input3').value = '';
        document.getElementById('input4').value = ' ';
        document.getElementById('input5').value = '';
        document.getElementById('input6').value = ' ';
        
        getData.fetchInitialVillageData();
    });

    // Attach event listener to the cancel button
    div.querySelector('#cancelButton').addEventListener('click', function () {
        // Hide the radio button container
        var radioButtonContainer = document.querySelector('#radioContainer');
        if (radioButtonContainer) {
            radioButtonContainer.style.display = 'none';
        }

        // Show the search button container
        var searchButtonContainer = document.querySelector('.search-button-control');
        if (searchButtonContainer) {
            searchButtonContainer.style.display = 'block';
            div.style = "visibility: hidden;"
        }
    });

    // Attach event listener to the search button
    div.querySelector('#searchButton').addEventListener('click', function () {
        div.querySelector('#searchButton').removeEventListener('click', getData.fetchInitialVillageData);
        // Check which radio button is selected
        var selectedRadioButton = document.querySelector('input[name="radio"]:checked');
        if (selectedRadioButton) {
            // close square clutter
            div.style = "visibility: hidden;"

            // Get the id of the selected radio button
            var radioButtonId = selectedRadioButton.id;
            
            // Determine the id of the corresponding input field
            var inputId1, inputId2;
            var inputValue1, inputValue2;

            // Select the search button
            let searchButton = document.getElementById('searchButton'); // replace 'searchButton' with the actual ID of your search button
            var request = new XMLHttpRequest();
            
            switch (radioButtonId) {
                case 'radio1': /* get village by year */
                    inputId1 = 'input1';
                    inputValue1 = document.getElementById(inputId1).value;

                    // Year Validation
                    if (inputValue1 == "") {
                        alert("Please enter the target year.");
                        break;
                    }
                    if (inputValue1 < minimumYear || inputValue1 > currentYear) {
                        alert("The the target year must be in between " + minimumYear + " - "+ currentYear);
                        break;
                    }
                    async function fetchVillagebByYear() {
                        try {
                            const time = getCurrentTime();
                            const hash = await getTestPackage(time);
                            const url = `${protocol}://${host}:${port}/api/village/?year=${inputValue1}&time=${time}&key=${hash}`;
                            getData.getVillageData(url, 'green')
                        } catch (error) {
                            console.error('Error:', error);
                        }
                    }
                    fetchVillagebByYear();
                    break;
                case 'radio2': /* get village by start and end year */
                    var startYear = parseInt(document.getElementById('input2').value);
                    var endYear = parseInt(document.getElementById('input3').value);
                    
                    inputId2 = 'input2';
                    inputId3 = 'input3';
                    inputValue2 = document.getElementById(inputId2).value;
                    inputValue3 = document.getElementById(inputId3).value;
                    
                    // Year Validation
                    if (inputValue2 == "" || inputValue3 == "") {
                        console.log('start year and end year is empty');
                        alert("Please enter the start year and end year.");
                        break;
                    }
                    if (startYear > endYear) {
                        alert("The start year shoud be less than end year");
                        break;
                    }
                    if (startYear < minimumYear || endYear > currentYear) {
                        alert("The start year and end year \n should be in between " + minimumYear + " - "+ currentYear);
                        break;
                    }

                    // Create the container
                    let container = document.createElement('div');
                    container.style.border = '1px solid black';
                    container.style.padding = '10px';
                    container.style.marginTop = '10px';

                    // Add the years to the container
                    for(let i = inputValue2; i <= inputValue3; i++) {
                        container.innerHTML += `<p>${i}</p>`;
                    }

                    // Append the container to the body
                    document.body.appendChild(container);

                    // Open the year slider
                    if (yearSliderContainer != null && rangeInput != null && yearText != null)
                    {
                        yearSliderContainer.style.visibility = "visible";
                        rangeInput.min = String(startYear);
                        rangeInput.max = String(endYear);
                        rangeInput.value = String(startYear);
                        yearText.innerHTML = rangeInput.value;
                    }
                   
                    // fetch and get api data
                    async function fetchVillagebByStartAndEndYear() {
                        try {
                            const time = getCurrentTime();
                            const hash = await getTestPackage(time);
                            const url = `${protocol}://${host}:${port}/api/village/?start_year=${inputValue2}&end_year=${inputValue3}&time=${time}&key=${hash}`;
                            // fetch("https://kht-map.org:2546/api/village/?start_year=" + inputValue2 + "&end_year=" + inputValue3)
                            getData.getVillageData(url, 'green');
                        } catch (error) {
                            console.error('Error:', error);
                        }
                    }
                    fetchVillagebByStartAndEndYear();
                    break;
                case 'radio3': /* get village by project type */
                    const projectType = document.getElementById('input4').value;
                    if (projectType == " ") {
                        alert("Please select the project type.");
                        break;
                    }
                    async function fetchVillagebyProjectType() {
                        try {
                            const time = getCurrentTime();
                            const hash = await getTestPackage(time);

                            // check the input for project type
                            const projectTypeMapping = {
                                'WASH': 'WASH',
                                'Further Education Scholarship': 'Further%20Education%20Scholarships',
                                'Irrigation': 'Irrigation',
                                'Dormitory Meals': 'Dormitory%20Meals',
                                // 'School Buses': 'School%20Buses'
                            };

                            if (projectTypeMapping[projectType]) {
                                const url = `${protocol}://${host}:${port}/api/village/?project_type=${projectTypeMapping[projectType]}&time=${time}&key=${hash}`;
                                getVillageData(url, 'green')
                            }

                            inputId1 = 'input4';
                            inputValue1 = document.getElementById(inputId1).value;
                            searchButton.addEventListener('click', function () {

                            });
                        } catch (error) {
                            console.error('Error:', error);
                        }
                    }
                    
                    fetchVillagebyProjectType();
                    break;
                case 'radio4': /* get village by minimum distance and facility type */
                    var input5 = document.getElementById('input5');
                    var input6 = document.getElementById('input6');

                    if (input5 && input6) {
                        var inputValue5 = parseInt(input5.value);
                        var inputValue6 = input6.value;
                    }
                    console.log(inputValue5);
                    console.log(inputValue6);
                    //print type of 5
                    console.log(typeof inputValue5);

                    // Distance validation
                    if (isNaN(inputValue5)) {
                        alert("Please enter the minimum distance to find the villages.");
                        break;
                    }
                    if (inputValue5 < 0 || inputValue5 > 41) {
                        console.log('distance validation')
                        alert("The minimum distance should be larger than 0 and less than 41 km to get results");
                        break;
                    }
                    // Facility validation
                    if (inputValue6 == " ") {
                        alert("Please select facility type to find the minimum distance to villages");
                        break;
                    }

                    async function fetchVillageByDistance() {
                        try {
                            const time = getCurrentTime();
                            const hash = await getTestPackage(time);
                            const url = `${protocol}://${host}:${port}/api/village/?distance=${inputValue5}&facility_type=${inputValue6}&time=${time}&key=${hash}`;
                            getVillageData(url, 'green')
                        } catch (error) {
                            console.error('Error:', error);
                        }
                    }
                    fetchVillageByDistance();
                    break;
            }
            // Hide the radio button container
            var radioButtonContainer = document.querySelector('#radioContainer');
            if (radioButtonContainer) {
                radioButtonContainer.style.display = 'none';
            }

            // Show the search button container
            var searchButtonContainer = document.querySelector('.search-button-control');
            if (searchButtonContainer) {
                searchButtonContainer.style.display = 'block';
            }
        }
        else {
            alert("Please select one of the search option");
        }
    });

    // Prevent map interactions when interacting with the control
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.disableScrollPropagation(div);

    return div;
};

// Add the control to the map
radioButtonControl.addTo(map);


// Create a new search button icon
var searchButtonControl = L.control({ position: 'topleft' });

// When the control is added to the map
searchButtonControl.onAdd = function (map) {
    // Create a div for the control
    var div = L.DomUtil.create('div', 'search-button-control');

    // Add a button to the div
    div.innerHTML = '<button class="searchButtonControl" id="searchButton"><i class="material-icons">search</i></button>';

    // Add an event listener to the search button
    div.querySelector('#searchButton').addEventListener('click', function () {
        // Show the radio buttons when the search button is clicked
        var clutter = document.querySelector(".radio-button-control.leaflet-control");
        clutter.style = "visibility: visible;"
        var radioButtonContainer = document.querySelector('#radioContainer');
        if (radioButtonContainer) {
            radioButtonContainer.style.display = 'block';
            //make the search button and its container disappear
            var searchButtonContainer = document.querySelector('.search-button-control');
            if (searchButtonContainer) {
                searchButtonContainer.style.display = 'none';
            }
        }
        // Hide the year slider
        yearSliderContainer.style.visibility = "hidden";
    });

    return div;
};

// Add the control to the map
searchButtonControl.addTo(map);
// Add the control to the map
radioButtonControl.addTo(map);
// add the control to the map
YearBoxControl.addTo(map);

window.onload = function () {
    // Store the original state
    var form = document.getElementById('radioContainer');
    var originalState = form.choice.value;

    // Attach event listener to the cancel button
    document.getElementById('cancelButton').addEventListener('click', function () {
        // Revert to the original state
        form.choice.value = originalState;
    });
};
//window.addTo(map);

// Attach event listener to the search button
document.getElementById('searchButton').addEventListener('click', function () {
    // Check which radio button is selected
    var selectedRadioButton = document.querySelector('input[name="radio"]:checked');
    if (selectedRadioButton) {
        // Get the id of the selected radio button
        var radioButtonId = selectedRadioButton.id;

        // Determine the id of the corresponding input field
        var inputId;
        switch (radioButtonId) {
            case 'radio1':
                inputId = 'input1';
                break;
            case 'radio2':
                inputId = 'input2';
                break;
            case 'radio3':
                inputId = 'input3';
                break;
        }

        // Get the value of the corresponding input field
        var inputValue = document.getElementById(inputId).value;

        // Print the value
        console.log(inputValue);
    }
});

/* ==========================================
                LAYER CONTROL
=============================================*/
var overlayMaps = {
    // 'Terrain': elevationLayer,
    "Terrain (Monochrome)": null, //elevavtionMono,
    // 'Subdistrict': SubdistrictLayer,
    // 'District': mhsdistrict,
    'School': null, //schoolLayer,
    'Geographical Info': null, //  GeographicLayer,
    'Hospital': null, // hospital,
    // 'nexrad': nexrad
};








export { 
    map,
    host,
    port,
    protocol,
    getCurrentTime,
    onEachFeatureFunction
} 
