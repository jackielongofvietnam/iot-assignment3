-- Soil Moisture Table (value in %)
CREATE TABLE soil_moisture (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value INT,  -- percentage
    timestamp DATETIME
);

-- Temperature Table (value in Celsius)
CREATE TABLE temperature (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value FLOAT,  -- e.g. 25.3°C
    timestamp DATETIME
);

-- Sunlight Table (categorized as 'Sunny' or 'Cloudy')
CREATE TABLE sunlight (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value VARCHAR(20),  -- 'Sunny' or 'Cloudy'
    timestamp DATETIME
);

-- Rain Table (e.g., 'No rain', 'Slight rain', 'Heavy rain')
CREATE TABLE rain (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value VARCHAR(20),
    timestamp DATETIME
);

-- Water Level Table (e.g., 'OK', 'High', 'Flooded')
CREATE TABLE water_level (
    id INT AUTO_INCREMENT PRIMARY KEY,
    value VARCHAR(20),
    timestamp DATETIME
);