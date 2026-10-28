`define SPI_FLASH_DUMMY_CLOCKS 0

module MappedSPIRAM(
    input wire          clk,
    input wire          reset,
    input wire          rd,
    input wire          wr,
    input wire [15:0]   word_address,
    input wire [31:0]   wdata,
    output wire [31:0]  rdata,
    output reg          rbusy,
    output reg          wbusy,
    output reg          CLK,
    output reg          CS_N,
    output wire         MOSI,
    input wire          MISO
);

parameter START      = 3'b000;
parameter WAIT_INST  = 3'b001;
parameter SEND       = 3'b010;
parameter RECEIVE    = 3'b011;
parameter WAIT_SCLK  = 3'b100;

parameter divisor = 10;

reg edge_CLK;
reg [2:0] state;
reg [8:0] snd_bitcount;
reg [63:0] cmd_addr;
reg [5:0] rcv_bitcount;
reg [31:0] rcv_data;
reg [5:0] div_counter;

reg clk_sample;
reg clk_shift;

always @(negedge clk) begin
    if (!reset) begin
        clk_sample  <= 0;
        clk_shift   <= 0;
        CLK         <= 0;
        edge_CLK    <= 0;
        div_counter <= 0;
    end
    else begin
        if (CS_N == 1'b0) begin
            if (div_counter == (divisor / 2)) begin
                clk_sample  <= 1;
                clk_shift   <= 0;
                CLK         <= 1;
                edge_CLK    <= 1;
                div_counter <= div_counter + 1;
            end
            else if (div_counter >= divisor) begin
                clk_sample  <= 0;
                clk_shift   <= 1;
                CLK         <= 0;
                edge_CLK    <= 1;
                div_counter <= 0;
            end
            else begin
                clk_sample  <= 0;
                clk_shift   <= 0;
                edge_CLK    <= 0;
                div_counter <= div_counter + 1;
            end
        end
        else begin
            clk_sample  <= 0;
            clk_shift   <= 0;
            CLK         <= 0;
            edge_CLK    <= 0;
            div_counter <= 0;
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
    end
    else begin
        case (state)

            START: begin
                CS_N         <= 1'b1;
                rbusy        <= 1'b0;
                snd_bitcount <= 6'd0;
                rcv_bitcount <= 6'd0;
                state        <= WAIT_INST;
                wbusy        <= 1'b0;
            end

            WAIT_INST: begin
                state <= WAIT_INST;

                if (rd) begin
                    CS_N         <= 1'b0;
                    rbusy        <= 1'b1;
                    snd_bitcount <= 8'd32;
                    cmd_addr     <= {8'h03, 8'h00, word_address[15:0], 32'd0};
                    state        <= WAIT_SCLK;
                    rcv_bitcount <= 6'd32;
                    wbusy        <= 1'b0;
                end

                if (wr) begin
                    CS_N         <= 1'b0;
                    rbusy        <= 1'b0;
                    wbusy        <= 1'b1;
                    snd_bitcount <= 8'd64;
                    rcv_bitcount <= 6'd0;
                    cmd_addr     <= {8'h02, 8'h00, word_address[15:0], wdata[31:0]};
                    state        <= WAIT_SCLK;
                end
            end

            WAIT_SCLK: begin
                state <= SEND;
            end

            SEND: begin
                if (clk_shift) begin
                    if (snd_bitcount == 1) begin
                        snd_bitcount <= 0;
                        cmd_addr     <= {cmd_addr[62:0], 1'b1};

                        if (rcv_bitcount > 0)
                            state <= RECEIVE;
                        else
                            state <= START;
                    end
                    else begin
                        snd_bitcount <= snd_bitcount - 6'd1;
                        cmd_addr     <= {cmd_addr[62:0], 1'b1};
                        state        <= SEND;
                    end
                end
            end

            RECEIVE: begin
                if (clk_sample) begin
                    if (rcv_bitcount == 1) begin
                        rcv_bitcount <= 0;
                        rcv_data     <= {rcv_data[30:0], MISO};
                        state        <= START;
                    end
                    else begin
                        rcv_bitcount <= rcv_bitcount - 6'd1;
                        rcv_data     <= {rcv_data[30:0], MISO};
                        state        <= RECEIVE;
                    end
                end
            end

            default: begin
                state <= START;
            end

        endcase
    end
end

assign MOSI = cmd_addr[63];
assign rdata = rcv_data;

endmodule