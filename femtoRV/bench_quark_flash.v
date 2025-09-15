`timescale 1ns / 1ps
module bench();
// Testbench uses a 10 MHz clock
// Want to interface to 115200 baud UART
// 25000000 / 115200 = 217 Clocks Per Bit.
parameter tck              = 40;
parameter c_BIT_PERIOD     = 8680;

   reg CLK;
   reg i;
   reg RESET; 
   wire LEDS;
   reg  RXD = 1'b0;
   wire TXD;
   wire spi_cs;
   wire spi_clk;
   wire spi_miso;
   wire spi_mosi;



  // Takes in input byte and serializes it 
  task UART_WRITE_BYTE;
    input [7:0] i_Data;
    integer     ii;
    begin
       
      // Send Start Bit
      RXD <= 1'b0;
      #(c_BIT_PERIOD);
      #1000;
       
       
      // Send Data Byte
      for (ii=0; ii<8; ii=ii+1)
        begin
          RXD <= i_Data[ii];
          #(c_BIT_PERIOD);
        end
       
      // Send Stop Bit
      RXD <= 1'b1;
      #(c_BIT_PERIOD);
     end
  endtask // UART_WRITE_BYTE
  
  
   femto uut(
     .clk(CLK),
     .resetn(RESET),
     .spi_mosi(spi_mosi), 
     .spi_miso(spi_miso), 
     .spi_cs_n(spi_cs),
     .spi_clk(spi_clk),
     .LEDS(LEDS),
     .RXD(RXD),
     .TXD(TXD)
   );

 spiflash flash0(
	.csb(spi_cs),
	.clk(spi_clk),
	.io0(spi_mosi), // MOSI
	.io1(spi_miso) // MISO
);


initial         CLK <= 0;
always #(tck/2) CLK <= ~CLK;


   reg[4:0] prev_LEDS = 0;
   initial begin
	 if(LEDS != prev_LEDS) begin
	    $display("LEDS = %b",LEDS);
	 end
	 prev_LEDS <= LEDS;
	
   end
   
   
       integer idx; 
   initial begin

`ifdef BENCH
    $dumpfile("bench.vcd");
    $dumpvars(-1,bench);
//    for(idx = 0; idx < 32; idx = idx +1)  $dumpvars(0, bench.uut.CPU.registerFile[idx]);
//    for(idx = 0; idx < 16; idx = idx +1)  $dumpvars(0, bench.uut.RAM.MEM[idx]);
`endif

    #0   RXD   = 1;
    #0   RESET = 0;
    #80  RESET = 0;
    #160 RESET = 1;
    // Send a command to the UART (exercise Rx)
    @(posedge CLK);
    #(tck*200000)
    UART_WRITE_BYTE(8'h34);
    #(tck*4000)
    UART_WRITE_BYTE(8'h2A);    // Operator *
    #(tck*4000)  
    UART_WRITE_BYTE(8'h34);
    #(tck*4000)
    UART_WRITE_BYTE(8'h39);
    #(tck*4000)
    UART_WRITE_BYTE(8'h2F);   // operator /
    #(tck*4000)
    UART_WRITE_BYTE(8'h30);


    
    @(posedge CLK);
    #(tck*100000) $finish;
 end
 
 
endmodule   
 
