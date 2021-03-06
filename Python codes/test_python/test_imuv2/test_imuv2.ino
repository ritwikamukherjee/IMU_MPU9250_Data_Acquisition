// Vishesh Vikas

#include<Wire.h>
#include "Timer.h"
const int MPU_addr=0x68;  // I2C address of the MPU-6050
#define START_BYTE1 3   //8 bits
#define START_BYTE2 31  //3<<8|31=799
#define FREQUENCY 250 // in millisec; freq=1000/cycle_period

#define DATA_LENGTH 18
byte DAQ_Data[DATA_LENGTH];
Timer tt;
int ii;
unsigned int xx;
void setup(){
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);  // PWR_MGMT_1 register
  Wire.write(0);     // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  Serial.begin(115200);
  tt.every(1000/FREQUENCY,theDAQ);
  xx=0;
  DAQ_Data[0] = START_BYTE1;
  DAQ_Data[1] = START_BYTE2;
}

void loop(){
  tt.update();
}

void theDAQ(){
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);  // request a total of 14 registers

// IMPORTANT => THE REGISTER ORDER - Accelerations, Tempertature and then Gyro
//  0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    //2 bytes for each accel x
//  0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
//  0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
//  0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
//  0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
//  0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
//  0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)    
  for(ii=0;ii<14;ii++)
  {
    DAQ_Data[ii+2]=Wire.read();    
  }
  // Writing the double for the
  DAQ_Data[16] = (byte)(xx>>8);
  DAQ_Data[17] = (byte)xx;
  Serial.write(DAQ_Data,DATA_LENGTH);
  xx++;
}
