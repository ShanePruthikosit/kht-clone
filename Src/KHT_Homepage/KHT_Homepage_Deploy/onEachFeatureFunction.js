import { resetClickedLayer, clickedLayer, getCurrentTime, protocol, host, port } from './index.js';


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

export{onEachFeatureFunction};