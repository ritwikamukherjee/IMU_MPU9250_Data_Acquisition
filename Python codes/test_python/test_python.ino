// analog-plot
// 
// Read analog values from A0 and A1 and print them to serial port.
//
// electronut.in

#include "Arduino.h"

void setup()
{
  // initialize serial comms
  Serial.begin(9600); 
}

void loop()
{
  // read A0
  int val1 = analogRead(0);
  // read A1
  int val2 = analogRead(1);
  // read A2
  int val3 = analogRead(2);
  // read A3
  int val4 = analogRead(3);
  // read A4
  int val5 = analogRead(4);
  // read A5
  int val6 = analogRead(5);
  // print to serial
  Serial.print(val1);
  Serial.print(" ");
  Serial.print(val2);
  Serial.print(" ");
  Serial.print(val3);
  Serial.print(" ");
  Serial.print(val4);
  Serial.print(" ");
  Serial.print(val5);
  Serial.print(" ");
  Serial.print(val6);
  Serial.print("\n");
  // wait 
  delay(50);
}
