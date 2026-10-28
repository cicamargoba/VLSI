// MappedSPIRAM_fixed.v  -- propuesta de corrección de MappedSPIRAM.v
// Mismos puertos y parámetro `divisor`; SCK = clk/(divisor+1) (igual que el original).
//
// Cambios respecto al original:
//  1. SCK ya no corre libre: sólo hay pulsos durante la transacción y parte siempre
//     de 0 con CS_N bajo => el primer bit del comando siempre tiene flanco de subida
//     (antes, según la fase del divisor, se perdía el primer bit: 4 de 11 fases).
//  2. MISO se muestrea en el flanco de SUBIDA de SCK (centro del bit) y se capturan
//     exactamente 32 bits (antes: 31, con el MSB heredado de la lectura anterior).
//  3. MOSI cambia en el flanco de bajada. Escritura = 64 pulsos exactos (antes 65).
//  4. CS_N sube medio periodo después del último flanco de subida (hold).
//
// `word_address` se sigue interpretando como dirección de BYTES (en el SoC: mem_address[15:0]).

module MappedSPIRAM(
    input  wire        clk,
    input  wire        reset,          // activo en bajo
    input  wire        rd,
    input  wire        wr,
    input  wire [15:0] word_address,
    input  wire [31:0] wdata,
    output wire [31:0] rdata,
    output reg         rbusy,
    output reg         wbusy,
    output reg         CLK,
    output reg         CS_N,
    output wire        MOSI,
    input  wire        MISO
);
    parameter divisor = 10;

    localparam IDLE = 1'b0, XFER = 1'b1;

    reg        state;
    reg [5:0]  div_counter;     // 0..divisor
    reg [6:0]  rise_count;      // flancos de subida ya emitidos (0..64)
    reg        is_read;
    reg [63:0] cmd_addr;
    reg [31:0] rcv_data;

    assign MOSI  = cmd_addr[63];
    assign rdata = rcv_data;

    always @(negedge clk) begin
        if (!reset) begin
            state       <= IDLE;
            CS_N        <= 1'b1;
            CLK         <= 1'b0;
            rbusy       <= 1'b0;
            wbusy       <= 1'b0;
            div_counter <= 6'd0;
            rise_count  <= 7'd0;
            is_read     <= 1'b0;
            cmd_addr    <= 64'd0;
            rcv_data    <= 32'd0;
        end else begin
            case (state)
            IDLE: begin
                CS_N  <= 1'b1;
                CLK   <= 1'b0;
                rbusy <= 1'b0;
                wbusy <= 1'b0;
                div_counter <= 6'd0;
                rise_count  <= 7'd0;
                if (rd) begin
                    CS_N     <= 1'b0;
                    rbusy    <= 1'b1;
                    is_read  <= 1'b1;
                    cmd_addr <= {8'h03, 8'h00, word_address, 32'd0};
                    state    <= XFER;
                end else if (wr) begin
                    CS_N     <= 1'b0;
                    wbusy    <= 1'b1;
                    is_read  <= 1'b0;
                    cmd_addr <= {8'h02, 8'h00, word_address, wdata};
                    state    <= XFER;
                end
            end

            XFER: begin
                div_counter <= (div_counter == divisor) ? 6'd0 : div_counter + 6'd1;

                if (div_counter == divisor/2) begin            // flanco de subida de SCK
                    CLK        <= 1'b1;
                    rise_count <= rise_count + 7'd1;
                    if (is_read && rise_count >= 7'd32)         // bits 33..64: datos de la RAM
                        rcv_data <= {rcv_data[30:0], MISO};
                end

                if (div_counter == divisor) begin               // flanco de bajada de SCK
                    CLK      <= 1'b0;
                    cmd_addr <= {cmd_addr[62:0], 1'b0};         // siguiente bit de MOSI
                    if (rise_count == 7'd64) begin              // terminó: soltar CS_N y busy
                        CS_N  <= 1'b1;
                        rbusy <= 1'b0;
                        wbusy <= 1'b0;
                        state <= IDLE;
                    end
                end
            end
            endcase
        end
    end
endmodule
