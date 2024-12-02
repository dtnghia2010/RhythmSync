// Define the pin where the AD8232 OUTPUT is connected
#define AD8232_PIN 34  // Analog pin GPIO34 (change if using a different pin)


// Setup function to initialize serial communication
void setup() {
  // Start the serial communication
  Serial.begin(115200);


  // Set the AD8232 pin as input
  pinMode(AD8232_PIN, INPUT);
  Serial.println("AD8232 ECG Sensor Test");
}


// Loop function to read data continuously
void loop() {
  // Read the analog value from the AD8232 output pin
  int ecgValue = analogRead(AD8232_PIN);


  // Print the ECG value to the serial monitor
  Serial.println(ecgValue);


  // Small delay to control the data output rate
  delay(10);  // Adjust this as necessary (10ms for ~100Hz sampling rate)
}

// Define the pin where the AD8232 OUTPUT is connected
// Define the pin where the AD8232 OUTPUT is connected
// #define AD8232_PIN 34  // Analog pin GPIO34 (change if using a different pin)

// // Variables for BPM calculation
// unsigned long lastPeakTime = 0;      // Time of the last detected peak
// unsigned long currentTime = 0;       // Current time
// int threshold = 2500;                 // Threshold for detecting a peak (adjust as necessary)
// bool aboveThreshold = false;         // Flag to track when the signal crosses the threshold
// unsigned long peakTimestamps[600];   // Array to store timestamps of peaks (up to 600 peaks for a minute)
// int peakIndex = 0;                   // Index for storing peak timestamps
// int bpm = 0;                         // Beats per minute (BPM)
// unsigned long lastBPMUpdate = 0;     // Time of the last BPM update

// void setup() {
//   // Start the serial communication
//   Serial.begin(115200);

//   // Set the AD8232 pin as input
//   pinMode(AD8232_PIN, INPUT);
//   Serial.println("AD8232 ECG Sensor BPM Calculation (1-minute Updates)");
// }

// void loop() {
//   // Read the analog value from the AD8232 output pin
//   int ecgValue = analogRead(AD8232_PIN);

//   // Get the current time in milliseconds
//   currentTime = millis();

//   // Detect peaks in the ECG signal
//   if (ecgValue > threshold) {
//     if (!aboveThreshold) {  // Detect the rising edge
//       aboveThreshold = true;  // Signal is above threshold

//       // Store the timestamp of the detected peak
//       peakTimestamps[peakIndex] = currentTime;
//       peakIndex = (peakIndex + 1) % 600;  // Circular buffer to keep peaks for the last minute
//     }
//   } else {
//     aboveThreshold = false;  // Reset flag when below threshold
//   }

//   // Update BPM every minute (60000 ms)
//   if (currentTime - lastBPMUpdate >= 60000) {
//     lastBPMUpdate = currentTime;  // Reset the last update time

//     // Count peaks in the last minute (60 seconds)
//     int peakCount = 0;
//     for (int i = 0; i < 600; i++) {  // Check up to 600 peaks (since 60000ms / 100ms sampling = 600 data points)
//       if (currentTime - peakTimestamps[i] <= 60000) {  // Only count peaks in the last minute
//         peakCount++;
//       }
//     }

//     // Calculate BPM (number of peaks in the last minute)
//     bpm = peakCount;

//     // Print the BPM
//     Serial.print("BPM: ");
//     Serial.println(bpm);
//   }

//   // Small delay to control the data output rate (100Hz sampling rate)
//   delay(10);  // 100Hz sampling rate
// }
