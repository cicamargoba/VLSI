//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55
//%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%55
module bram (
   input             clk,
   input      [6:2] mem_addr,  // address to be read
   output reg [31:0] mem_rdata, // data read from memory
   input   	     cs, // goes high when processor wants to read
   input         rd,
   input         wr,
   input      [31:0] mem_wdata // data to be written
   //input      [3:0]  mem_wmask	// masks for writing the 4 bytes (1=write byte) 
);

   reg [31:0] MEM [0:31];    // Modificar .equ IO_HW_CONFIG_RAM, 8192  (2048 palabras de 32 bits = 2048 * 4 bytes) en libfemtorv/include/HardwareConfig_bits.inc 

   wire [4:0] word_addr = mem_addr[6:2];
   
   always @(posedge clk) begin
      if(cs & rd) begin
         mem_rdata <= MEM[word_addr[4:0]];
      end
      if(cs & wr) begin
         MEM[word_addr[4:0]] <= mem_wdata;
      end 
   end
endmodule

