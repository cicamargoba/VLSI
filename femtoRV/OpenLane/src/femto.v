module tt_um_femto(
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // Register the reset on the negative edge of clock for safety.
  // This also allows the option of async reset in the design, which might be preferable in some cases
  /* verilator lint_off SYNCASYNCNET */
  reg rst_reg_n;
  /* verilator lint_on SYNCASYNCNET */
  always @(negedge clk) rst_reg_n <= rst_n;


endmodule

module femto (
   input 	     clk,    // system clock 
   input 	     resetn, // reset button

   output        spi_mosi,
   input         spi_miso,
   output        spi_cs_n,
   output        spi_clk,

   output      spi_clk_ram,      // SPI RAM Clock
   output      spi_cs_n_ram,     // SPI RAM Chip Select, Active Low
   input       spi_miso_ram,     // SPI RAM Master In Slave Out
   output      spi_mosi_ram,     // SPI RAM Master Out Slave In

   output        wire LEDS,   // system LEDs
   input 	     RXD,    // UART receive
   output 	     TXD     // UART transmit
);
   wire [31:0] mem_address;
   reg  [31:0] mem_rdata;
   wire mem_rstrb;
   wire [31:0] mem_wdata;
   wire [3:0]  mem_wmask;

   wire mapped_spi_flash_rbusy;

   FemtoRV32 CPU(
      .clk(clk),
      .reset(resetn),		 
      .mem_addr(mem_address),
      .mem_rdata(mem_rdata),
      .mem_rstrb(mem_rstrb),
      .mem_wdata(mem_wdata),
      .mem_wmask(mem_wmask),
      .mem_rbusy(mapped_spi_flash_rbusy | spi_ram_rbusy),
      .mem_wbusy(spi_ram_wbusy)
   );
   wire [31:0] RAM_rdata;
   wire  wr = |mem_wmask;
   wire  rd = mem_rstrb; 

/*
   bram RAM(
      .clk(clk),
      .mem_addr(mem_address[6:2]),
      .mem_rdata(dpram_dout),
      .cs(cs[6]),
      .rd(rd),
      .wr(wr),
      .mem_wdata(mem_wdata)
      //.mem_wmask( { 4{ cs[6] } } & mem_wmask )
   );

*/


   wire spi_ram_rbusy;
   wire spi_ram_wbusy;
   MappedSPIRAM mapped_spi_ram(
      .clk(clk),
      .reset(resetn),
      .word_address(mem_address[21:2]),
      .wdata(mem_wdata),
      .rd(cs[6] & rd),
      .wr(cs[6] & wr),
      .rbusy(spi_ram_rbusy),
      .wbusy(spi_ram_wbusy),
      .CLK(spi_clk_ram),
      .CS_N(spi_cs_n_ram),
      .MISO(spi_miso_ram),
      .MOSI(spi_mosi_ram),
      .rdata(dpram_dout)
   );
//   wire [31:0] spi_ram_dout;



   //wire [31:0] mapped_spi_flash_rdata;

   
   MappedSPIFlash mapped_spi_flash(
      .clk(clk),
      .reset(resetn),
      .rstrb(cs[0] & rd),
      .word_address(mem_address[21:2]),
      .rdata(RAM_rdata),
      .rbusy(mapped_spi_flash_rbusy),
      .CLK(spi_clk),
      .CS_N(spi_cs_n),
      .MISO(spi_miso),
      .MOSI(spi_mosi)
      
   );




   wire [31:0] uart_dout;
//   wire [31:0] gpio_dout;
//   wire [31:0] mult_dout;
//   wire [31:0] div_dout;
//   wire [31:0] bin2bcd_dout;
   wire [31:0] dpram_dout;


  peripheral_uart #(
     .clk_freq(27000000),    // 27000000 for gowin
     .baud(115200)            // 57600 for gowin
   ) per_uart(
     .clk(clk), 
     .rst(!resetn), 
     .d_in(mem_wdata[7:0]), 
     .cs(cs[5]), 
     .addr(mem_address[4:0]), 
     .wr(wr), 
     .d_out(uart_dout), 
     .uart_tx(TXD), 
     .uart_rx(RXD), 
     .ledout(LEDS)
   ); 

/*
	peripheral_mult mult1 (
		.clk(clk), 
		.reset(!resetn), 
		.d_in(mem_wdata[15:0]), 
		.cs(cs[3]), 
		.addr(mem_address[4:0]), 
		.rd(rd), 
		.wr(wr), 
		.d_out(mult_dout) 
	);


   peripheral_dpram dpram_p0( 
      .clk(clk),
      .reset(!resetn),
      .d_in(mem_wdata[15:0]),
      .cs(cs[6]),
      .addr(mem_address[15:0]),
      .rd(rd),
      .wr(wr),
      .d_out(dpram_dout)
  );
*/

  // ============== Chip_Select (Addres decoder) ======================== 
  // se hace con los 8 bits mas significativos de mem_addr
  // Se asigna el rango de la memoria de programa 0x00000000 - 0x003FFFFF
  // ====================================================================
  reg [6:0]cs;  // CHIP-SELECT
  always @*
  begin
      case (mem_address[31:16])	// direcciones - chip_select
        16'h0000: cs= 7'b0000001; 	//RAM
        16'h0040: cs= 7'b0100000; 	//uart
//        16'h0041: cs= 7'b0010000;	//gpio
//        16'h0042: cs= 7'b0001000;	//mult
//        16'h0043: cs= 7'b0000100;	//div
//        16'h0044: cs= 7'b0000010;	//bin_to_bcd
          16'h0001: cs= 7'b1000000;   //dpRAM
        default: cs= 7'b0000001;
      endcase
  end
  // ============== MUX ========================  // se encarga de lecturas del RV32
  always @*
  begin
      case (cs)
        7'b1000000: mem_rdata = dpram_dout;
        7'b0100000: mem_rdata = uart_dout;
//        7'b0010000: mem_rdata = gpio_dout;
//        7'b0001000: mem_rdata = mult_dout;
//        7'b0000100: mem_rdata = div_dout;
//        7'b0000010: mem_rdata = bin2bcd_dout;
        7'b0000001: mem_rdata = RAM_rdata;
        default:    mem_rdata = 32'h00000000;
      endcase
  end
 // ============== MUX ========================  // 

`ifdef BENCH
   always @(posedge clk) begin
      if(cs[5] & wr ) begin
	 $write("%c", mem_wdata[7:0] );
	 $fflush(32'h8000_0001);
      end
   end
`endif


endmodule
