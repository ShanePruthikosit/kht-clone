const fetch = require('node-fetch');
const fs = require('fs');
const csv = require('csv-parser');

// Function to read CSV file and geocode addresses
async function geocodeAddresses(csvFilePath, accessToken) {
    const results = [];

    // Read CSV file
    fs.createReadStream(csvFilePath)
        .pipe(csv())
        .on('data', async (row) => {
            // Construct address string
            const address = `${row['ชื่อหน่วยงาน']} ${row['จังหวัด']} ${row['อำเภอ']} ${row['ตำบล']}`;

            // Send POST request to geocode the address
            try {
                const response = await fetch('https://pin-point.co/g/search/batch', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        data: [{
                            input: address
                        }],
                        key: accessToken
                    })
                });

                if (!response.ok) {
                    console.error(`Failed to geocode address: ${address}`);
                    return;
                }

                const data = await response.json();
                results.push(data);
            } catch (error) {
                console.error(`Error geocoding address: ${address}`, error);
            }
        })
        .on('end', () => {
            console.log('Geocoding completed.');
            console.log(results);
            // Length of results
            console.log(results.length);
            // Print URL request if needed
        });
}


// geocodeAddresses('data.csv', '6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935');



// const fetch = require('node-fetch'); // Import node-fetch for making HTTP requests
// const fs = require('fs'); // Import fs module to work with file system

const fetchData = async () => {
    const url = "https://pin-point.co/g/search/autocomplete";
    const data = {
        keyword: "โรงพยาบาลขุนยวม,ตำบลขุนยวม, อำเภอขุนยวม, จังหวัดแม่ฮ่องสอน, 58140",
        key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935",
        maxResult: 5
    };
    const headers = {
        "Content-Type": "application/json",
        "Referer": "panuo"
    };

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonResponse = await response.json();
        // Do something with the jsonResponse
        console.log(jsonResponse);
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Call the fetchData function
// fetchData();

const keyword = "โรงพยาบาลปางมะผ้า ทางหลวงแผ่นดินหมายเลข1095 ตำบลสบป่อง อำเภอปางมะผ้า จังหวัดแม่ฮ่องสอน 58150"
const keyword2 = "โรงพยาบาลส่งเสริมสุขภาพตำบลห้วยปูลิง ตำบลห้วยปูลิง อำเภอเมืองแม่ฮ่องสอน จังหวัดแม่ฮ่องสอน 58000"
const test= "โรงพยาบาลส่งเสริมสุขภาพตำบลห้วยปูลิง,จ.แม่ฮ่องสอน,อ.เมืองแม่ฮ่องสอน, ต.ห้วยปูลิง,5800"

const fetchLocationDetails = async () => {
    const autocompleteUrl = "https://pin-point.co/g/search/autocomplete";
    const detailsUrl = "https://pin-point.co/g/search/details";
    const autocompleteData = {
        keyword: test,
        key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935",
        maxResult: 5
    };
    const headers = {
        "Content-Type": "application/json",
        "Referer": "panuo"
    };

    try {
        // Fetch autocomplete data
        const autocompleteResponse = await fetch(autocompleteUrl, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(autocompleteData)
        });

        if (!autocompleteResponse.ok) {
            throw new Error(`HTTP error! status: ${autocompleteResponse.status}`);
        }

        const autocompleteJsonResponse = await autocompleteResponse.json();

        // Extract the first location ID from the autocomplete response
        const firstLocationId = autocompleteJsonResponse.data[0].LocationID;

        // Use the first location ID in the details request
        const detailsData = {
            locationid: firstLocationId,
            key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935" // Replace with your actual access token
        };

        // Fetch details using the first location ID
        const detailsResponse = await fetch(detailsUrl, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(detailsData)
        });

        if (!detailsResponse.ok) {
            throw new Error(`HTTP error! status: ${detailsResponse.status}`);
        }

        const detailsJsonResponse = await detailsResponse.json();
        // Do something with the detailsJsonResponse
        console.log(detailsJsonResponse);
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Call the function to initiate fetching location details
// fetchLocationDetails();

const fetchLocationDetails2 = async (csvFilePath) => {
    try {
        const csvData = fs.readFileSync(csvFilePath, 'utf-8'); // Read CSV file
        const locations = csvData.split('\n').map(row => {
            const [ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์] = row.split(','); // Split each row into columns
            return { ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์ };
        });

        const autocompleteUrl = "https://pin-point.co/g/search/autocomplete";
        const detailsUrl = "https://pin-point.co/g/search/details";
        const headers = {
            "Content-Type": "application/json",
            "Referer": "panuo"
        };

        for (const location of locations) {
            const autocompleteData = {
                keyword: `${location['ชื่อหน่วยงาน']},${location['ตำบล']},${location['อำเภอ']},${location['จังหวัด']},${location['รหัสไปรษณีย์']}`,
                key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935",
                maxResult: 1
            };

            // Fetch autocomplete data
            const autocompleteResponse = await fetch(autocompleteUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(autocompleteData)
            });

            if (!autocompleteResponse.ok) {
                throw new Error(`HTTP error! status: ${autocompleteResponse.status}`);
            }

            const autocompleteJsonResponse = await autocompleteResponse.json();

            // Extract the first location ID from the autocomplete response
            const firstLocationId = autocompleteJsonResponse.data[0].LocationID;

            // Use the first location ID in the details request
            const detailsData = {
                locationid: firstLocationId,
                key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935" // Replace with your actual access token
            };

            // Fetch details using the first location ID
            const detailsResponse = await fetch(detailsUrl, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(detailsData)
            });

            if (!detailsResponse.ok) {
                throw new Error(`HTTP error! status: ${detailsResponse.status}`);
            }

            const detailsJsonResponse = await detailsResponse.json();
            // Extract PremiseName, LAT_LON, and FormattedAddress from the detailsJsonResponse
            const { LAT_LON, FormattedAddress } = detailsJsonResponse.data;

            console.log(locations.indexOf(location) + 1, LAT_LON, FormattedAddress);

            // Delay for 1 second before the next iteration
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Example usage:
// fetchLocationDetails2('data.csv'); // Pass the path to your CSV file

//chat version
const fetchLocationDetails3 = async (csvFilePath, outputFilePath) => {
    try {
        const csvData = fs.readFileSync(csvFilePath, 'utf-8'); // Read CSV file
        const locations = csvData.split('\n').map(row => {
            const [ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์] = row.split(','); // Split each row into columns
            return { ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์ };
        });

        const autocompleteUrl = "https://pin-point.co/g/search/autocomplete";
        const detailsUrl = "https://pin-point.co/g/search/details";
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
                    const autocompleteData = {
                        keyword: `${loc['ชื่อหน่วยงาน']},${loc['ตำบล']},${loc['อำเภอ']},${loc['จังหวัด']},${loc['รหัสไปรษณีย์']}`,
                        key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935",
                        maxResult: 5
                    };
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
                        const firstLocationId = autocompleteJsonResponse.data[0].LocationID;
                        const detailsData = {
                            locationid: firstLocationId,
                            key: "6b56bcf7c907653c3d50b1a5094379aea39090020111b49dc52ce35df6db5c2d64556ded7510e935"
                        };
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
// fetchLocationDetails3('hospital_data.csv', 'hospital_data.json');

const fetchLocationDetailsID = async (csvFilePath, outputFilePath) => {
    try {
        const csvData = fs.readFileSync(csvFilePath, 'utf-8'); // Read CSV file
        const locations = csvData.split('\n').map(row => {
            const [ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์] = row.split(','); // Split each row into columns
            return { ชื่อหน่วยงาน, ตำบล, อำเภอ, จังหวัด, รหัสไปรษณีย์ };
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
                    const autocompleteData = {
                        keyword: `${loc['ชื่อหน่วยงาน']},${loc['ตำบล']},${loc['อำเภอ']},${loc['จังหวัด']},${loc['รหัสไปรษณีย์']}`,
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
// fetchLocationDetailsID('hospital_data_p3.csv', 'hospital_data_p3.json');


const fetchHospitalDetails = async (jsonFilePath, outputFilePath) => {
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
            const detailsData = {
                locationid: location.response.data[0].LocationID,
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

        // Write results to JSON file
        fs.writeFileSync(outputFilePath, JSON.stringify(results, null, 2));
        console.log("Results saved to", outputFilePath);
    } catch (error) {
        console.error("Fetch error:", error);
    }
};

// Usage
fetchHospitalDetails('hospital_data_p3_chose.json', 'hospital_data_p3_details.json');


