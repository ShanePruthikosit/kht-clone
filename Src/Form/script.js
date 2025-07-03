/* ==========================================
            Generate time stamp
=============================================*/
function getCurrentTime() {
  const now = new Date();
  const hours = now.getHours().toString().padStart(2, "0");
  const minutes = now.getMinutes().toString().padStart(2, "0");
  const seconds = now.getSeconds().toString().padStart(2, "0");
  return `${hours}-${minutes}-${seconds}`;
}

/* ==========================================
          Endpoint url configuration
=============================================*/
const host = "ailurophile.xyz";
const port = "2546";
const protocol = "https";

const form = document.getElementById("village-url-form");
const searchInput = document.getElementById("village_name");
const resultContainer = document.getElementById("result-container");
const messageElement = document.getElementById("message");

searchInput.addEventListener("input", function () {
  if (this.value.length > 0) {
    resultContainer.style.display = "block";
  } else {
    resultContainer.style.display = "none";
  }
});

document.addEventListener("click", function (e) {
  if (!searchInput.contains(e.target)) {
    resultContainer.style.display = "none";
  }
});

document
  .getElementById("village_name")
  .addEventListener("input", async function (e) {
    const searchQuery = e.target.value.toLowerCase();
    if (!searchQuery) {
      document.getElementById("result-container").innerHTML = "";
      return;
    }

    const time = getCurrentTime();
    const hash = await getTestPackage(time);
    const url = `${protocol}://${host}:${port}/api/village_names/?time=${time}&key=${hash}`;

    // fetch('https://kht-map.org:2546/api/village/', {
    fetch(url, {
      method: "GET",
      mode: "cors",
    })
      .then((response) => response.json())
      .then((data) => {
        const filteredVillages = data.filter((village) =>
          village.toLowerCase().includes(searchQuery)
        );
        const resultContainer = document.getElementById("result-container");
        resultContainer.innerHTML = "";
        filteredVillages.forEach((village) => {
          const div = document.createElement("div");
          div.textContent = village;
          div.classList.add("village-name");
          div.addEventListener("click", function () {
            searchInput.value = this.textContent;
            resultContainer.style.display = "none";
          });
          resultContainer.appendChild(div);
        });
      })
      .catch((error) => console.error("Error fetching village names:", error));
  });

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // Prevent default form submission
  console.log("Form submitted!");

  const villageName = document.getElementById("village_name").value;
  const url = document.getElementById("url").value;
  const imageUrl = document.getElementById("image_url").value || ""; // Set to empty string if null
  const password = document.getElementById("password").value;

  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    messageElement.innerHTML =
      '<span style="color: #cc0000;">A link must start with http:// or https://</span>';
    return;
  }
  if (
    imageUrl &&
    !imageUrl.startsWith("http://") &&
    !imageUrl.startsWith("https://")
  ) {
    messageElement.innerHTML =
      '<span style="color: #cc0000;">A link must start with http:// or https://</span>';
    return;
  }
  const articleTitle = document.getElementById("article_title").value || ""; // Set to empty string if null
  const postedDate = document.getElementById("posted_date").value || ""; // Set to empty string if null

  // Validate the form data
  const data = {
    village_name: villageName,
    url: url,
    image_url: imageUrl,
    article_title: articleTitle,
    posted_date: postedDate,
    password: password,
  };

  const time = getCurrentTime();
  const hash = await getTestPackage(time);
  const postUrl = `${protocol}://${host}:${port}/api/post/village_url/?time=${time}&key=${hash}`;

  try {
    // const response = await fetch('https://kht-map.org:2546/api/post/village_url', {
    const response = await fetch(postUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    const jsonResponse = await response.json();
    console.log("Response:", jsonResponse);

    if (jsonResponse.message.password_message) {
      document.getElementById("message").innerHTML =
        jsonResponse.message.password_message;
    } else {
      if (jsonResponse.message.status === "Failed") {
        //print the password_message from the response first

        //reponse both the message and password_message but it goes to next line
        document.getElementById("message").innerHTML =
          jsonResponse.message.message;

        // document.getElementById('message').innerHTML = jsonResponse.message.password_message + '\n' + jsonResponse.message.message;
      } else {
        document.getElementById("message").innerHTML =
          jsonResponse.message.message;
      }
    }
  } catch (error) {
    console.error("Error:", error);
    document.getElementById("message").innerHTML = error.message;
  }
});

document.getElementById("clear-button").addEventListener("click", function () {
  document.getElementById("village-url-form").reset();
  document.getElementById("message").innerHTML="";
});
