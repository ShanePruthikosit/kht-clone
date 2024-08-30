const Http = new XMLHttpRequest();


const urls = [
    // Village endpoints
    "kht-data.uk.to/api/village", 
    "kht-data.uk.to/api/village/?village_id=ea2be552-9769-4b3e-b0c6-53a9bc918bb5", 
    "kht-data.uk.to/api/get_village_project_by_year/?year=2002", 
    "kht-data.uk.to/api/get_village_project_by_year/?start_year=2021&end_year=2027",
    "kht-data.uk.to/api/village?village_id=ea2be552-9769-4b3e-b0c6-53a9bc918bb5&start_year=2000&end_year=2030", 
    "kht-data.uk.to/api/village?distance=5&facility_type=shcool&facility_name=โรงเรียนอนุบาลขุนยวม", 
    "kht-data.uk.to/api/village?road_distance=10&facility_type=hospital&facility_name=โรงพยาบาลส่งเสริมสุขภาพตำบลแม่สุริน",

    // Project Endpoints
    "kht-data.uk.to/api/project",
    "kht-data.uk.to/api/project_donor/?project_id=706d428b-4aac-4289-bed2-d083489fc0f5",
    "kht-data.uk.to/api/project_type/?project_type=WASH",
    "kht-data.uk.to/api/project_type/?project_type=Irrigation",
    "kht-data.uk.to/api/project_type/?project_type=Further%20Education%20Scholarships",
    "kht-data.uk.to/api/project_type/?project_type=Dormitory%20 Meals",
    "kht-data.uk.to/api/project_type/?project_type=School%20Buses",

    // Schools and hospitals
    "kht-data.uk.to/api/hospital",
    "kht-data.uk.to/api/school",

    // Geographic endpoints
    "kht-data.uk.to/api/mhs_districts",
    "kht-data.uk.to/api/mhs_roads",
    "kht-data.uk.to/api/mhs_water_areas",
    "kht-data.uk.to/api/mhs_water_lines"
];

const url=urls[0];
Http.open("GET", url);
Http.send();
Http.onreadystatechange = (e) => {
  console.log(Http.responseText)
}