import { map, layerControl, port, host, protocol, getCurrentTime as getCurrentTime, onEachFeatureFunction as onEachFeatureFunction} from "./index.js"

/* ==========================================
            Get Village data from api
=============================================*/

var firstLoad = true;
var VillageData;
var done = true; 
var last = [' ', ' '];
var mhswater;

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

        if (mhswater) {
            map.removeLayer(mhswater);
            layerControl.removeLayer(mhswater);
        }
        

        const time = getCurrentTime();
        const hash = await getTestPackage(time);
        const url = `${protocol}://${host}:${port}/api/mhs_water_areas/?time=${time}&key=${hash}`;
        fetch(url)
            .then(response => response.json())
            .then(data => {
                mhswater = L.geoJSON(data, {
                    style: function (feature) {
                        return { color: "blue" };
                    }
                }).addTo(map);

                // Add the new layer to the layer control
                layerControl.addOverlay(mhswater, 'Water Area');
            });
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log('Fetch aborted');
        } else {
            console.error('Error fetching GeoJSON:', error);
        }
    }
}

export default {
    getVillageData,
    fetchInitialVillageData,
    getWaterAreas
}

