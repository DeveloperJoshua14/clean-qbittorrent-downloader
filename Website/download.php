<?php
// File path to the JSON file
$filePath = 'ToDownload.json';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Validate input
    $input = json_decode(file_get_contents('php://input'), true);
    $movie = $input['movie'];

    $title = $movie['Title'];
    $year = $movie['Year'];
    $imdbID = $movie['imdbID'];
    $type = $movie['Type'];
    
    // Define the start date in Unix time
    $startDate = '1970-01-01 00:00:00';
    $startTimestamp = strtotime($startDate);
    $currentTimestamp = time();
    $secondsSince = $currentTimestamp - $startTimestamp;

    // Check if the JSON file exists
    if (file_exists($filePath)) {
        // Read the existing content of the JSON file
        $jsonData = file_get_contents($filePath);

        // Decode JSON into a PHP array
        $dataArray = json_decode($jsonData, true);

        // Ensure the file content is an array
        if (!is_array($dataArray)) {
            $dataArray = [];
        }
    } else {
        // If the file doesn't exist, start with an empty array
        $dataArray = [];
    }

    // Check if it is a movie/show
    if ($type == "movie") {
        http_response_code(300);
    } else if ($type == "series"){
        http_response_code(301);
    } else {
        http_response_code(302);
        exit;
    }


    // Check if an entry with the same imdbID already exists
    $isDuplicate = false;
    foreach ($dataArray as $entry) {
        if ($entry['imdbID'] === $imdbID) {
            $isDuplicate = true;
            break;
        }
    }

    if ($isDuplicate) {
        echo "Movie with imdbID '$imdbID' already exists.";
    } else {
        // Add new data to the array
        $dataArray[] = [
            'title' => $title,
            'year' => $year,
            'imdbID' => $imdbID,
            'type' => $type,
            'dateAdded' => $secondsSince
        ];

        // Encode the updated array back to JSON
        $newJsonData = json_encode($dataArray, JSON_PRETTY_PRINT);

        // Write the updated JSON back to the file
        if (file_put_contents($filePath, $newJsonData)) {
            echo "Movie added successfully!";
        } else {
            echo "Failed to write to the JSON file.";
        }
    }
}
?>
