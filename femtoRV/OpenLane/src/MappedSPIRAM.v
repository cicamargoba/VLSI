 `define SPI_FLASH_DUMMY_CLOCKS 0

module MappedSPIRAM( 
    input wire 	        clk,           // system clock
    input wire          reset,         // system reset
    input wire 	        rd,         // read strobe
    input wire          wr,         // write strobe		
    input wire [19:0]   word_address,  // address of the word to be read

    input wire [31:0]   wdata,         // data to be written
    output wire [31:0]  rdata,         // data read
    output reg          rbusy,        // asserted if busy receiving data
    output reg          wbusy,         // asserted if busy writing data		    

		             // SPI flash pins
    output reg         CLK,  // clock
    output reg         CS_N, // chip select negated (active low)		
    output wire        MOSI, // master out slave in (data to be sent to flash)
    input  wire        MISO  // master in slave out (data received from flash)
);


 parameter START      = 2'b00;
 parameter WAIT_INST  = 2'b01;
 parameter SEND       = 2'b10;
 parameter RECEIVE    = 2'b11;

 parameter divisor    = 2;


 
 reg [1:0] state;
 reg clk_div;



   reg [5:0]  snd_bitcount;
   reg [31:0] cmd_addr;
   reg [5:0]  rcv_bitcount;
   reg [31:0] rcv_data;

   reg [5:0]  div_counter;


always @(negedge clk) begin
    if (!reset) begin
      clk_div     <= 0;
      div_counter <= 0;
    end
    else begin
      if (div_counter >= divisor) begin
        clk_div      <= 1;
        div_counter  <= 0;
      end
      else begin
        clk_div      <= 0;
        div_counter  <=  div_counter + 1;
      end
    end
end

always @(negedge clk) begin
    if (!reset) begin
      CLK    <= 0;
    end
    else begin
      if ( (div_counter == divisor/2) | ( div_counter == divisor )   ) begin
        CLK  <= ~CLK;
      end
    end
end




always @(negedge clk) begin
    if (!reset) begin
      state    <= START;
      rbusy    <= 1'b0;
      wbusy    <= 1'b0;
      rcv_data <= 0;
      CS_N     <= 1; 
      cmd_addr <= 0;
    end else begin
    case(state)
      START:begin
        CS_N         <= 1'b1;
        rbusy        <= 1'b0;
        wbusy        <= 1'b0;
        snd_bitcount <= 6'd0;
        rcv_bitcount <= 6'd0;
        state        <= WAIT_INST;
      end

      WAIT_INST: begin
        if (rd) begin
          CS_N         <= 1'b0;
          rbusy        <= 1'b1;
          wbusy        <= 1'b0;
          snd_bitcount <= 6'd24;
          rcv_bitcount <= 6'd32;
          cmd_addr     <= {8'h03,word_address[15:0],8'h00};
          state        <= SEND;
        end
        else if (wr) begin
          CS_N         <= 1'b0;
          rbusy        <= 1'b0;
          wbusy        <= 1'b1;
          snd_bitcount <= 6'd32;
          rcv_bitcount <= 6'd0;
          cmd_addr     <= {8'h02,word_address[15:0],wdata[7:0]};
          state        <= SEND;
        end
        else begin
          state        <= WAIT_INST;
        end
      end

      SEND: begin
        if(CLK) begin
            if(snd_bitcount == 1) begin
                state        <= RECEIVE;
            end
            else begin
            snd_bitcount <= snd_bitcount - 6'd1;
            cmd_addr     <= {cmd_addr[30:0],1'b1};
            state        <= SEND;
            end
        end
      end

      RECEIVE: begin
        if(CLK) begin
          if(rcv_bitcount == 0) begin
            state         <= START;
          end
          else begin
            rcv_bitcount <= rcv_bitcount - 6'd1;
            rcv_data     <= {rcv_data[30:0],MISO};
          state         <= RECEIVE;  
          end
        end
      end

       default: 
         state <= START;
    
    endcase
  end
end


assign  MOSI  = cmd_addr[31];

//   assign  CLK   = !CS_N && !clk; // CLK needs to be inverted (sample on posedge, shift of negedge) 
                                  // and needs to be disabled when not sending/receiving (&& !CS_N).

   // since least significant bytes are read first, we need to swizzle...
   assign rdata = {rcv_data[7:0],rcv_data[15:8],rcv_data[23:16],rcv_data[31:24]};


endmodule
