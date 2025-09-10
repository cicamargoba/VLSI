`timescale 1ns / 1ps

module spiram(
    input wire CS,       // Chip Select (activo en bajo)
    input wire SCK,      // SPI Clock
    input wire SI,       // Serial Input (MOSI)
    output wire SO       // Serial Output (MISO)
);

    // Memoria RAM interna de 32 KB
    reg [7:0] mem [0:32767];
    integer i;
    initial begin
        for (i = 0; i < 32768; i = i + 1)
            mem[i] = 8'd0;
    end

    // Estados del SPI
    localparam IDLE  = 3'd0;
    localparam CMD   = 3'd1;
    localparam ADDR1 = 3'd2;
    localparam ADDR2 = 3'd3;
    localparam READ  = 3'd4;
    localparam WRITE = 3'd5;

    reg [2:0] state = IDLE;
    reg [7:0] shift_reg = 8'd0;
    reg [2:0] bit_cnt = 3'd0;
    reg [7:0] cmd = 8'd0;
    reg [14:0] addr = 15'd0;
    reg [7:0] data_out = 8'd0;
    reg so_reg = 1'b1;

    assign SO = (!CS) ? so_reg : 1'b1;

    always @(posedge SCK or posedge CS) begin
        if (CS) begin
            state <= IDLE;
            bit_cnt <= 3'd0;
            shift_reg <= 8'd0;
            cmd <= 8'd0;
            addr <= 15'd0;
            data_out <= 8'd0;
            so_reg <= 1'b1;
        end else begin
            shift_reg <= {shift_reg[6:0], SI};
            bit_cnt <= bit_cnt + 3'd1;
            if (bit_cnt == 3'd7) begin
                case (state)
                    IDLE: begin
                        cmd <= {shift_reg[6:0], SI};
                        if ({shift_reg[6:0], SI} == 8'h03) // READ
                            state <= ADDR1;
                        else if ({shift_reg[6:0], SI} == 8'h02) // WRITE
                            state <= ADDR1;
                        else
                            state <= IDLE;
                    end
                    ADDR1: begin
                        addr[14:8] <= {shift_reg[6:0], SI};
                        state <= ADDR2;
                    end
                    ADDR2: begin
                        addr[7:0] <= {shift_reg[6:0], SI};
                        if (cmd == 8'h03)
                            state <= READ;
                        else if (cmd == 8'h02)
                            state <= WRITE;
                        else
                            state <= IDLE;
                    end
                    WRITE: begin
                        mem[addr] <= {shift_reg[6:0], SI};
                        addr <= addr + 15'd1;
                    end
                    default: state <= IDLE;
                endcase
                bit_cnt <= 3'd0;
            end
        end
    end

    // Salida en flanco de bajada de SCK
    always @(negedge SCK) begin
        if (!CS) begin
            if (state == READ) begin
                if (bit_cnt == 3'd0)
                    data_out <= mem[addr];
                so_reg <= data_out[7 - bit_cnt];
                if (bit_cnt == 3'd7)
                    addr <= addr + 15'd1;
            end else begin
                so_reg <= 1'b0;
            end
        end else begin
            so_reg <= 1'b1;
        end
    end

endmodule
