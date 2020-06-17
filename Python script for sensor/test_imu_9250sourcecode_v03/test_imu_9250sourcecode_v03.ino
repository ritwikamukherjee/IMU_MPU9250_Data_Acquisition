 #include<Wire.h>
#include "Timer.h"

#define    MPU9250_ADDRESS            0x68  //for ADO = 0 LOW 
#define    MAG_ADDRESS                0x0C  //  Address of magnetometer
 
#define    GYRO_FULL_SCALE_250_DPS    0x00  
#define    GYRO_FULL_SCALE_500_DPS    0x08
#define    GYRO_FULL_SCALE_1000_DPS   0x10
#define    GYRO_FULL_SCALE_2000_DPS   0x18
#define    PWR_MGMT_1                0x6B // Device defaults to the SLEEP mode
#define    ACC_FULL_SCALE_2_G        0x00  
#define    ACC_FULL_SCALE_4_G        0x08
#define    ACC_FULL_SCALE_8_G        0x10
#define    ACC_FULL_SCALE_16_G       0x18
#define    INT_ENABLE                0x38
#define    INT_STATUS                0x3A
#define    MAG_CNTL                  0x0A // Power down (0000), single-measurement (0001), self-test (1000) and Fuse ROM (1111) modes on bits 
#define    MAG_ASTC                  0x0C  // Self test control
#define    MAG_ST2                   0x09 // Data overflow bit 3 and data read error status bit 2
#define    MAG_I2CDIS                0x0F  // I2C disable
#define    MAG_ASAX                  0x10  // Fuse ROM x-axis sensitivity adjustment value
#define    MAG_ASAY                  0x11  // Fuse ROM y-axis sensitivity adjustment value
#define    MAG_ASAZ                  0x12  // Fuse ROM z-axis sensitivity adjustment value
#define    CONFIG           0x1A
#define    GYRO_CONFIG      0x1B
#define    ACCEL_CONFIG     0x1C
#define    ACCEL_CONFIG2    0x1D
#define    SMPLRT_DIV       0x19
#define    INT_PIN_CFG     0x37
#define    SerialDebug   true // set to true to get Serial output for debugging

#define START_BYTE1 3   //8 bits
#define START_BYTE2 31  //3<<8|31=799
#define FREQUENCY 250 // in Hz; freq=1000/cycle_period
#define DATA_LENGTH 25

Timer tt;
byte DAQ_Data[DATA_LENGTH];
int ii;
unsigned int xx;


// Set initial input parameters
enum Ascale {
  AFS_2G = 0,
  AFS_4G,
  AFS_8G,
  AFS_16G
};

enum Gscale {
  GFS_250DPS = 0,
  GFS_500DPS,
  GFS_1000DPS,
  GFS_2000DPS
};

enum Mscale {
  MFS_14BITS = 0, // 0.6 mG per LSB
  MFS_16BITS     // 0.15 mG per LSB magnetometer resolution
};
// Specify sensor full scale
uint8_t Gscale = GFS_1000DPS;
uint8_t Ascale = AFS_16G;
uint8_t Mscale = MFS_16BITS; // MFS_14BITS or MFS_16BITS, 14-bit or 16-bit magnetometer resolution
uint8_t Mmode = 0x06;        // Either 8 Hz (0x02) or 100 Hz (0x06) magnetometer data ODR 
float aRes, gRes, mRes; // scale resolutions per LSB for the sensors

uint8_t MPU9250Data[14]; // used to read all 14 bytes at once from the MPU9250 accel/gyro
int16_t accelCount[3];   // Stores the 16-bit signed accelerometer sensor output
int16_t gyroCount[3];    // Stores the 16-bit signed gyro sensor output
uint8_t magCount[6];     // Stores the 16-bit signed magnetometer sensor output
float magCalibration[3] = {0, 0, 0}, magbias[3] = {0, 0, 0};  // Factory mag calibration and mag bias
float gyroBias[3] = {0, 0, 0}, accelBias[3] = {0, 0, 0};      // Bias corrections for gyro and accelerometer
int16_t tempCount;      // temperature raw count output
float   temperature;    // Stores the real internal chip temperature in degrees Celsius
float pitch, yaw, roll;
float ax, ay, az, gx, gy, gz, mx, my, mz; // variables to hold latest sensor data values 


//===================================================================================================================
//====== Set of useful function to access acceleration. gyroscope, magnetometer, and temperature data
//===================================================================================================================
 
// This function read Nbytes bytes from I2C device at address Address. 
// Put read bytes starting at register Register in the Data array. 

void I2Cread(uint8_t Address, uint8_t Register, uint8_t Nbytes, uint8_t* Data)
{
  // Set register address
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.endTransmission();
 
  // Read Nbytes
  Wire.requestFrom(Address, Nbytes); 
  uint8_t index=0;
  while (Wire.available())
    Data[index++]=Wire.read();
}
 
// Write a byte (Data) in device (Address) at register (Register)
void I2CwriteByte(uint8_t Address, uint8_t Register, uint8_t Data)
{
  // Set register address
  Wire.beginTransmission(Address);
  Wire.write(Register);
  Wire.write(Data);
  Wire.endTransmission();
}
 
uint8_t readByte(uint8_t address, uint8_t subAddress)
{
  uint8_t data; // `data` will store the register data   
  Wire.beginTransmission(address);         // Initialize the Tx buffer
  Wire.write(subAddress);                  // Put slave register address in Tx buffer
  Wire.endTransmission(false);             // Send the Tx buffer, but send a restart to keep connection alive
  Wire.requestFrom(address, (uint8_t) 1);  // Read one byte from slave register address 
  data = Wire.read();                      // Fill Rx buffer with result
  return data;                             // Return data read from slave register
}

void getMres() {
  switch (Mscale)
  {
   // Possible magnetometer scales (and their register bit settings) are:
  // 14 bit resolution (0) and 16 bit resolution (1)
    case MFS_14BITS:
          mRes = 10.*4912./8190.; // Proper scale to return milliGauss
          break;
    case MFS_16BITS:
          mRes = 10.*4912./32760.0; // Proper scale to return milliGauss
          break;
  }
}

void getGres() {
  switch (Gscale)
  {
  // Possible gyro scales (and their register bit settings) are:
  // 250 DPS (00), 500 DPS (01), 1000 DPS (10), and 2000 DPS  (11). 
        // Here's a bit of an algorith to calculate DPS/(ADC tick) based on that 2-bit value:
    case GFS_250DPS:
          gRes = 250.0/32768.0;
          break;
    case GFS_500DPS:
          gRes = 500.0/32768.0;
          break;
    case GFS_1000DPS:
          gRes = 1000.0/32768.0;
          break;
    case GFS_2000DPS:
          gRes = 2000.0/32768.0;
          break;
  }
}

void getAres() {
  switch (Ascale)
  {
  // Possible accelerometer scales (and their register bit settings) are:
  // 2 Gs (00), 4 Gs (01), 8 Gs (10), and 16 Gs  (11). 
        // Here's a bit of an algorith to calculate DPS/(ADC tick) based on that 2-bit value:
    case AFS_2G:
          aRes = 2.0/32768.0;
          break;
    case AFS_4G:
          aRes = 4.0/32768.0;
          break;
    case AFS_8G:
          aRes = 8.0/32768.0;
          break;
    case AFS_16G:
          aRes = 16.0/32768.0;
          break;
  }
}

void readMPU9250Data(uint8_t * destination)
{
  uint8_t rawData[14];  // x/y/z accel register data stored here
  I2Cread(MPU9250_ADDRESS, 0X3B, 14, &rawData[0]);  // Read the 14 raw data registers into data array
  //destination=rawData;
    for (int i = 0; i < 14; i++) {
      destination[i]= rawData[i];
    }
  //destination[0] = ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a signed 16-bit value
  //destination[1] = ((int16_t)rawData[2] << 8) | rawData[3] ;  
  //destination[2] = ((int16_t)rawData[4] << 8) | rawData[5] ; 
  //destination[3] = ((int16_t)rawData[6] << 8) | rawData[7] ;   
  //destination[4] = ((int16_t)rawData[8] << 8) | rawData[9] ;  
  //destination[5] = ((int16_t)rawData[10] << 8) | rawData[11] ;  
  //destination[6] = ((int16_t)rawData[12] << 8) | rawData[13] ; 
  
}

//void readAccelData(int16_t * destination)
//{
//  uint8_t rawData[6];  // x/y/z accel register data stored here
//  I2Cread(MPU9250_ADDRESS, 0x3B, 6, &rawData[0]);  // Read the six raw data registers into data array //ACCEL_XOUT_H 0x3B
//  destination[0] = ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a signed 16-bit value
//  destination[1] = ((int16_t)rawData[2] << 8) | rawData[3] ;  
//  destination[2] = ((int16_t)rawData[4] << 8) | rawData[5] ; 
//}


//void readGyroData(int16_t * destination)
//{
//  uint8_t rawData[6];  // x/y/z gyro register data stored here
//  I2Cread(MPU9250_ADDRESS, 0x43, 6, &rawData[0]);  // Read the six raw data registers sequentially into data array //GYRO_XOUT_H 0x43
//  destination[0] = ((int16_t)rawData[0] << 8) | rawData[1] ;  // Turn the MSB and LSB into a signed 16-bit value
//  destination[1] = ((int16_t)rawData[2] << 8) | rawData[3] ;  
//  destination[2] = ((int16_t)rawData[4] << 8) | rawData[5] ; 
//}

void readMagData(uint8_t * destination)
{
  uint8_t rawData[7];  // x/y/z gyro register data, ST2 register stored here, must read ST2 at end of data acquisition
  if(readByte(MAG_ADDRESS, 0x02) & 0x01) { // wait for magnetometer data ready bit to be set
  I2Cread(MAG_ADDRESS, 0x03, 7, &rawData[0]);  // Read the six raw data and ST2 registers sequentially into data array
  uint8_t c = rawData[6]; // End data read by reading ST2 register
    if(!(c & 0x08)) { // Check if magnetic sensor overflow set, if not then report data
    destination[0]= rawData[1];
    destination[1]= rawData[0];
    destination[2]= rawData[3];
    destination[3]= rawData[2];
    destination[4]= rawData[5];
    destination[5]= rawData[4];
    
    //destination[0] = ((int16_t)rawData[1] << 8) | rawData[0] ;  // Turn the MSB and LSB into a signed 16-bit value
    //destination[1] = ((int16_t)rawData[3] << 8) | rawData[2] ;  // Data stored as little Endian
    //destination[2] = ((int16_t)rawData[5] << 8) | rawData[4] ; 
   }
  }
}


void initMAG()
{
  // First extract the factory calibration for each magnetometer axis
  uint8_t rawData[3];  // x/y/z gyro calibration data stored here
  I2CwriteByte(MAG_ADDRESS, MAG_CNTL, 0x00); // Power down magnetometer  
  I2CwriteByte(MAG_ADDRESS, MAG_CNTL, 0x0F); // Enter Fuse ROM access mode
  //I2Cread(MAG_ADDRESS, MAG_ASAX, 3, &rawData[0]);  // Read the x-, y-, and z-axis calibration values
  //destination[0] =  (float)(rawData[0] - 128)/256. + 1.;   // Return x-axis sensitivity adjustment values, etc. ADJUSTMENTS!
  //destination[1] =  (float)(rawData[1] - 128)/256. + 1.;  
  //destination[2] =  (float)(rawData[2] - 128)/256. + 1.; 
  I2CwriteByte(MAG_ADDRESS,MAG_CNTL, 0x00); // Power down magnetometer  
  // Configure the magnetometer for continuous read and highest resolution
  // set Mscale bit 4 to 1 (0) to enable 16 (14) bit resolution in CNTL register,
  // and enable continuous mode data acquisition Mmode (bits [3:0]), 0010 for 8 Hz and 0110 for 100 Hz sample rates
  I2CwriteByte(MAG_ADDRESS, MAG_CNTL, Mscale << 4 | Mmode); // Set magnetometer data resolution and sample ODR
}

void initMPU9250()
{  
      // wake up device
  I2CwriteByte(MPU9250_ADDRESS, PWR_MGMT_1, 0x00); // Clear sleep mode bit (6), enable all sensors 
  //delay(100);    // Wait for all registers to reset   
  I2CwriteByte(MPU9250_ADDRESS, PWR_MGMT_1, 0x01);  // Auto select clock source to be PLL gyroscope reference if ready else
  
 // Configure Gyro and Thermometer
 // Disable FSYNC and set thermometer and gyro bandwidth to 41 and 42 Hz, respectively; 
 // minimum delay time for this setting is 5.9 ms, which means sensor fusion update rates cannot
 // be higher than 1 / 0.0059 = 170 Hz
 // DLPF_CFG = bits 2:0 = 011; this limits the sample rate to 1000 Hz for both
 // With the MPU9250, it is possible to get gyro sample rates of 32 kHz (!), 8 kHz, or 1 kHz CHANGED TO 8KHZ
  I2CwriteByte(MPU9250_ADDRESS, CONFIG, 0x03);  

 // Set sample rate = gyroscope output rate/(1 + SMPLRT_DIV)
  //I2CwriteByte(MPU9250_ADDRESS, SMPLRT_DIV, 0x00);  // Use a 1KHz rate; a rate consistent with the filter update rate 
                                    // determined inset in CONFIG above; 8KHZ/(1+7)=1KHZ
 
 // Set gyroscope full scale range
 // Range selects FS_SEL and AFS_SEL are 0 - 3, so 2-bit values are left-shifted into positions 4:3
  uint8_t c = readByte(MPU9250_ADDRESS, GYRO_CONFIG); // get current GYRO_CONFIG register value
 // c = c & ~0xE0; // Clear self-test bits [7:5] 
  c = c & ~0x02; // Clear Fchoice bits [1:0] 
  c = c & ~0x18; // Clear AFS bits [4:3]
  c = c | Gscale << 3; // Set full scale range for the gyro
 // c =| 0x00; // Set Fchoice for the gyro to 11 by writing its inverse to bits 1:0 of GYRO_CONFIG
  I2CwriteByte(MPU9250_ADDRESS, GYRO_CONFIG, c ); // Write new GYRO_CONFIG value to register
  
 // Set accelerometer full-scale range configuration
  c = readByte(MPU9250_ADDRESS, ACCEL_CONFIG); // get current ACCEL_CONFIG register value
 // c = c & ~0xE0; // Clear self-test bits [7:5] 
  c = c & ~0x18;  // Clear AFS bits [4:3]
  c = c | Ascale << 3; // Set full scale range for the accelerometer 
  I2CwriteByte(MPU9250_ADDRESS, ACCEL_CONFIG, c); // Write new ACCEL_CONFIG register value

 // Set accelerometer sample rate configuration
 // It is possible to get a 4 kHz sample rate from the accelerometer by choosing 1 for accel_fchoice_b bit [3]; in this case the bandwidth is 1.13 kHz
  c = readByte(MPU9250_ADDRESS, ACCEL_CONFIG2); // get current ACCEL_CONFIG2 register value
  c = c & ~0x0F; // Clear accel_fchoice_b (bit 3) and A_DLPFG (bits [2:0])  
  c = c | 0x03;  // Set accelerometer rate to 1 kHz and bandwidth to 41 Hz (A_DLPF_CFG=3)
  I2CwriteByte(MPU9250_ADDRESS, ACCEL_CONFIG2, c); // Write new ACCEL_CONFIG2 register value
 // The accelerometer, gyro, and thermometer are set to 1 kHz sample rates, 
 // but all these rates are further reduced by a factor of 5 to 200 Hz because of the SMPLRT_DIV setting

  // Configure Interrupts and Bypass Enable
  // Set interrupt pin active high, push-pull, hold interrupt pin level HIGH until interrupt cleared,
  // clear on read of INT_STATUS, and enable I2C_BYPASS_EN so additional chips 
  // can join the I2C bus and all can be controlled by the Arduino as master
   I2CwriteByte(MPU9250_ADDRESS, INT_PIN_CFG, 0x22);    
   I2CwriteByte(MPU9250_ADDRESS, INT_ENABLE, 0x01);  // Enable data ready (bit 0) interrupt
   
}

// Initializations
void setup()
{
  // Arduino initializations
  Wire.begin();
  Serial.begin(115200);
 
  // Read the WHO_AM_I register, this is a good test of communication
  //byte c = readByte(MPU9250_ADDRESS, WHO_AM_I_MPU9250);  // Read WHO_AM_I register for MPU-9250
  //Serial.print("MPU9250 "); Serial.print("I AM "); Serial.print(c, HEX); Serial.print(" I should be "); Serial.println(0x71, HEX);
  // Read the WHO_AM_I register, this is a good test of communication
  //byte d = readByte(MAG_ADDRESS, 0x00);  // Read WHO_AM_I register for AK8963
  //Serial.print("AK8963 "); Serial.print("I AM "); Serial.print(d, HEX); Serial.print(" I should be "); Serial.println(0x48, HEX);
  getMres();
  getAres();
  getGres();
  DDRC = DDRC&B11111110; //set PortC as input 0 inputs; 1 is output
  tt.every(1000/FREQUENCY,THEDAQ); //every (something seconds)
  xx=0;
  DAQ_Data[0] = START_BYTE1;
  DAQ_Data[1] = START_BYTE2;
  initMPU9250(); 
  initMAG();
  
}
 
// Main loop, read and display data
void THEDAQ()
{
   // If intPin goes high, all data registers have new data
  if (readByte(MPU9250_ADDRESS, INT_STATUS) & 0x01) {  // On interrupt, check if data ready interrupt
    
    
    readMPU9250Data(MPU9250Data); // INT cleared on any read
    //readAccelData(accelCount);  // Read the x/y/z adc values
    // Now we'll calculate the accleration value into actual g's
    //ax = (float)MPU9250Data[0]*aRes; // - accelBias[0];  // get actual g value, this depends on scale being set
    //ay = (float)MPU9250Data[1]*aRes; // - accelBias[1];   
    //az = (float)MPU9250Data[2]*aRes; // - accelBias[2];  
   
    //readGyroData(gyroCount);  // Read the x/y/z adc values
    // Calculate the gyro value into actual degrees per second
    //gx = (float)MPU9250Data[4]*gRes;  // get actual gyro value, this depends on scale being set
    //gy = (float)MPU9250Data[5]*gRes;  
    //gz = (float)MPU9250Data[6]*gRes;   
  
    readMagData(magCount);  // Read the x/y/z adc values
   
    //magbias[0] = +470.;  // User environmental x-axis correction in milliGauss, should be automatically calculated. Take from magcal code
    //magbias[1] = +120.;  // User environmental x-axis correction in milliGauss
    //magbias[2] = +125.;  // User environmental x-axis correction in milliGauss
    
    // Calculate the magnetometer values in milliGauss
    // Include factory calibration per data sheet and user environmental corrections
    //mx = (float)magCount[0]*magCalibration[0] - magbias[0];  // get actual magnetometer value, this depends on scale being set
    //my = (float)magCount[1]*magCalibration[1] - magbias[1];  
    //mz = (float)magCount[2]*magCalibration[2] - magbias[2];  
}
   for(ii=0;ii<14;ii++)
  {
    DAQ_Data[ii+2]=MPU9250Data[ii];    
  }
  for(ii=0;ii<6;ii++)
  {
    DAQ_Data[ii+16]=magCount[ii];
  }
  // Writing the double for the
  
  DAQ_Data[22] = (byte)(xx<<8); 
  DAQ_Data[23] = (byte)xx; //arduino time
  
  DAQ_Data[24]= PINC;
  Serial.write(DAQ_Data,DATA_LENGTH); 
  xx++;
   //if(SerialDebug) {
    // Print acceleration values in milligs!
    //Serial.print(1000*ax); Serial.print(" mg ");
    //Serial.print(1000*ay); Serial.print(" mg ");
    //Serial.print(1000*az); Serial.println(" mg ");
 
    // Print gyro values in degree/sec
    //Serial.print(gx, 3); Serial.print(" degrees/sec "); 
    //Serial.print(gy, 3); Serial.print(" degrees/sec "); 
    //Serial.print(gz, 3); Serial.println(" degrees/sec"); 
    
    // Print mag values in degree/sec
   //Serial.print(mx); Serial.print(" mG "); 
   //Serial.print(my); Serial.print(" mG "); 
   //Serial.print(mz); Serial.println(" mG"); 
}

void loop(){
  tt.update();
}
