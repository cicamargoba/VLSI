`timescale 1ns / 1ps
`define SIMULATION
module mult_32_TB;
   reg  clk;
   reg  rst;
   reg  reset;
   reg  start;
   reg  [15:0]A;
   reg  [15:0]B;
   wire [31:0] pp;
   wire done;

  mult_32 uut ( 
    .clk(clk),  
    .rst(rst), 
    .init(start) ,  
    .done(done) ,
    .  \A[0] (A[0]), 
    .  \A[1] (A[1]),  
    .  \A[2] (A[2]), 
    .  \A[3] (A[3]),   
    .  \A[4] (A[4]),  
    .  \A[5] (A[5]),   
    .  \A[6] (A[6]), 
    .  \A[7] (A[7]),  
    .  \A[8] (A[8]), 
    .  \A[9] (A[9]), 
    .  \A[10] (A[10]), 
    .  \A[11] (A[11]), 
    .  \A[12] (A[12]),  
    .  \A[13] (A[13]), 
    .  \A[14] (A[14]), 
    .  \A[15] (A[15]), 
    .  \B[0] (B[0]),  
    .  \B[1] (B[1]),  
    .  \B[2] (B[2]), 
    .  \B[3] (B[3]),  
    .  \B[4] (B[4]),  
    .  \B[5] (B[5]),  
    .  \B[6] (B[6]), 
    .  \B[7] (B[7]), 
    .  \B[8] (B[8]),  
    .  \B[9] (B[9]),  
    .  \B[10] (B[10]),  
    .  \B[11] (B[11]), 
    .  \B[12] (B[12]), 
    .  \B[13] (B[13]),  
    .  \B[14] (B[14]),  
    .  \B[15] (B[15]), 
    .  \pp[0] (pp[0]) ,
    .  \pp[1] (pp[1]), 
    .  \pp[2] (pp[2]), 
    .  \pp[3] (pp[3]), 
    .  \pp[4] (pp[4]), 
    .  \pp[5] (pp[5]), 
    .  \pp[6] (pp[6]),  
    .  \pp[7] (pp[7]), 
    .  \pp[8] (pp[8]),
    .  \pp[9] (pp[9]), 
    .  \pp[10] (pp[10]), 
    .  \pp[11] (pp[11]), 
    .  \pp[12] (pp[12]), 
    .  \pp[13] (pp[13]), 
    .  \pp[14] (pp[14]), 
    .  \pp[15] (pp[15]), 
    .  \pp[16] (pp[16]), 
    .  \pp[17] (pp[17]), 
    .  \pp[18] (pp[18]), 
    .  \pp[19] (pp[19]), 
    .  \pp[20] (pp[20]),
    .  \pp[21] (pp[21]), 
    .  \pp[22] (pp[22]),
    .  \pp[23] (pp[23]),  
    .  \pp[24] (pp[24]), 
    .  \pp[25] (pp[25]), 
    .  \pp[26] (pp[26]), 
    .  \pp[27] (pp[27]), 
    .  \pp[28] (pp[28]), 
    .  \pp[29] (pp[29]),  
    .  \pp[30] (pp[30]), 
    .  \pp[31] (pp[31])
    );
    

   parameter PERIOD          = 20;
   parameter real DUTY_CYCLE = 0.5;
   parameter OFFSET          = 0;
   reg [20:0] i;
	event reset_trigger;
	event reset_done_trigger;
	initial begin 
	  forever begin 
	   @ (reset_trigger);
		@ (negedge clk);
		rst = 1;
		@ (negedge clk);
		rst = 0;
		-> reset_done_trigger;
		end
	end
   initial begin  // Initialize s
      clk = 0; reset = 1; start = 0; A = 16'h00F7; B = 16'h007F;
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
        #10 -> reset_trigger;
        @ (reset_done_trigger);
        @ (posedge clk);
        start = 0;
        @ (posedge clk);
        start = 1;
       for(i=0; i<2; i=i+1) begin
         @ (posedge clk);
       end
          start = 0;
       for(i=0; i<17; i=i+1) begin
         @ (posedge clk);
       end
   end	 
   initial begin: TEST_CASE
     $dumpfile("mult_32_TB.vcd");
     $dumpvars(-1, uut);
     #((PERIOD*DUTY_CYCLE)*120) $finish;
   end
endmodule

