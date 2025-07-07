 `define SPI_FLASH_DUMMY_CLOCKS 0

module MappedSPIFlash( 
    input wire 	       clk,          // system clock
    input wire         reset,
    input wire 	       rstrb,        // read strobe		
    input wire [19:0]  word_address, // address of the word to be read

    output wire [31:0] rdata,        // data read
    output reg        rbusy,        // asserted if busy receiving data			    

		             // SPI flash pins
    output reg         CLK,  // clock
    output reg         CS_N, // chip select negated (active low)		
    output wire        MOSI, // master out slave in (data to be sent to flash)
    input  wire        MISO  // master in slave out (data received from flash)
);


 parameter START      = 3'b000;
 parameter WAIT_STRB  = 3'b001;
 parameter SEND       = 3'b010;
 parameter RECEIVE    = 3'b011;
 //parameter END        = 3'b100;

 parameter divisor    = 2;


 
 reg [2:0] state;
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
      state     <= START;
      rbusy    <= 1'b0;
      rcv_data <= 0;
      CS_N     <= 1; 
      cmd_addr <= 0;
    end else begin
    case(state)
      START:begin
        CS_N         <= 1'b1;
        rbusy        <= 1'b0;
        snd_bitcount <= 6'd0;
        rcv_bitcount <= 6'd0;
        state        <= WAIT_STRB;

      end

      WAIT_STRB: begin
        if (rstrb) begin
          CS_N         <= 1'b1;
          rbusy        <= 1'b1;
          snd_bitcount <= 6'd32;
          cmd_addr     <= {8'h03, 2'b00,word_address[19:0], 2'b00};
          CS_N         <= 1'b0;
          state         <= SEND;

        end
        else begin
          state         <= WAIT_STRB;
        end
      end

      SEND: begin
        if(clk_div) begin
            if(snd_bitcount == 1) begin
                rcv_bitcount <= 6'd32;
                state         <= RECEIVE;
            end
            else begin
            snd_bitcount <= snd_bitcount - 6'd1;
            cmd_addr     <= {cmd_addr[30:0],1'b1};
            state        <= SEND;
            end
        end
      end
    


      RECEIVE: begin
        if(clk_div) begin
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
