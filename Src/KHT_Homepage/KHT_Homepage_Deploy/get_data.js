/* ==========================================
            Get Village data from api
=============================================*/

var firstLoad = true;
var VillageData;
var done = true; 
var last = [' ', ' '];

async function getVillageData(url, villagePointColor) {
    if (done == true) { 
        done = false;
        // close old village points
        if (VillageData) {
            map.removeLayer(VillageData);
        } 
        const response = await fetch(url);
        const data = await response.json();
        data_length = data.features.length;
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

export default {
    getVillageData
}

