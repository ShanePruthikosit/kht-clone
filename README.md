<p align="center">
  <img src="https://raw.githubusercontent.com/PKief/vscode-material-icon-theme/ec559a9f6bfd399b82bb44393651661b08aaf7ba/icons/folder-markdown-open.svg" width="100" alt="project-logo">
</p>
<p align="center">
    <h1 align="center">KHT_TEAM</h1>
</p>
<p align="center">
    <h2>Karen Hilltribes Trust: Interactive Map for Public Outreach and Donor Communication</h2>
</p>

<br><!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary><br>

- [Overview](#overview)
- [Methodology: Overview of Architecture Diagram](#methodology-overview-of-architecture-diagram)
- [Interactive Map and Features](#interactive-map-and-features)
- [Repository Structure](#repository-structure)
- [Village Article Post Form](#village-article-post-form)
- [Technologies](#technologies)
- [Modules](#modules)
- [Getting Started](#getting-started)
  - [To open Interactive Map](#to-open-interactive-map)
  - [To open Village Article Post Form](#to-open-village-article-post-form)
  - [Server Side (Backend)](#server-side-backend)
  - [PostgreSQL and PostGIS (Database)](#postgresql-and-postgis-database)
- [Project Roadmap (Extra Functionalities)](#project-roadmap-extra-functionalities)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
</details>
<hr>

## Overview

In Mae Hong Son province, around 40% of the Karen population lacks access to clean drinking water and adequate waste disposal. Karen Hilltribes Trust (KHT) is a charity organization in the United Kingdom that collects donations to support disadvantaged communities in Mae Hong Son, northern Thailand.<br>

KHT aims to broaden its outreach in the UK, raising awareness about its charity and inspiring donations. However, potential donors face challenges understanding KHT's work due to limited knowledge about Thailand, the Karen, and the geography of the mountainous north. To enhance efficiency and productivity, we propose creating an interactive web-based map. This map will offer a user-friendly interface, allowing users to pan, zoom, and explore village locations. Additionally, it will provide detailed information about each facility, facilitating a better understanding of KHT's impactful initiatives.

To create a functional interactive map, these are important components that need to be constructed:<br>
- **Data gathering**: The component is mainly responsible for the necessary information to either be displayed or implemented by other components.
- **The database after collecting all necessary data**: The database serves to collect and combine all data in a convenient, searchable form, to facilitate implementation by other components.
- **Configuring a database hosting system**: To allow our stakeholders to pull the data and display it on the map, configuring a database hosting system takes part in being responsible for this task.
- **The integration of the interactive map and the KHT pages**: This component is responsible for integration between the map and KHT page which involves the design and the deployment document.

---

##  Methodology: Overview of Architecture Diagram

![architecture](images/architecture.png)

We have an architecture diagram of our project, which consists of three main parts; the first is the Stakeholder’s Database, where KHT stores their village and project information. Then, there’s the backend where we use Linode as our database server.

The data manager will take the information from the Stakeholder’s (KHT) database, filter only the important info, and store it in the PostgreSQL database. We also use PostGIS, an extension of PostgreSQL, to store and query spatial data. Furthermore, we also have a bash and python program to do backups and update the database. Next is our API provider. It allows the interactive map (Front-end) to retrieve information from the database and display it on the map using HTTPS requests. Lastly, we have our Apache Server, enabling us to deploy our interactive map on the website at <https://kht-map.org/>, where we will later integrate it with the KHT’s website.

##  Interactive Map and Features

![interactive_map](images/interactive_map.png)

When entering our website at <https://kht-map.org>, users can find a sidebar on the left displaying map instructions. On the right, there is an interactive map marked with locations. Users have the ability to toggle layers via the layer control in the top right corner and can utilize the search function by clicking the search icon. Additionally, a legend is provided in the bottom right corner to help identify various elements on the map.

Users can select to show different types of layers such as OpenStreetMap, and  Dark background color map. For interaction on the map, the user can also turn and off markers such as terrain (elevation), districts, schools, hospitals, roads, water areas, water lines

Added a search button box for users to search and find each village by categories including year, start year - end year, project type, and minimum distance(Km) of villages and each facility. The user can select the button option that they want to search by that category and enter the input for that specific category to specify the type of villages that they want to search for. They can click the search button to search and click cancel button to cancel the operation and click clear to clear the search result and remove the current layer. 

Search Functionalities:
- **Search for village by project year**: When the user inputs a year of projects and this search will return all the villages that have a project in that specific year.
- **Search for village by project start and end year**: When the user inputs a start and end year of projects and this search will return all the villages that are in the range of the start and end year of the projects.
- **Search for village by project type**: Here, we have a drop down, showing all the project types that KHT has done. There are five project types in total which are WASH (Water, Sanitation and Hygiene), Further Education Scholarship, Irrigation, and Dormitory Meals. When the user selects one of them, the search will return all the villages that have that specific project type.
- **Search for village beyond a minimum distance from a facility**: In this search function, the user can find villages that are further away from a specific facility beyond a minimum distance. They can first turn on the hospitals and schools layer to help visualize the search better. Then they can input the minimum distance and select a facility type from the drop down. The user can only select one of the facility types which are school and hospital. Moreover, they can only select distances (in kilometers) between 0 and 41km. 

## Village Article Post Form  

![village_article_post_form](images/village_article_post_form.png)

This form <https://kht-map.org:8080/> is used as the KHT team will be able to enter a village name and a link to the article, which is required. In the village name box, there will be a collapsible box that sends a GET request and shows all the villages that match the user input. Moreover, the KHT people can also add the image link, article title, and posted date, which is optional. For security, we have the KHT staff input a password everytime they want to submit a form. Finally, this form will send the POST request and update our database in the URL table by adding a new row including the village name, article link, image link, article title, and posted date.

---

## Technologies 

Interactive Map (Frontend):
- HTML
- CSS
- Javascript
- Bootstrap

Server Side (Backend and Database)
- Linode (for our server)
- Python3 (FastAPI, Uvicorn)
- PgAdmin (management tool for PostgreSQL)
- PostgreSQL 
- PostGIS  
- pin-pont.co (website for geocoding hospital and school data)

Geospatial Computing Technologies
- Leaflet
- OpenSteetMap
- Shapefiles
- KML
- QGIS
- Map Shaper
- GeoJSON

---

##  Repository Structure

```sh
└── KHT_Team/
    ├── Project_Materials
    │   ├── All_Editable_Docs.txt
    │   ├── Final_Reports
    │   ├── Use_cases_diagram_V2.pdf
    │   ├── geo_json_files
    │   ├── shape_files
    │   └── zoho_data_analysis
    ├── README.md
    ├── Src
    │   ├── .gitignore
    │   ├── .vscode
    │   ├── Form
    │   ├── KHT_API_Test
    │   ├── KHT_Homepage
    │   ├── Map2
    │   ├── README.txt
    │   ├── Zoho_manager
    │   ├── api_provider2.py
    │   ├── backup_db.sh
    │   ├── cert.pem
    │   ├── database
    │   ├── download_kht_data.sh
    │   ├── get_recent_kht_data.sh
    │   ├── karenhilltribes.org.uk
    │   ├── key.pem
    │   ├── local_pid_file.txt
    │   ├── nohup.out
    │   ├── pid_file.txt
    │   ├── postgreSQL.py
    │   ├── postgreSQL.py.save
    │   ├── requirement.txt
    │   ├── rotate_backups.sh
    │   ├── rotate_logfiles.sh
    │   ├── run_kht_data_tasks.sh
    │   ├── sql_scripts
    │   ├── start_server.sh
    │   ├── testpackage.js
    │   ├── update_tables_db.sh
    │   ├── update_tables_db_log.txt
    │   └── village_url_model.py
    └── geo_data
        ├── mhs_districts.csv
        ├── mhs_roads.csv
        ├── mhs_roads.geojson
        ├── mhs_water_areas.csv
        └── mhs_water_lines.csv
```

---

##  Modules

</details>

<details closed><summary>Project_Materials</summary>

| File                                                                                                            | Summary                         |
| ---                                                                                                             | ---                             |
| [All_Editable_Docs.txt](https://github.com/Mhonns/KHT_Team/blob/master/Project_Materials/All_Editable_Docs.txt) | <code>► All documentation in links</code> |

</details>

<details closed><summary>Project_Materials.Final_Reports</summary>

| File                                                                                                    | Summary                         |
| ---                                                                                                     | ---                             |
| [KHT_Team_2nd_Semester_Undergraduate_Research_Project.pdf](https://github.com/Mhonns/KHT_Team/blob/master/Project_Materials/Final_Reports/KHT_Team_2nd_Semester_Undergraduate_Research_Project.pdf) | <code>► Final report pdf</code> |
| [KHT_Team_2nd_Semester_Undergraduate_Research_Project.pdf](https://github.com/Mhonns/KHT_Team/blob/master/Project_Materials/KHT_Databasetableschema.docx) | <code>► Database table schema docx</code> |
| [KHT_Team_2nd_Semester_Undergraduate_Research_Project.pdf](https://github.com/Mhonns/KHT_Team/blob/master/Project_Materials/KHT_FunctionalTestPlan.xlsx) | <code>► Functional Test Plan xlsx</code> |
| [KHT_Team_2nd_Semester_Undergraduate_Research_Project.pdf](https://github.com/Mhonns/KHT_Team/blob/master/Project_Materials/KHT_API_Table.docx) | <code>► KHT API Table docx</code> |

</details>

<details closed><summary>Src</summary>

| File                                                                                                    | Summary                         |
| ---                                                                                                     | ---                             |
| [postgreSQL.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/postgreSQL.py)                       | <code>► Using the psycopg2 library, this program interacts directly with the 'mhs_geographic' postgreSQL database, and run SQL queries.</code> |
| [api_provider2.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/api_provider2.py)                 | <code>► By using the FastAPI and Uvicorn library, this program provides the HTTPS request (GET and POST) and response handling</code> |
| [start_server.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/start_server.sh)                   | <code>► Script to restart the api_provider2.py</code> |
| [backup_db.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/backup_db.sh)                         | <code>► Backup postgreSQL database called 'mhs_geographic' on Linode Server</code> |
| [rotate_backups.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/rotate_backups.sh)               | <code>► From the backup_db.sh, this will rotate the backups so that there will always 3 backups </code> |
| [rotate_logfiles.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/rotate_logfiles.sh)             | <code>► Rotate log files from backup_dh.sh</code> |
| [download_kht_data.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/download_kht_data.sh)         | <code>► Download the most recent KHT data from google drive link using gdown</code> |
| [get_recent_kht_data.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/get_recent_kht_data.sh)     | <code>► Gets the most recent KHT data by date, moves it to KHT_Team/Src/database</code> |
| [run_kht_data_tasks.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/run_kht_data_tasks.sh)       | <code>► Script to run download_kht_data.sh and get_recent_kht_data.sh </code> |
| [update_tables_db.sh](https://github.com/Mhonns/KHT_Team/blob/master/Src/update_tables_db.sh)           | <code>► Update tables in the database for tables : village, project, projectVillage, donor, projectDonor, district </code> |
| [update_tables_db_log.txt](https://github.com/Mhonns/KHT_Team/blob/master/Src/update_tables_db_log.txt) | <code>► Log files from update_tables_db.sh</code> |
| [village_url_model.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/village_url_model.py)         | <code>► Village url model for Village Article Post Form</code> |

</details>

<details closed><summary>Src.database</summary>

| File                                                                                                                         | Summary                         |
| ---                                                                                                                          | ---                             |
| [create_school_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_school_table.py)                 | <code>► create school table</code> |
| [create_projectStatus_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_projectStatus_table.py)   | <code>► create projectStatus table</code> |
| [main.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/main.py)                                               | <code>► File to create and update tables </code> |
| [create_url_table2.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_url_table2.py)                     | <code>► create url2 table</code> |
| [create_donor_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_donor_table.py)                   | <code>► create donor table </code> |
| [create_project_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_project_table.py)               | <code>► create project table</code> |
| [config.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/config.py)                                           | <code>► Database configuration</code> |
| [create_projectDonor_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_projectDonor_table.py)     | <code>► create projectDonor table</code> |
| [create_district_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_district_table.py)             | <code>► create district table</code> |
| [create_projectVillage_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_projectVillage_table.py) | <code>► create projectVillage table</code> |
| [create_village_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_village_table.py)               | <code>► create village table</code> |
| [create_hospital_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_hospital_table.py)             | <code>► create hospital table</code> |
| [create_project_type_table.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/create_project_type_table.py)     | <code>► create projectType table</code> |
| [clean_csv.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/clean_csv.py)                                     | <code>► Clean the csv columns from KHT data</code> |

</details>

<details closed><summary>Src.database.geocode_data.getting_gov_data_from_data.go</summary>

| File                                                                                                                              | Summary                         |
| ---                                                                                                                               | ---                             |
| [hospital.py](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/geocode_data/getting_gov_data_from_data.go/hospital.py) | <code>► To get hospital data in csv from <data.go.th></code> |

</details>

<details closed><summary>Src.database.geocode_data.geocoding_school_and_hospital</summary>

| File                                                                                                                                         | Summary                         |
| ---                                                                                                                                          | ---                             |
| [server2.js](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/geocode_data/geocoding_school_and_hospital/school_data/server2.js)                                   | <code>► Using javascript to geocode school from <https://th.wikipedia.org/wiki/%E0%B8%A3%E0%B8%B2%E0%B8%A2%E0%B8%8A%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B9%82%E0%B8%A3%E0%B8%87%E0%B9%80%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B8%99%E0%B9%83%E0%B8%99%E0%B8%88%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%A7%E0%B8%B1%E0%B8%94%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AE%E0%B9%88%E0%B8%AD%E0%B8%87%E0%B8%AA%E0%B8%AD%E0%B8%99></code> |

</details>

<details closed><summary>Src.database.geocode_data.geocoding_school_and_hospital</summary>

| File                                                                                                                                                           | Summary                         |
| ---                                                                                                                                                            | ---                             |
| [server.js](https://github.com/Mhonns/KHT_Team/blob/master/Src/database/geocode_data/geocoding_school_and_hospital/hospital_data/server.js)                                         | <code>► Using javascript to geocode hospitals from  <https://data.go.th/dataset></code> |

</details>

<details closed><summary>Src.Form</summary>

| File                                                                                     | Summary                         |
| ---                                                                                      | ---                             |
| [script.js](https://github.com/Mhonns/KHT_Team/blob/master/Src/Form/script.js)           | <code>► script for Village Article Post Form  </code> |
| [stylesheet.css](https://github.com/Mhonns/KHT_Team/blob/master/Src/Form/stylesheet.css) | <code>► stylesheet for Village Article Post Form  </code> |
| [index.html](https://github.com/Mhonns/KHT_Team/blob/master/Src/Form/index.html)         | <code>► HTML for Village Article Post Form</code> |

</details>

<details closed><summary>Src.sql_scripts</summary>

| File                                                                                                                                                      | Summary                         |
| ---                                                                                                                                                       | ---                             |
| [tha_geographic_data.sql](https://github.com/Mhonns/KHT_Team/blob/master/Src/sql_scripts/)                                         | <code>► Manually Database backups</code> |

</details>

<details closed><summary>Src.KHT_Homepage</summary>

| File                                                                                                         | Summary                         |
| ---                                                                                                          | ---                             |
| [index.html](https://github.com/Mhonns/KHT_Team/blob/master/Src/KHT_Homepage/index.html)                     | <code>► This file contain the code for the side panel and include the map from map.html.</code> |
| [index.js](https://github.com/Mhonns/KHT_Team/blob/master/Src/KHT_Homepage/index.js)                         | <code>► This is the main file that contains the code for the KHT homepage. It imports the necessary libraries and components, and renders the main App component. It also contains the code for the map and the sidebar.</code> |
| [index_stylesheet.css](https://github.com/Mhonns/KHT_Team/blob/master/Src/KHT_Homepage/index_stylesheet.css) | <code>► stylesheet for index.html</code> |
| [map.html](https://github.com/Mhonns/KHT_Team/blob/master/Src/KHT_Homepage/map.html)                         | <code>► This the main file that contains the structure of the webpage. It includes the leaflet library and the main javascript file that will be used to create the map. The main javascript file will be used to create the map and add the layers to the map. The layers are stored in the data folder/ API and will be imported into the main javascript file. The main javascript file will also contain the logic to add the layers to the map and create the layer control. The layer control will allow the user to toggle the layers on and off.</code> |
| [stylesheet.css](https://github.com/Mhonns/KHT_Team/blob/master/Src/KHT_Homepage/stylesheet.css)             | <code>► stylesheet for map.html</code> |


</details>

---

##  Getting Started

**System Requirements (Front End):**

* **HTML**
* **CSS**
* **JAVASCRIPT**
* **BOOTSTRAP**

---

###  To open Interactive Map

<h4>From <code>source</code></h4>

> Open the index.html locally:
> 
> ```console
> $ git clone https://github.com/Mhonns/KHT_Team
> ```
>
> 1. Change to the KHT_Homepage directory:
> ```console
> $ cd KHT_Homepage
> ````
>
> 2. Open index.html:
> ```console
> $ index.html
> ```

---

###  To open Village Article Post Form  

<h4>From <code>source</code></h4>

> Open the index.html form locally. (Password: Please contact if you want to know the password)
>
> 1. Change to the project directory:
> ```console
> $ cd Form
> ```
>
> 3. Open index.html:
> ```console
> $ index.html
> ```

---

**System Requirements (Back End):**
- *Linode*:`Ubuntu 22.04.4 LTS`
- *PostgreSQL*: `13` 
- *PostGIS*: `3.4.2`

<details>
<summary>Pip Freeze Requirements.txt</summary>
  
- *annotated-types*: `0.6.0`
- *anyio*: `4.3.0`
- *attrs*: `21.2.0`
- *Automat*: `20.2.0`
- *Babel*: `2.8.0`
- *bcrypt*: `3.2.0`
- *beautifulsoup4*: `4.12.3`
- *blinker*: `1.4`
- *certifi*: `2.020.6.20`
- *chardet*: `4.0.0`
- *click*: `8.0.3`
- *cloud-init*: `23.1.2`
- *colorama*: `0.4.4`
- *command-not-found*: `0.3`
- *configobj*: `5.0.6`
- *constantly*: `15.1.0`
- *cryptography*: `3.4.8`
- *dbus-python*: `1.2.18`
- *distro*: `1.7.0`
- *distro-info*: `1.1+ubuntu0.2`
- *exceptiongroup*: `1.2.0`
- *fastapi*: `0.110.0`
- *filelock*: `3.14.0`
- *gdown*: `5.2.0`
- *geojson*: `3.1.0`
- *h11*: `0.14.0`
- *httplib2*: `0.20.2`
- *hyperlink*: `21.0.0`
- *idna*: `3.3`
- *importlib-metadata*: `4.6.4`
- *incremental*: `21.3.0`
- *iotop*: `0.6`
- *jeepney*: `0.7.1`
- *Jinja2*: `3.0.3`
- *Js2Py*: `0.74`
- *jsonpatch*: `1.32` 
- *jsonpointer*: `2.0`
- *jsonschema*: `3.2.0`
- *keyring*: `23.5.0`
- *launchpadlib*: `1.10.16`
- *lazr.restfulclient*: `0.14.4`
- *lazr.uri*: `1.0.6`
- *MarkupSafe*: `2.0.1`
- *more-itertools*: `8.10.0`
- *netifaces*: `0.11.0`
- *numpy*: `1.26.4`
- *oauthlib*: `3.2.0`
- *pandas*: `2.2.1`
- *pexpect*: `4.8.0`
- *postgres*: `4.0`
- *psycopg2*: `2.9.9`
- *psycopg2-binary*: `2.9.9`
- *psycopg2-pool*: `1.2`
- *ptyprocess*: `0.7.0`
- *pyasn1*: `0.4.8`
- *pyasn1-modules*: `0.2.1`
- *pydantic*: `2.6.3`
- *pydantic_core*: `2.16.3`
- *PyExecJS*: `1.5.1`
- *PyGObject*: `3.42.1`
- *PyHamcrest*: `2.0.2`
- *pyjsparser*: `2.7.1`
- *PyJWT*: `2.3.0`
- *pyOpenSSL*: `21.0.0`
- *pyparsing*: `2.4.7`
- *pyrsistent*: `0.18.1`
- *pyserial*: `3.5`
- *PySocks*: `1.7.1`
- *python-apt*: `2.4.0+ubuntu3`
- *python-dateutil*: `2.9.0.post0`
- *python-debian*: `0.1.43+ubuntu1.1`
- *python-magic*: `0.4.24`
- *pytz*: `2022.1`
- *PyYAML*: `5.4.1`
- *requests*: `2.25.1`
- *SecretStorage*: `3.3.1`
- *service-identity*: `18.1.0`
- *shapely*: `2.0.3`
- *six*: `1.16.0`
- *sniffio*: `1.3.1`
- *sos*: `4.5.6`
- *soupsieve*: `2.5`
- *ssh-import-id*: `5.11`
- *starlette*: `0.36.3`
- *systemd-python*: `234`
- *tqdm*: `4.66.4`
- *Twisted*: `22.1.0`
- *typing_extensions*: `4.10.0`
- *tzdata*: `2024.1`
- *tzlocal*: `5.2`
- *ubuntu-pro-client*: `8001`
- *ufw*: `0.36.1`
- *unattended-upgrades*: `0.1`
- *urllib3*: `1.26.5`
- *Uvicorn*: `0.27.1`
- *wadllib*: `1.3.6`
- *zipp*: `1.0.0`
- *zope.interface*: `5.4.0`
</details>

---
  
###  Server Side (Backend)

> SSH into into Linode Server
>
> 1. Configuring Linode
>
> At the beginning, We should install useful linux packages including git, certbot, apache server, and python libraries such as psycopg2, json, geojson, shapely, etc. We created a new user to limit the permissions.
> And our secure shell (ssh) public keys to the server so we can automatically shell to the server without typing the password. We configured the firewall to only allow usable interfaces such as secure shell on
> port 22, https request on port 80, postgreSQL on port 5432. We install postgreSQL tools on our server and open the remote connection to let our team access the database using PGAdmin.
>
> 2. Set up your private key on your laptop
> In this step, you have to generate your public key on your device, copy the key and configure it with Linode. (Please contact for more information on how to configure with Linode account)
>
>  Generate new ssh keys in Windows 10 / 11: <https://stackoverflow.com/questions/31813080/generate-new-ssh-keys-in-windows-10-11>
> Generating SSH keys on Linux and Mac: <https://www.ibm.com/docs/en/cognos-analytics/11.2.0?topic=content-generating-ssh-keys-linux-mac>
>
> 4. SSH into Linode by Command Line
> ```console
> $ ssh kht-team@172.105.120.121
> ```
>![ssh](images/ssh.png)
>
> #### KHT_Team/Src/postgreSQL.py
> This file contains all the SQL Queries.
>
> #### KHT_Team/Src/api_provider2.py
> This file contains all the API requests (GET & POST) .
> 
> 4.1) To test out the output of API calls: Check process ID first. You can do this by running this command or checking in KHT_Team/Src/pid_file.txt
> ```console
> $ ps aux | grep python
> ```
>![check_process](images/check_process.png)
> 
> 4.2) Kill the process
> ```console
> $ sudo kill -9 <process>
> ```
>
> 4.3) Running api_provider2.py manually and seeing API calls
> ```console
> $ sudo python3 api_provider2.py
> ```
>![check_process2](images/check_process2.png)
> 
> 4.4) **UPDATE**: Changed from using API process from nohup in KHT_Team/Src/start_server.sh to systemd. How to: <https://www.squash.io/executing-bash-script-at-startup-in-ubuntu-linux/>
> You can access and see this file by doing. Here, the systemd is running python3 api_provider2.py directly.
> ```console
> $ sudo nano /etc/systemd/system/start_server.service
> ```
> ![start_server.service](images/start_server.service.png)
>
> You can also check the status of the server by doing:
> ```console
> $ sudo systemctl status start_server.service
> ```
> ![start_server.service_status](images/start_server.service_status.png)
> 
> 4. Configuring Apache Serve
>
> For hosting our web server we chose Apache server which allows our team to serve multiple hosts hence our team can deploy two websites at the same time. For the current project. Our team configures two websites
> including an interactive map website on port 80, 443 and the village article form on port 8080.
>
> How to restart apache server (if you made changes to KHT_Homepage or Form:
> ```console
> $ sudo su
> ```
> For Homepage:
> ```console
> $ cp -r /home/kht-team/KHT_Team/Src/KHT_Homepage /var/www/
> ```
> For Form:
> ```console
> $ cp -r /home/kht-team/KHT_Team/Src/Form /var/www/
> ```
> After running either of these commands, do:
> ```console
> $ systemctl restart apache2.service
> ```
>
> 5. Cronjob (Cronjob is for schluding tasks)
>
> To access cronjob:
> ```console
> $ sudo crontab -e
> ```
---

###  PostgreSQL and PostGIS (Database)

> PgAdmin 4v7++ >
>
> 1. Creating Server
>
> Once opened PgAdmin, Click on 'Servers', 'Create', and 'Server Group'. This page will pop up. Fill in the details as follow
>
> ![create_server1](images/create_server1.png)
> ![create_server2](images/create_server2.png)
> ![create_server3](images/create_server3.png)
>
> 2. Connecting to the Server
>
> To access the database, double click on your server name and input the password. (Password: Please contact if you want to know the password)
> 
> ![connect_to_server](images/connect_to_server.png) 
---

##  Project Roadmap (Extra Functionalities)

- [ ] `► Create a toplogical data for roads`
- [ ] `► Use pgrouting or write your own code to find villages nearest to a facility by road`

---

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Report Issues](https://github.com/Mhonns/KHT_Team/issues)**: Submit bugs found or log feature requests for the `KHT_Team` project.
- **[Submit Pull Requests](https://github.com/Mhonns/KHT_Team/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/Mhonns/KHT_Team/discussions)**: Share your insights, provide feedback, or ask questions.

<details closed>
<summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your github account.
2. **Clone Locally**: Clone the forked repository to your local machine using a git client.
   ```sh
   git clone https://github.com/Mhonns/KHT_Team
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to github**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.
8. **Review**: Once your PR is reviewed and approved, it will be merged into the main branch. Congratulations on your contribution!
</details>

<details closed>
<summary>Contributor Graph</summary>
<br>
<p align="center">
   <a href="https://github.com{/Mhonns/KHT_Team/}graphs/contributors">
      <img src="https://contrib.rocks/image?repo=Mhonns/KHT_Team">
   </a>
</p>
</details>

---

##  Acknowledgments

### Team Members

#### Frontend
- Tatchphol Charoensupthaworn (Toiek) <tcharoen@cmkl.ac.th>
- Krittin Kamolpornwijit (Roong) <kkamolpo@cmkl.ac.th>
- Ittiphat Kijpaisansak (Ohm)  <ikijpais@cmkl.ac.th>

#### Backend
- Panupong Dangkajitpetch (King)  <pdangkaj@cmkl.ac.th>
- Nathadon Samairat (Mhon) <nsamaira@cmkl.ac.th>

### Advisor
- Dr. Sally Goldin <sally@cmkl.ac.th>


[**Return**](#overview)

---
