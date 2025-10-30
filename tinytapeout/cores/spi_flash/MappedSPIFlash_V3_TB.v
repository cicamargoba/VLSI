`timescale 1ns / 1ps
`define SIMULATION
module MappedSPIFlash_TB;
   reg  clk;
   reg  reset;
   reg  rstrb;
   reg  [19:0] word_address;

   wire [31:0] rdata;
   wire  rbusy;
   wire CLK;
   wire CS_N;
   wire MISO;
   wire MOSI;
   
   MappedSPIFlash uut (.clk(clk) , .reset(reset), .rstrb(rstrb) , .word_address(word_address) , .rdata(rdata) , .rbusy(rbusy) , .CLK(CLK) , .CS_N(CS_N), .MOSI(MOSI), .MISO(MISO)    );
 
  spiflash flash0(
    .csb(CS_N),
    .clk(CLK),
    .io0(MOSI), // MOSI
    .io1(MISO) // MISO
  );
    

   parameter PERIOD          = 20;
   parameter real DUTY_CYCLE = 0.5;
   parameter OFFSET          = 0;
   reg [20:0] i;
	 initial begin  // Initialize Inputs
      clk = 0; reset = 1; rstrb = 0; word_address = 20'h0000;
   end
   initial  begin  // Process for clk
     #OFFSET;
     forever
       begin
         clk = 1'b0;
         #(PERIOD-(PERIOD*DUTY_CYCLE)) clk = 1'b1;
         #(PERIOD*DUTY_CYCLE);
       end
   end
   initial begin // Reset the system, Start the image capture process
       repeat (3) @ (posedge clk);
       reset = 0;
       @ (posedge clk);
       reset = 1;
       for(i=0; i<32; i=i+1) begin
         repeat (1) @ (posedge clk);
         rstrb = 0;
         word_address = i;
         repeat (1) @ (posedge clk);
         rstrb = 1;
         repeat (1) @ (posedge clk);
         rstrb = 0;
         repeat (100*5) @ (posedge clk);



       end
   end	 
   initial begin: TEST_CASE
     $dumpfile("MappedSPIFlash_V3_TB.vcd");
     $dumpvars(-1, uut);
     #((PERIOD*DUTY_CYCLE)*12000*5) $finish;
   end
endmodule

