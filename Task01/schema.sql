PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stations (
    station_id INTEGER PRIMARY KEY,
    station_name TEXT NOT NULL UNIQUE,
    temperature_unit TEXT NOT NULL CHECK (temperature_unit IN ('C', 'F'))
);

CREATE TABLE IF NOT EXISTS readings (
    station_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    hour INTEGER NOT NULL,
    pm25 REAL,
    pm10 REAL,
    no2 REAL,
    temperature_c REAL,
    PRIMARY KEY (station_id, day, hour),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

CREATE INDEX IF NOT EXISTS idx_readings_station_day
ON readings(station_id, day);
