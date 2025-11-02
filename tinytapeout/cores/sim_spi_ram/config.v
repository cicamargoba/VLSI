//********************************************************************************************************
// Copyright(c) Cypress Semiconductor, 2019. All rights reserved.
// This model is the property of Cypress Semiconductor Corp.
// and is protected by the US copyright laws, any unauthorized
// copying and distribution is prohibited.
// Cypress reserves the right to change any of the functional 
// specifications without any prior notice.
// Cypress is not liable for any damages which may result from
// the use of this functional model
// -------------------------------------------------------------------------------------------------------
// File name : config.v
// -------------------------------------------------------------------------------------------------------
// Functionality : Verilog behavourial Model for Excelon SPI F-RAM
// Source:  CYPRESS Data Sheet : 
// Version:  1.2 May 20, 2019
// -------------------------------------------------------------------------------------------------------
// Developed by CYPRESS SEMICONDUCTOR
//
// version |   author     | mod date |  changes made
//    1.0  |    VINI      | 04/08/17 |  Added tPU, Added MPN
//    1.1  |    ZSK       | 01/09/19 |  Added 8Mb device options; Removed Reset parameters
//    1.2  |    ZSK       | 05/22/19 |  Added 8Mb, 20 MHz (no inrush current control) part option
//                                   |  Removed non supported MPNs
//    1.3  |    ZSK       | 10/15/19 |  Updated the copyright year
// -------------------------------------------------------------------------------------------------------
// PART DESCRIPTION :
// Part:        All parts of Excelon SPI F-RAM
//
// Descripton:  Verilog behavourial Model  for  Excelon SPI F-RAM parts
// ----------------------------------------------------------------------------------------------------------  

//*******************************************************
// Define the F-RAM part
//*******************************************************
//`define CY15V108QI20 
//`define CY15B108QI20 
//`define CY15B108QN40
//`define CY15V108QN20    
//`define CY15V104QI20 
//`define CY15B104QI20  
`define CY15B104QN50   
//`define CY15V102QN50 
//`define CY15B102QN50

//Device config - 1

`ifdef CY15V108QI20 //MPN = CY15V108QI-20xxx
   `define addrBits 20
   `define Memblksize 1048576
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  1.89;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =5000 us   
   parameter tREC =50;//For simulation only; actual tREC =5000 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   //***Commercial temp ID**//
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2F;
   parameter DEV_ID_LSB = 8'hA5;   
   
   //***Industrial temp ID**//
   //parameter DEV_ID_MSB = 8'hC2;
   //parameter DEV_ID_ISB = 8'h2F;
   //parameter DEV_ID_LSB = 8'h05; 

   parameter fMAX  = 20;     // Max. frequency (Mz) 

   parameter tCH = 22;       // min. SCK High Time
   parameter tCL = 22;       // min. SCK LOw Time
 
   parameter tD   = 50;      // min. CS High Time
   parameter tCSU = 10;      // min. CS Setup Time
   parameter tCSH = 10;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 16;      // max. Output Valid from Clock Low
   parameter tOH  =0;        // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
   
   parameter tDPD = 150000; //max. DPD exit time
   
`endif

//Device config - 2

`ifdef CY15B108QI20  //MPN = CY15B108QI-20xxx
   `define addrBits 20
   `define Memblksize 1048576
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  3.6;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =5000 us   
   parameter tREC =50;//For simulation only; actual tREC =5000 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   //***Commercial temp ID**//
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2F;
   parameter DEV_ID_LSB = 8'hA1;   
   
   //***Industrial temp ID**//
   //parameter DEV_ID_MSB = 8'hC2;
   //parameter DEV_ID_ISB = 8'h2F;
   //parameter DEV_ID_LSB = 8'h01;    
   
   parameter fMAX  = 20;     // Max. frequency (Mz) 

   parameter tCH = 22;       // min. SCK High Time
   parameter tCL = 22;       // min. SCK LOw Time
 
   parameter tD   = 50;      // min. CS High Time
   parameter tCSU = 10;      // min. CS Setup Time
   parameter tCSH = 10;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 16;      // max. Output Valid from Clock Low
   parameter tOH  =0;        // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
  
   parameter tDPD = 150000; //max. DPD exit time
   
`endif

 //Device config - 3

`ifdef CY15B108QN40   //MPN = CY15B108QN-40xxx
   `define addrBits 20
   `define Memblksize 1048576
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  3.6;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =450 us   
   parameter tREC =50;//For simulation only; actual tREC =450 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2E;
   parameter DEV_ID_LSB = 8'h00;   
   
   parameter fMAX  = 40;     // Max. frequency (Mz) 

   parameter tCH = 11;       // min. SCK High Time
   parameter tCL = 11;       // min. SCK LOw Time
 
   parameter tD   = 40;      // min. CS High Time
   parameter tCSU = 5;      // min. CS Setup Time
   parameter tCSH = 5;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 9;       // max. Output Valid from Clock Low
   parameter tOH  = 1;       // min. Output HOLD time
   parameter tOD  = 12;      // max. Output Disable Time
   
   parameter tDPD = 10000;	//max. DPD exit time
   
`endif

 //Device config - 4

`ifdef CY15V108QN20   //MPN = CY15V108QN-20xxx
   `define addrBits 20
   `define Memblksize 1048576
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  1.89;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =450 us   
   parameter tREC =50;//For simulation only; actual tREC =450 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2E;
   parameter DEV_ID_LSB = 8'hA5;   
   
   parameter fMAX  = 20;     // Max. frequency (Mz) 

   parameter tCH = 22;       // min. SCK High Time
   parameter tCL = 22;       // min. SCK LOw Time
 
   parameter tD   = 60;      // min. CS High Time
   parameter tCSU = 10;      // min. CS Setup Time
   parameter tCSH = 10;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 20;       // max. Output Valid from Clock Low
   parameter tOH  = 1;       // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
   
   parameter tDPD = 10000;	//max. DPD exit time
   
`endif


//Device config - 5

`ifdef CY15V104QI20 //MPN = CY15V104QI-20xxx
   `define addrBits 19
   `define Memblksize 524288
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  1.89;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =5000 us   
   parameter tREC =50;//For simulation only; actual tREC =5000 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2D;
   parameter DEV_ID_LSB = 8'hA5;   
   
   parameter fMAX  = 20;     // Max. frequency (Mz) 

   parameter tCH = 22;       // min. SCK High Time
   parameter tCL = 22;       // min. SCK LOw Time
 
   parameter tD   = 50;      // min. CS High Time
   parameter tCSU = 10;      // min. CS Setup Time
   parameter tCSH = 10;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 16;      // max. Output Valid from Clock Low
   parameter tOH  =0;        // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
   
   parameter tDPD = 150000; //max. DPD exit time
   
`endif

//Device config - 6

`ifdef CY15B104QI20  //MPN = CY15B104QI-20xxx
   `define addrBits 19
   `define Memblksize 524288
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  3.6;
   parameter hasWP = ;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =5000 us   
   parameter tREC =50;//For simulation only; actual tREC =5000 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2D;
   parameter DEV_ID_LSB = 8'hA1;   
   
   parameter fMAX  = 20;     // Max. frequency (Mz) 

   parameter tCH = 22;       // min. SCK High Time
   parameter tCL = 22;       // min. SCK LOw Time
 
   parameter tD   = 50;      // min. CS High Time
   parameter tCSU = 10;      // min. CS Setup Time
   parameter tCSH = 10;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 16;      // max. Output Valid from Clock Low
   parameter tOH  =0;        // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
   
   parameter tDPD = 150000; //max. DPD exit time
   
`endif

//Device config - 7

`ifdef CY15B104QN50   //MPN = CY15B104QN-50xxx
   `define addrBits 19
   `define Memblksize 524288
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 256
   
   parameter Vddmax    =  3.6;
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1; 
   parameter hasDeviceid = 1;            
   parameter hasSN = 1;
   parameter tPU = 50;//For simulation only; actual tPU  =450 us   
   parameter tREC =50;//For simulation only; actual tREC =450 us   
   parameter hasfastread = 1;                  
   
   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2C;
   parameter DEV_ID_LSB = 8'h00;   
   
   parameter fMAX  = 50;     // Max. frequency (Mz) 

   parameter tCH = 09;       // min. SCK High Time
   parameter tCL = 09;       // min. SCK LOw Time
 
   parameter tD   = 40;      // min. CS High Time
   parameter tCSU = 5;      // min. CS Setup Time
   parameter tCSH = 5;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 7;       // max. Output Valid from Clock Low
   parameter tOH  = 1;       // min. Output HOLD time
   parameter tOD  = 6;      // max. Output Disable Time
  
   parameter tDPD = 10000;	//max. DPD exit time
   
`endif

//Device config - 8

`ifdef CY15V102QN50 //MPN = CY15V102QN-50xxx
   `define addrBits 18
   `define Memblksize 262144
   `define THREE_BYTE_ADDR
   `define specialsectorsize 256
      
   parameter Vddmax    =  1.89;      
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1;    
   parameter hasDeviceid = 1;         
   parameter hasSN = 0;
   parameter tPU = 50;//For simulation only; actual tPU  =450 us   
   parameter tREC =50;//For simulation only; actual tREC =450 us   
   parameter hasfastread = 1;                     

   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2C;
   parameter DEV_ID_LSB = 8'h64;
   
   parameter fMAX  = 50;     // Max. frequency (Mz) 

   parameter tCH = 9;       // min. SCK High Time
   parameter tCL = 9;       // min. SCK LOw Time
 
   parameter tD   = 40;      // min. CS High Time
   parameter tCSU = 5;      // min. CS Setup Time
   parameter tCSH = 5;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 7;       // max. Output Valid from Clock Low
   parameter tOH  = 1;       // min. Output HOLD time
   parameter tOD  = 6;      // max. Output Disable Time
   
   parameter tDPD = 10000;	//max. DPD exit time

`endif

//Device config - 9

`ifdef CY15B102QN50 //MPN = CY15B102QN-50xxx
   `define addrBits 18
   `define Memblksize 262144
   `define THREE_BYTE_ADDR
   `define specialsectorsize 256
      
   parameter Vddmax    =  3.6;      
   parameter hasWP = 1;
   parameter hasSleep = 1; 
   parameter hasDPD = 1;    
   parameter hasDeviceid = 1;         
   parameter hasSN = 0;
   parameter tPU = 50;//For simulation only; actual tPU  =450 us   
   parameter tREC =50;//For simulation only; actual tREC =450 us   
   parameter hasfastread = 1;                     

   parameter addrBytes = 3;
   
   parameter DEV_ID_MSB = 8'hC2;
   parameter DEV_ID_ISB = 8'h2A;
   parameter DEV_ID_LSB = 8'h60;
   
   parameter fMAX  = 50;     // Max. frequency (Mz) 

   parameter tCH = 9;       // min. SCK High Time
   parameter tCL = 9;       // min. SCK LOw Time
 
   parameter tD   = 40;      // min. CS High Time
   parameter tCSU = 5;      // min. CS Setup Time
   parameter tCSH = 5;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 7;       // max. Output Valid from Clock Low
   parameter tOH  = 1;       // min. Output HOLD time
   parameter tOD  = 6;      // max. Output Disable Time
   
   parameter tDPD = 10000;	//max. DPD exit time


//_______________________________________________________________________
//  Uncomment only if you want to initialize memory with values from a file
//
//`define       initMemFile     "init.dat"