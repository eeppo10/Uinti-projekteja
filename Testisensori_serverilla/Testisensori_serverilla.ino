"""
Author: Eerikki Laitala

This program is written for the M5stickCplus2 
It records IMU data at the frequency of 100Hz
Data is downloadable from a web interface after it has been recorded 
"""

#include <M5StickCPlus2.h>
#include <Wire.h>
#include <WiFi.h>
#include <SPIFFS.h>
#include <WebServer.h>
#include <driver/rtc_io.h>
#include <esp_sleep.h>

File dataFile;

// WiFi credentials
const char* ssid = "ID";
const char* password = "PASSWORD";
unsigned long previousMillis = 0;¨

// Sampling frequency of 100Hz = 10ms intervals
const unsigned long interval = 10;  // 10ms looptime 10ms=100Hz

// Initial states
WebServer server(80);
bool isRecording = false; // Flag to track recording state

// Buffer
const int BUFFER_SIZE = 7000;  // Buffer for 100 samples
int16_t buffer[BUFFER_SIZE][7];  // 3 for X, Y, Z axes (int16_t = 2 bytes each)
int bufferIndex = 0;
int16_t delta = 0;


void setup() {
  auto cfg = M5.config();
  StickCP2.begin(cfg);
  Wire.begin();

  // Initialize SPIFFS
 if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return;
  }
  // Open or create the file in write mode
  dataFile = SPIFFS.open("/data.bin", FILE_WRITE);
  if (!dataFile) {
    Serial.println("Failed to open file for writing");
  }
  dataFile.close();

  // Initialize WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    M5.Lcd.print(".");
  }

  // Promtp when connected
  M5.Lcd.println("Connected to WiFi");
  M5.Imu.init();


  // Display the IP address on the screen
  M5.Lcd.setCursor(0, 20);
  M5.Lcd.printf("IP Address: %s\n", WiFi.localIP().toString().c_str());

  // Setup server
  server.on("/", HTTP_GET, handleRoot);      // Root path: list files
  server.on("/download", HTTP_GET, handleDownload);  // Download file
  server.on("/toggleRecording", HTTP_GET, handleToggleRecording);


}

void loop() {
  M5.update();

  // Check if button A is pressed
  if (M5.BtnA.wasPressed()) {
    isRecording = !isRecording; // Toggle recording state
    if (isRecording) {
      M5.Lcd.println("Recording started");
      stopServer();    // Stop the server when recording starts
    } else {
      writeBufferToSPIFFS();
      bufferIndex = 0;  // Reset buffer index after writing
      M5.Lcd.println("Recording stopped");
      startServer();      // Start the server when recording stops
    }
  }

  if (isRecording) {

    // Record time between measurements
    unsigned long currentMillis = millis();

    if (currentMillis - previousMillis >= interval) {
    delta = currentMillis - previousMillis;
    previousMillis = currentMillis;

    // Get data
    float accX, accY, accZ;
    float gyroX, gyroY, gyroZ;

    M5.Imu.getAccelData(&accX, &accY, &accZ);
    M5.Imu.getGyroData(&gyroX, &gyroY, &gyroZ);

    // Store scaled integers
    int16_t ax_int = (int16_t)(accX * 1000);  // Scale to millig-forces
    int16_t ay_int = (int16_t)(accY * 1000);
    int16_t az_int = (int16_t)(accZ * 1000);
    // Store scaled integers
    int16_t gx_int = (int16_t)(gyroX);
    int16_t gy_int = (int16_t)(gyroY);
    int16_t gz_int = (int16_t)(gyroZ);

    // data point number since start
    Serial.println(previousMillis);

  // buffer
  buffer[bufferIndex][0] = ax_int;
  buffer[bufferIndex][1] = ay_int;
  buffer[bufferIndex][2] = az_int;
  buffer[bufferIndex][3] = gx_int;
  buffer[bufferIndex][4] = gy_int;
  buffer[bufferIndex][5] = gz_int;
  buffer[bufferIndex][6] = delta;
  bufferIndex++;

  // Empty buffer when full
  if (bufferIndex >= BUFFER_SIZE) {
    writeBufferToSPIFFS();
    bufferIndex = 0;  // Reset buffer index after writing
  }

  }
  }

  // Handle server client requests only if not recording
  if (!isRecording) {
    server.handleClient();
  }
}

// Toggling server on
void startServer() {
  server.begin();
  M5.Lcd.println("Server started");
}

// Toggling server off
void stopServer() {
  server.close();
  M5.Lcd.println("Server stopped");
}


// Write to buffer 
void writeBufferToSPIFFS() {
  File dataFile = SPIFFS.open("/data.bin", FILE_APPEND);

  if (!dataFile) {
    Serial.println("File not open for writing");
    return;
  }

  // Write buffer data to the file as binary
  size_t writtenBytes = dataFile.write((uint8_t*)buffer, sizeof(buffer));

  // Check if data was written successfully
  if (writtenBytes == sizeof(buffer)) {
    Serial.println("Buffer written to SPIFFS successfully");
  } else {
    Serial.println("Error writing buffer to SPIFFS");
  }

    dataFile.close();
    Serial.println("File closed");
}

// Handle root path and list files
void handleRoot() {
  String html = "<html><body><h1>Control Panel</h1>";

  // Add a toggle recording button to web interface
  html += "<button onclick=\"toggleRecording()\">Toggle Recording</button>";
  
  html += "<script>";
  html += "function toggleRecording() {";
  html += "  fetch('/toggleRecording')"; // Send request to toggle recording
  html += "    .then(response => response.text())";
  html += "    .then(data => alert(data))";
  html += "    .catch(err => console.error('Error:', err));";
  html += "}";
  html += "</script>";

  html += "<h1>File List</h1><ul>";

  File root = SPIFFS.open("/");
  File file = root.openNextFile();
  while (file) {
    String fileName = file.name();
    html += "<li><a href='/download?file=" + fileName + "'>" + fileName + "</a></li>";
    file = root.openNextFile();
  }

  html += "</ul></body></html>";
  server.send(200, "text/html", html); // Send the updated HTML
}


// Handle download request
void handleDownload() {
String fileName = server.arg("file");
  
  // Ensure the fileName starts with a '/'
  if (!fileName.startsWith("/")) {
    fileName = "/" + fileName;
  }
  
  // Send file if found
  if (SPIFFS.exists(fileName)) {
    File file = SPIFFS.open(fileName, "r");
    server.streamFile(file, "application/octet-stream");
    file.close();
    Serial.println(SPIFFS.totalBytes());
    Serial.println(SPIFFS.usedBytes());
    delay(5000);
    SPIFFS.remove(fileName);
  } else {
    server.send(404, "text/plain", "File Not Found");
  }
}

// Toggling recording
void handleToggleRecording() {
  isRecording = !isRecording; // Toggle recording state
  
  if (isRecording) {
    M5.Lcd.println("Recording started via web");
    stopServer(); // Stop server during recording
  } else {
    writeBufferToSPIFFS();
    bufferIndex = 0;  // Reset buffer index
    M5.Lcd.println("Recording stopped via web");
    startServer(); // Restart the server
  }
  
  // Send response to the client
  String response = isRecording ? "Recording started" : "Recording stopped";
  server.send(200, "text/plain", response);
}

