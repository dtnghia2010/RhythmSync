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


