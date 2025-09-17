`timescale 1us / 1ns
`define SIMULATION
module mult_TB;
   reg  clk;
   reg  reset;
   reg  init;
   reg  [3:0] op_A;
   reg  [3:0] op_B;
   wire [7
   :0] result;
   wire done;

   Mult_4 uut (
      .clk(clk), 
      .rst(reset), 
      .init(init), 
      .A(op_A), 
      .B(op_B), 
      .pp(result), 
      .done(done)
   );

   parameter PERIOD = 20;
   initial begin  // Initialize Inputs
      clk = 0; reset = 0; init = 0; op_A = 8'h0A; op_B = 8'h0A;
   end
   // clk generation
   initial         clk <= 0;
   always #(PERIOD/2) clk <= ~clk;

   initial begin // Reset the system, Start the image capture process
        // Reset 
        @ (negedge clk);
	     reset = 1;
	     @ (negedge clk);
	     reset = 0;
        #(PERIOD*4)
        init = 0;
        @ (posedge clk);
        init = 1;
        #(PERIOD*2)
        init = 0;
        #(PERIOD*50);
   end
	 

   initial begin: TEST_CASE
     $dumpfile("Mult_4_TB.vcd");
     $dumpvars(-1, mult_TB);
     #(PERIOD*50) $finish;
   end

endmodule

