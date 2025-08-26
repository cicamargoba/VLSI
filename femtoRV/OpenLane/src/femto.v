module femto (
   input       clk,              // System Clock 
   input 	   resetn,           // Reset Button

   output      spi_clk_flash,    // SPI Flash Clock
   output      spi_cs_n_flash,   // SPI Flash Chip Select, Active Low
   input       spi_miso_flash,   // SPI Flash Master In Slave Out
   output      spi_mosi_flash,   // SPI Flash Master Out Slave In
   
   output      spi_clk_ram,      // SPI RAM Clock
   output      spi_cs_n_ram,     // SPI RAM Chip Select, Active Low
   input       spi_miso_ram,     // SPI RAM Master In Slave Out
   output      spi_mosi_ram,     // SPI RAM Master Out Slave In

   input 	   RXD,              // UART receive
   output 	   TXD,               // UART transmit
   output wire LEDS             // System LEDs
);

   (* keep *) wire [31:0] mem_address;
   reg  [31:0] mem_rdata;
   wire        mem_rstrb;
   (* keep *) wire [31:0] mem_wdata;
   wire [3:0]  mem_wmask;

   wire rd = mem_rstrb;
   wire wr = |mem_wmask;


   FemtoRV32 CPU(
      .clk(clk),
      .reset(resetn),		 
      .mem_addr(mem_address),
      .mem_rdata(mem_rdata),
      .mem_rstrb(mem_rstrb),
      .mem_wdata(mem_wdata),
      .mem_wmask(mem_wmask),
      .mem_rbusy(spi_flash_rbusy | spi_ram_rbusy),
      .mem_wbusy(spi_ram_wbusy)
   );


   wire spi_flash_rbusy;
   MappedSPIFlash mapped_spi_flash(
      .clk(clk),
      .reset(resetn),
      .word_address(mem_address[21:2]),
      .rstrb(cs[0] & rd),
      .rbusy(spi_flash_rbusy),
      .CLK(spi_clk_flash),
      .CS_N(spi_cs_n_flash),
      .MISO(spi_miso_flash),
      .MOSI(spi_mosi_flash),
      .rdata(spi_flash_dout)
   );
   wire [31:0] spi_flash_dout;


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
      .rdata(spi_ram_dout)
   );
   wire [31:0] spi_ram_dout;
   

   peripheral_uart #(
      .clk_freq(25000000),
      .baud(115200)
   )  per_uart(
         .clk(clk), 
         .rst(!resetn),
         .addr(mem_address[4:0]),
         .d_in(mem_wdata), 
         .cs(cs[5]), 
         .rd(rd), 
         .wr(wr),
         .uart_rx(RXD),
         .uart_tx(TXD), 
         .ledout(LEDS),
         .d_out(uart_dout)
   );
   wire [31:0] uart_dout; 


	peripheral_mult mult1 (
      .clk(clk), 
      .reset(!resetn),
      .addr(mem_address[4:0]),
      .d_in(mem_wdata[15:0]), 
      .cs(cs[3]), 
      .rd(rd), 
      .wr(wr), 
      .d_out(mult_dout)
	);
   wire [31:0] mult_dout;


   // ============== Chip_Select (Addres decoder) ======================== 
   // Se hace con los 8 bits mas significativos de mem_address
   // Se asigna el rango de la memoria de programa 0x00000000 - 0x003FFFFF
   // ====================================================================
   (* keep *) reg [6:0]cs;  // Chip Select
   always @*
   begin
      case (mem_address[31:16])	// Address - Chip Select
         16'h0000: cs= 7'b0000001;  // SPI Flash
         16'h0001: cs= 7'b1000000;  // SPI RAM
         
         16'h0040: cs= 7'b0100000; 	// UART
         16'h0042: cs= 7'b0001000;	// Multiplier
        
         default:  cs= 7'b0000001;	// No Address Match
      endcase
   end
   // ============== MUX ========================  // Se encarga de lecturas del RV32
   always @*
   begin
      case (cs)
         7'b0000001: mem_rdata = spi_flash_dout;   // SPI Flash
         7'b1000000: mem_rdata = spi_ram_dout;     // SPI RAM
         
         7'b0100000: mem_rdata = uart_dout;        // UART
         7'b0001000: mem_rdata = mult_dout;        // Multiplier
        
         default:    mem_rdata = 32'h66666666;     // No Chip Select
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
