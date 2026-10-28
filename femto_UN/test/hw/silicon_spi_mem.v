// SPDX-License-Identifier: Apache-2.0
// silicon_spi_mem.v -- Memoria SPI "consciente del silicio" (flash + RAM) para FPGA/CPLD.
//
// Sustituye a la flash y a la RAM SPI de la placa del chip femto_UN (commit f15fccd).
// Conoce los defectos del silicio y los compensa del lado de la memoria:
//   * Cuenta flancos de BAJADA de SCK desde que CS_N baja (no pulsos de subida). Así no le afecta que el
//     chip pierda el primer bit del comando (DEF-F1/DEF-S1): comando y dirección son siempre los 32 bits
//     de sh[31:0] (el bit perdido siempre es un 0 y entra como 0 al registro de desplazamiento).
//   * Flash: el primer bit de dato se presenta en la caída nº 33 (equivale a 1 ciclo "dummy"): el controlador
//     de flash del chip captura entonces los 32 bits exactos (corrige DEF-F2).
//   * RAM: el controlador captura 31 bits (DEF-S2): D31 (caída 32) lo ignora el chip; se presenta D30 en la caída 33;
//     el firmware debe tratar las palabras de RAM como de 31 bits.
//   * La flash cuenta como "tick" la caída de SCK coincidente con la bajada de CS_N; la RAM no (la RAM tiene
//     un estado extra WAIT_SCLK en su controlador).
// Debe usar el MISMO reloj `clk` que el chip: las salidas del chip cambian en el flanco de bajada, el emulador
// las muestrea en el de subida (medio ciclo después) y su MISO llega antes del siguiente muestreo del chip.
module silicon_spi_mem #(
    parameter FLASH_AW = 14,          // 2**14 = 16 KiB de flash
    parameter RAM_AW   = 16           // 64 KiB de RAM (el chip direcciona 16 bits)
) (
    input  wire clk,
    input  wire f_sck, f_csn, f_mosi, output reg f_miso,
    input  wire r_sck, r_csn, r_mosi, output reg r_miso
);
    // ------------------------------------------------------------------ FLASH (sólo lectura, 0x03)
    reg [7:0] fmem [0:(1<<FLASH_AW)-1];
    reg        f_sck_q = 1'b0, f_cs_q = 1'b1;
    reg [6:0]  f_nf;
    reg [31:0] f_sh;
    reg [23:0] f_base;
    reg        f_ok;
    reg [7:0]  f_byte;

    wire f_act    = ~f_csn;
    wire f_start  = f_cs_q & ~f_csn;                       // CS_N acaba de bajar
    wire f_rise   = ~f_sck_q & f_sck & f_act;
    wire f_fall   = f_sck_q & ~f_sck & f_act;
    wire [6:0]  f_nf_cur = f_start ? 7'd0 : f_nf;
    wire [31:0] f_sh_cur = f_start ? 32'd0 : f_sh;
    wire [6:0]  f_nf_new = f_nf_cur + {6'd0, f_fall};      // la caída coincidente con CS_N SÍ cuenta
    wire [6:0]  f_k      = f_nf_new - 7'd33;               // índice del bit de dato que toca presentar
    // dirección del byte que se necesitará en la PRÓXIMA caída (índice f_nf+1-33), para que f_byte esté listo a tiempo
    wire [6:0]  f_k_next = f_nf - 7'd32;
    wire [FLASH_AW-1:0] f_raddr = f_base[FLASH_AW-1:0] + {{(FLASH_AW-3){1'b0}}, f_k_next[6:3]};

    always @(posedge clk) begin
        f_sck_q <= f_sck;
        f_cs_q  <= f_csn;
        f_byte  <= fmem[f_raddr];                          // lectura síncrona (BRAM)
        if (f_csn) begin
            f_nf <= 0; f_sh <= 0; f_ok <= 0; f_miso <= 1'b0;
        end else begin
            f_nf <= f_nf_new;
            f_sh <= f_rise ? {f_sh_cur[30:0], f_mosi} : f_sh_cur;
            if (f_fall && f_nf_new == 7'd32) begin          // dirección completa (en cualquier alineación)
                f_base <= f_sh_cur[23:0];
                f_ok   <= (f_sh_cur[31:24] == 8'h03);
            end
            if (f_fall && f_nf_new >= 7'd33 && f_ok)
                f_miso <= f_byte[3'd7 - f_k[2:0]];
        end
    end

    // ------------------------------------------------------------------ RAM (lectura 0x03 / escritura 0x02)
    reg [7:0] rmem [0:(1<<RAM_AW)-1];
    reg        r_sck_q = 1'b0, r_cs_q = 1'b1;
    reg [6:0]  r_nf;
    reg [31:0] r_sh;
    reg [23:0] r_base;
    reg [1:0]  r_mode;                                      // 0 nada, 1 lectura, 2 escritura
    reg [6:0]  r_wcnt;
    reg [7:0]  r_wsh;
    reg [7:0]  r_byte;

    wire r_act   = ~r_csn;
    wire r_start = r_cs_q & ~r_csn;
    wire r_rise  = ~r_sck_q & r_sck & r_act;
    wire r_fall  = r_sck_q & ~r_sck & r_act;
    wire r_fall_cnt = r_fall & ~r_start;                   // aquí la caída coincidente NO cuenta
    wire [6:0]  r_nf_cur = r_start ? 7'd0 : r_nf;
    wire [31:0] r_sh_cur = r_start ? 32'd0 : r_sh;
    wire [6:0]  r_nf_new = r_nf_cur + {6'd0, r_fall_cnt};
    wire [6:0]  r_k      = r_nf_new - 7'd32;
    wire [6:0]  r_k_next = r_nf - 7'd31;                    // índice del bit de la próxima caída (r_nf+1-32)
    wire [RAM_AW-1:0] r_raddr = r_base[RAM_AW-1:0] + {{(RAM_AW-3){1'b0}}, r_k_next[6:3]};

    always @(posedge clk) begin
        r_sck_q <= r_sck;
        r_cs_q  <= r_csn;
        r_byte  <= rmem[r_raddr];
        if (r_csn) begin
            r_nf <= 0; r_sh <= 0; r_mode <= 0; r_miso <= 1'b0; r_wcnt <= 0; r_wsh <= 0;
        end else begin
            r_nf <= r_nf_new;
            r_sh <= (r_rise && r_mode == 0) ? {r_sh_cur[30:0], r_mosi} : r_sh_cur;
            if (r_fall_cnt && r_nf_new == 7'd32) begin
                r_base <= r_sh_cur[23:0];
                r_mode <= (r_sh_cur[31:24] == 8'h03) ? 2'd1 : (r_sh_cur[31:24] == 8'h02) ? 2'd2 : 2'd0;
            end
            if (r_fall_cnt && r_nf_new >= 7'd33 && r_mode == 2'd1)
                r_miso <= r_byte[3'd7 - r_k[2:0]];
            if (r_rise && r_mode == 2'd2) begin             // datos de escritura: MSB primero
                r_wsh   <= {r_wsh[6:0], r_mosi};
                r_wcnt  <= r_wcnt + 7'd1;
                if (r_wcnt[2:0] == 3'd7)
                    rmem[r_base[RAM_AW-1:0] + {{(RAM_AW-3){1'b0}}, r_wcnt[6:3]}] <= {r_wsh[6:0], r_mosi};
            end
        end
    end
endmodule
