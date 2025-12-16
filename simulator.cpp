#include <Arduino.h>
#define FILTER_ORDER 2

float B_COEFFS[] = {
  0.000000,
  0.020198,
  -0.000000
};

float A_COEFFS[] = {
  1.000000,
  -1.788622,
  0.808858
};

float x_hist[FILTER_ORDER + 1] = {0};
float y_hist[FILTER_ORDER + 1] = {0};

const float fs = 20000.0;
const float dt = 1.0 / fs;

const float test_freq = 1000.0;  // 1 kHz
float t = 0.0;

float process_filter(float x) {
  for (int i = FILTER_ORDER; i > 0; i--) {
    x_hist[i] = x_hist[i - 1];
    y_hist[i] = y_hist[i - 1];
  }

  x_hist[0] = x;

  float y = 0.0;

  for (int i = 0; i <= FILTER_ORDER; i++) {
    y += B_COEFFS[i] * x_hist[i];
  }

  for (int i = 1; i <= FILTER_ORDER; i++) {
    y -= A_COEFFS[i] * y_hist[i];
  }

  y_hist[0] = y;
  return y;
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("2nd Order LPF Simulation Started");
}

void loop() {
  float input_signal = sin(2 * PI * test_freq * t);
  float output_signal = process_filter(input_signal);

  Serial.print("Input:");
  Serial.print(input_signal + 2.0);  // visual offset
  Serial.print(",");
  Serial.print("Output:");
  Serial.println(output_signal);

  t += dt;
  delay(5); 
}
