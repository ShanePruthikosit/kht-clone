import getData from './get_data.js';
import { map, layerControl} from './index.js';

// State variables for routing mode
let isRoutingMode = false;
let startVillage = null;
let endVillage = null;
let startLayer = null;
let endLayer = null;

// Function to toggle routing mode
export function toggleRoutingMode() {
    isRoutingMode = !isRoutingMode;
    resetRouting();
    return isRoutingMode;
}

// Function to check if we're in routing mode
export function isInRoutingMode() {
    return isRoutingMode;
}

// Function to handle village selection in routing mode
export function handleRoutingVillageClick(feature, layer) {
    if (!isRoutingMode) return false;
    
    const nodeId = feature.properties["nearby_node"];
    console.log("point clicked:", nodeId);
    
    if (nodeId == null) {
        layer.bindPopup(`Invalid geo data`).openPopup();
        console.log("node not found");
        return false;
    }

    // Set Start point
    if (startVillage == null) {
        startVillage = nodeId;
        startLayer = layer;
        try
        {
            layer.setStyle({ fillColor: 'yellow', color: 'black' });
            console.log("Start point set:", nodeId);
            layer.bindPopup(`Selected as starting point: ${feature.properties.village_name}`).openPopup();
        }
        catch (error) {
            // console.error("Error setting start point style:", error);
            // layer.bindPopup(`Error setting start point style`).openPopup();
        }
        return;
    } 
    // Set end point
    else if (endVillage == null && startVillage !== nodeId) {
        endVillage = nodeId;
        endLayer = layer;
        try
        {
        layer.setStyle({ fillColor: 'orange', color: 'black' });
        layer.bindPopup(`Selected as destination: ${feature.properties.village_name}`).openPopup();
        console.log("End point set:", startVillage);
        }
        catch (error) {
            // console.error("Error setting end point style:", error);
            // layer.bindPopup(`Error setting end point style`).openPopup();
        }
        // Call getRoute to display the route between the villages
        getData.getRoute(startVillage, endVillage);

        //Deactivates routing mode
        document.getElementById('routing-button').style.backgroundColor = 'white';
        isRoutingMode = false;
        return;
    }
    
    return false;
}

// Function to reset the routing state
export function resetRouting() {
    // Reset village styles if they exist
    try{
        if (startLayer) {
            startLayer.setStyle({ fillColor: 'blue', color: 'white' });
        }
        if (endLayer) {
            endLayer.setStyle({ fillColor: 'blue', color: 'white' });
        }
    }catch(error){}
    // Reset state variables
    startVillage = null;
    endVillage = null;
    startLayer = null;
    endLayer = null;
    
    // Fixed: Use window.Route instead of route
    if (window.Route && map.hasLayer(window.Route)) {
        map.removeLayer(window.Route);
        layerControl.removeLayer(window.Route);
    }
}
