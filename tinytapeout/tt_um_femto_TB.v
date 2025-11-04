`timescale 1ns / 1ps
module tt_um_femto_TB();
// Testbench uses a 10 MHz clock
// Want to interface to 115200 baud UART
// 25000000 / 115200 = 217 Clocks Per Bit.
parameter tck              = 40;
parameter c_BIT_PERIOD     = 8680;
wire VPWR = 1'b1;
wire VGND = 1'b0;

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
   wire spi_cs_n_ram;
   wire spi_clk_ram;
   wire spi_miso_ram;
   wire spi_mosi_ram;

tt_um_femto uut(
    .clk    (CLK),
    .ena    (ena),
    .rst_n  (RESET),
`ifndef BENCH
    .VPWR   (VPWR),
    .VGND   (VGND),
`endif
    .ui_in  ({5'b00000, RXD, spi_miso_ram, spi_miso}),
    .uo_out ({TXD, LEDS, spi_clk, spi_clk_ram, spi_cs_n_ram, spi_cs, spi_mosi_ram, spi_mosi}));


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

 spiflash flash0(
	.csb(spi_cs),
	.clk(spi_clk),
	.io0(spi_mosi), // MOSI
	.io1(spi_miso) // MISO
);


// spiram flashram0(
//   .CS(spi_cs_n_ram),     // Chip Select (activo en bajo)
//   .SCK(spi_clk_ram),    // SPI Clock
//   .SI(spi_mosi_ram),     // Serial Input (MOSI)
//   .SO(spi_miso_ram)     // Serial Output (MISO)
// );



  FRAM_SPI flashram0(
   .CSB(spi_cs_n_ram),     // Chip Select (activo en bajo)
   .SCK(spi_clk_ram),    // SPI Clock
   .SI(spi_mosi_ram),     // Serial Input (MOSI)
   .SO(spi_miso_ram),     // Serial Output (MISO)
   .VDD(reset_n),
   .WPB(1'b1)
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


    $dumpfile("tt_um_femto_TB.vcd");
    $dumpvars(-1,uut);
`ifdef SIM
    for(idx = 0; idx < 32; idx = idx +1)  $dumpvars(0, tt_um_femto_TB.uut.femto0.CPU.registerFile[idx]);
    for(idx = 32; idx < 65; idx = idx +1)  $dumpvars(0, tt_um_femto_TB.uut.femto0.flashram0.mem[idx]);
`endif

    #0   RXD   = 1;
    #0   RESET = 0;
    #80  RESET = 0;
  #160 RESET = 1;
    #(tck*100000)
    UART_WRITE_BYTE(8'h38);
    #(tck*8000)

    UART_WRITE_BYTE(8'h2A);    // Operator *
    #(tck*8000)   

    UART_WRITE_BYTE(8'h39);
    #(tck*120000)

    UART_WRITE_BYTE(8'h38);
    #(tck*8000)

    UART_WRITE_BYTE(8'h2A);    // Operator *
    #(tck*8000)   

    UART_WRITE_BYTE(8'h37);
    #(tck*8000)

//    @(posedge CLK);
    #(tck*200000) $finish;
 end

endmodule

