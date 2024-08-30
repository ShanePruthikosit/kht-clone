const fetch = require('node-fetch');
const fs = require('fs');
const csv = require('csv-parser');

// do this for school csv fileURLToPath
// โรงเรียน,ตำบล,อำเภอ,ระดับชั้น
// โรงเรียนขุนยวม,ขุนยวม,ขุนยวม,อนุบาล–ประถมศึกษา
// โรงเรียนเขตพื้นที่การศึกษาอำเภอขุนยวม[#1],ขุนยวม,ขุนยวม,อนุบาล–ประถมศึกษา
const fetchLocationDetailsID = async (csvFilePath, outputFilePath) => {
    try {
        const csvData = fs.readFileSync(csvFilePath, 'utf-8'); // Read CSV file
        const locations = csvData.split('\n').map(row => {
            const [โรงเรียน, ตำบล, อำเภอ, ระดับชั้น] = row.split(','); // Split each row into columns
            return { โรงเรียน, ตำบล, อำเภอ, ระดับชั้น };
        });

        const autocompleteUrl = "https://pin-point.co/g/search/autocomplete";
        const headers = {
            "Content-Type": "application/json",
            "Referer": "panuo"
        };

        const batchSize = 5; // Number of locations to process in each batch
        let batch = [];
        let results = []; // Array to store the results
        for (const location of locations) {
            batch.push(location);
            if (batch.length === batchSize || location === locations[locations.length - 1]) {
                const promises = batch.map(async (loc) => {
                    const autocompleteData = {//โรงเรียน,ตำบล,อำเภอ,ระดับชั้น
                        keyword: `${loc['โรงเรียน']},${loc['ตำบล']},${loc['อำเภอ']},${loc['ระดับชั้น']} `,
                        key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935",
                        maxResult: 5
                    };
                    console.log("Sending request for:", autocompleteData.keyword); // Log the request
                    try {
                        const autocompleteResponse = await fetch(autocompleteUrl, {
                            method: "POST",
                            headers: headers,
                            body: JSON.stringify(autocompleteData)
                        });
                        if (!autocompleteResponse.ok) {
                            throw new Error(`HTTP error! status: ${autocompleteResponse.status}`);
                        }
                        const autocompleteJsonResponse = await autocompleteResponse.json();
                        // Store the result along with the query string
                        results.push({ query: autocompleteData.keyword, response: autocompleteJsonResponse });
                    } catch (error) {
                        console.error("Error processing location:", error);
                    }
                });
                await Promise.all(promises);
                batch = []; // Reset batch
            }
        }

        // Write results to JSON file
        fs.writeFileSync(outputFilePath, JSON.stringify(results, null, 2));
        console.log("Results saved to", outputFilePath);
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Usage
// fetchLocationDetailsID('school_data_p7.csv', 'school_data_p7.json');

const fetchSchoolDetails = async (jsonFilePath, outputFilePath) => {
    try {
        const jsonData = fs.readFileSync(jsonFilePath, 'utf-8'); // Read JSON file
        const locations = JSON.parse(jsonData); // Parse JSON data

        const detailsUrl = "https://pin-point.co/g/search/details";
        const headers = {
            "Content-Type": "application/json",
            "Referer": "panuo"
        };

        let results = []; // Array to store the results
        for (const location of locations) {
            // Assuming location.response.data is an array of objects with LocationID
            for (const data of location.response.data) {
                const detailsData = {
                    locationid: data.LocationID,
                    key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935"
                };
                try {
                    const detailsResponse = await fetch(detailsUrl, {
                        method: "POST",
                        headers: headers,
                        body: JSON.stringify(detailsData)
                    });
                    if (!detailsResponse.ok) {
                        throw new Error(`HTTP error! status: ${detailsResponse.status}`);
                    }
                    const detailsJsonResponse = await detailsResponse.json();
                    const { LAT_LON, FormattedAddress } = detailsJsonResponse.data;
                    results.push({ location, LAT_LON, FormattedAddress }); // Store the result
                } catch (error) {
                    console.error("Error processing location:", error);
                }
            }
        }

        // Write results to JSON file
        fs.writeFileSync(outputFilePath, JSON.stringify(results, null, 2));
        console.log("Results saved to", outputFilePath);
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Usage
fetchSchoolDetails('school_data_p7_chose.json', 'school_data_p7_details.json');