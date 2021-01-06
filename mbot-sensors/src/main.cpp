#include <Arduino.h>
#include <MeShield.h>

MeRGBLed led1(PORT_3, SLOT_1, 15);   /* parameter description: port, slot, led number */
MeRGBLed led2(PORT_3, SLOT_2, 15);
MeTemperature myTemp(PORT_1, SLOT_2);
MeUltrasonicSensor ultraSensor(PORT_2);

int loopcount = 0;

void setup() {
  Serial.begin(9600);
  while (!Serial) continue;

  led1.setColor(1, 255, 0, 255); // parameter description: led number, red, green, blue
  led1.setColor(2, 255, 255, 0); // parameter description: led number, red, green, blue
  led1.show();
}

void loop() {
  loopcount++;

  if(loopcount%2)
  {
      led1.setColor(1, 0, 255, 255); // parameter description: led number, red, green, blue
      led1.setColor(2, 255, 0, 255); // parameter description: led number, red, green, blue
      led1.show();
  }
  else
  {
      led1.setColor(1, 255, 0, 255); // parameter description: led number, red, green, blue
      led1.setColor(2, 0, 255, 255); // parameter description: led number, red, green, blue
      led1.show();
  }

  Serial.print(myTemp.temperature() );
  Serial.print(",");
  Serial.println(ultraSensor.distanceCm() );
  delay(1000); /* the minimal measure interval is 100 milliseconds */
}