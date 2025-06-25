 `define SPI_FLASH_DUMMY_CLOCKS 0

module MappedSPIFlash( 
    input wire 	       clk,          // system clock
    input wire           reset,
    input wire 	       rstrb,        // read strobe		
    input wire [19:0]  word_address, // address of the word to be read

    output wire [31:0] rdata,        // data read
    output reg        rbusy,        // asserted if busy receiving data			    

		             // SPI flash pins
    output reg        CLK,  // clock
    output reg         CS_N, // chip select negated (active low)		
    output wire        MOSI, // master out slave in (data to be sent to flash)
    input  wire        MISO  // master in slave out (data received from flash)
);

   reg [5:0]  snd_bitcount;
   reg [31:0] cmd_addr;
   reg [5:0]  rcv_bitcount;
   reg [31:0] rcv_data;

   
   assign  MOSI  = cmd_addr[31];
//   assign  CLK   = !CS_N && !clk; // CLK needs to be inverted (sample on posedge, shift of negedge) 
                                  // and needs to be disabled when not sending/receiving (&& !CS_N).

   // since least significant bytes are read first, we need to swizzle...
   assign rdata = {rcv_data[7:0],rcv_data[15:8],rcv_data[23:16],rcv_data[31:24]};
   reg       sending;
   reg       receiving;
   reg       busy ;


   always @(*) begin
      if (snd_bitcount != 0) begin
          sending = 1;
          rbusy   = 1;
      end
      else begin
          sending = 0;
          rbusy   = 0;
      end
      if (rcv_bitcount != 0) begin
          receiving = 1;
          rbusy = 1;
      end
      else begin
          receiving = 0;
          rbusy   = 1;
      end
      busy = sending | receiving;

   end

    reg [31:0] counter;
    reg clk_div;
    always @(posedge clk ) begin

      if(reset) begin
        counter <= 0;
        CLK <= 0;
        clk_div <= 0;
      end
      else begin
         if (counter ==2 ) begin
            CLK     <= !CS_N && ~CLK;
            clk_div <= 1;
            counter <= counter + 1;
         end
         if (counter == 4) begin               
               counter <= 0;
               CLK     <= !CS_N && ~CLK;
               clk_div <= 1;
         end

         else begin
            clk_div <= 0;
            counter <= counter + 1;
         end
      end
    end

   always @(negedge clk) begin
      if(reset) begin
        CS_N <= 1'b1;
        snd_bitcount <= 6'd0;
        rcv_bitcount <= 6'd0;
        rcv_data <= 0;
        cmd_addr <= 0;
      end
      else begin
         if(clk_div) begin
            if(rstrb) begin
               CS_N <= 1'b0;
               cmd_addr <= {8'h03, 2'b00,word_address[19:0], 2'b00};
               snd_bitcount <= 6'd32;
            end else begin
               if(sending) begin
                  if(snd_bitcount == 1) begin
                     rcv_bitcount <= 6'd32;
                  end
                  snd_bitcount <= snd_bitcount - 6'd1;
                  cmd_addr <= {cmd_addr[30:0],1'b1};
               end
               if(receiving) begin
                  rcv_bitcount <= rcv_bitcount - 6'd1;
                  rcv_data <= {rcv_data[30:0],MISO};
               end
               if(!busy) begin
                  CS_N <= 1'b1;
               end
            end
         end
      end
   end
endmodule
