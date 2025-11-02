   `define addrBits 20
   `define Memblksize 1048576
   `define THREE_BYTE_ADDR   
   `define specialsectorsize 1024
   
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

   parameter tCH = 0;       // min. SCK High Time
   parameter tCL = 0;       // min. SCK LOw Time
 
   parameter tD   = 0;      // min. CS High Time
   parameter tCSU = 0;      // min. CS Setup Time
   parameter tCSH = 0;      // min. CS HOLD Time

   parameter tSU = 5;        // min. Data In Setup Time
   parameter tH  = 5;        // min. Data In Hold Time 

   parameter tODV = 16;      // max. Output Valid from Clock Low
   parameter tOH  =0;        // min. Output HOLD time
   parameter tOD  = 20;      // max. Output Disable Time
   
   parameter tDPD = 150000; //max. DPD exit time
   

//_______________________________________________________________________
//  Uncomment only if you want to initialize memory with values from a file
//
//`define       initMemFile     "init.dat"