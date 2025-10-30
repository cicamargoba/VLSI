/*
 * Copyright (c) 2025 Michael Bell
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_rebelmike_femtorv (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Address to peripheral map
    localparam PERI_NONE = 4'hF;
    localparam PERI_GPIO_OUT = 4'h0;
    localparam PERI_GPIO_IN = 4'h1;
    localparam PERI_GPIO_OUT_SEL = 4'h3;
    localparam PERI_UART = 4'h4;
    localparam PERI_UART_STATUS = 4'h5;
    localparam PERI_DEBUG_UART = 4'h6;
    localparam PERI_DEBUG_UART_STATUS = 4'h7;
    localparam PERI_SPI = 4'h8;
    localparam PERI_SPI_STATUS = 4'h9;
    localparam PERI_PWM = 4'hA;
    localparam PERI_GAME_1 = 4'hD;
    localparam PERI_GAME_2 = 4'hE;

    // Register the reset on the negative edge of clock for safety.
    // This also allows the option of async reset in the design, which might be preferable in some cases
    /* verilator lint_off SYNCASYNCNET */
    reg rst_reg_n;
    /* verilator lint_on SYNCASYNCNET */
    always @(negedge clk) rst_reg_n <= rst_n;

    // Bidirs are used for SPI interface
    wire [3:0] qspi_data_in = {uio_in[5:4], uio_in[2:1]};
    wire [3:0] qspi_data_out;
    wire [3:0] qspi_data_oe;
    wire       qspi_clk_out;
    wire       qspi_flash_select;
    wire       qspi_ram_a_select;
    wire       qspi_ram_b_select;
    wire       uio_out7;
    assign uio_out = {uio_out7, qspi_ram_a_select, qspi_data_out[3:2], 
                      qspi_clk_out, qspi_data_out[1:0], qspi_flash_select};
    assign uio_oe = rst_n ? {2'b11, qspi_data_oe[3:2], 1'b1, qspi_data_oe[1:0], 1'b1} : 8'h00;

    wire [23:1] instr_addr;
    wire        instr_jump;
    wire        instr_ready;

    wire [27:0] addr;
    wire  [1:0] write_n;
    wire  [1:0] read_n;
    wire [31:0] data_to_write;

    wire        data_ready;
    reg [31:0] data_from_read;
    wire [31:0] data_from_mem;
    wire is_mem = addr[27:25] == 3'b000;

    // Peripheral IOs on ui_in and uo_out
    wire       spi_miso   = ui_in[2];
    wire       game_latch = ui_in[4];
    wire       game_data  = ui_in[6];
    wire       uart_rxd   = ui_in[7];

`ifdef SIM
    wire       game_clk   = ui_in[5];
`elsif SCL_sky130_fd_sc_hd
    (* keep *) wire game_clk;
/* verilator lint_off PINMISSING */
    (* keep_hierarchy *) sky130_fd_sc_hd__clkbuf_8 game_clk_buf(.X(game_clk), .A(ui_in[5]));
/* verilator lint_on PINMISSING */
`elsif SCL_sg13g2_stdcell
    (* keep *) wire game_clk;
/* verilator lint_off PINMISSING */
    (* keep_hierarchy *) sg13g2_buf_8 game_clk_buf(.X(game_clk), .A(ui_in[5]));
/* verilator lint_on PINMISSING */
`else
    (* keep *) wire game_clk;
/* verilator lint_off PINMISSING */
    (* keep_hierarchy *) gf180mcu_fd_sc_mcu7t5v0__clkbuf_8 game_clk_buf(.X(game_clk), .A(ui_in[5]));
/* verilator lint_on PINMISSING */
`endif

    wire       spi_cs;
    wire       spi_sck;
    wire       spi_mosi;
    wire       spi_dc;
    wire       uart_txd;
    wire       uart_rts;
    wire       debug_uart_txd;
    reg  [8:0] gpio_out_sel;
    reg  [7:0] gpio_out;

    reg [3:0] connect_peripheral;

    // UART
    wire uart_tx_busy;
    wire uart_rx_valid;
    wire [7:0] uart_rx_data;
    wire uart_tx_start = write_n != 2'b11 && connect_peripheral == PERI_UART;

    // Debug UART - runs fast to reduce the width of the count necessary for the divider!
    wire debug_uart_tx_busy;
    wire debug_uart_tx_start = write_n != 2'b11 && connect_peripheral == PERI_DEBUG_UART;

    // SPI
    wire spi_start = write_n != 2'b11 && connect_peripheral == PERI_SPI;
    wire [7:0] spi_data;
    wire spi_busy;

    // PWM
    wire pwm_out;

    // GAME
    wire [11:0] controller1_data;
    wire [11:0] controller2_data;

    tinyqv_mem_ctrl i_mem_ctrl(
      .clk(clk),
      .rstn(rst_reg_n),

      .instr_addr(instr_addr),
      .instr_jump(instr_jump),
      .instr_fetch_stall(1'b0),

      .instr_ready(instr_ready),

      .data_addr(addr[24:0]),
      .data_write_n(is_mem ? write_n : 2'b11),
      .data_read_n(is_mem ? read_n : 2'b11),
      .data_to_write(data_to_write),

      .data_continue(1'b0),

      .data_ready(data_ready),
      .data_from_read(data_from_mem),

      .spi_data_in(qspi_data_in),
      .spi_data_out(qspi_data_out),
      .spi_data_oe(qspi_data_oe),
      .spi_clk_out(qspi_clk_out),
      .spi_flash_select(qspi_flash_select),
      .spi_ram_a_select(qspi_ram_a_select),
      .spi_ram_b_select(qspi_ram_b_select)
    );

    FemtoRV32 i_femtorv(
      .clk(clk),
      .resetn(rst_reg_n),

      .instr_addr(instr_addr),
      .instr_jump(instr_jump),
      .instr_ready(instr_ready),    

      .mem_addr(addr),
      .mem_wdata(data_to_write),
      .mem_write_n(write_n),
      .mem_rdata((instr_ready || is_mem) ? data_from_mem : data_from_read),
      .mem_read_n(read_n),
      .mem_ready(is_mem ? data_ready : 1'b1)
    );

    assign uo_out[0] = gpio_out_sel[0] ? gpio_out[0] : uart_txd;
    assign uo_out[1] = gpio_out_sel[1] ? gpio_out[1] : uart_rts;
    assign uo_out[2] = gpio_out_sel[2] ? gpio_out[2] : spi_dc;
    assign uo_out[3] = gpio_out_sel[3] ? gpio_out[3] : spi_mosi;
    assign uo_out[4] = gpio_out_sel[4] ? gpio_out[4] : spi_cs;
    assign uo_out[5] = gpio_out_sel[5] ? gpio_out[5] : spi_sck;
    assign uo_out[6] = gpio_out_sel[6] ? gpio_out[6] : debug_uart_txd;
    assign uo_out[7] = gpio_out_sel[7] ? gpio_out[7] : pwm_out;
    assign uio_out7 = gpio_out_sel[8] ? pwm_out : qspi_ram_b_select;

    always @(*) begin
        if ({addr[27:7], addr[1:0]} == 23'h400000) 
            connect_peripheral = addr[5:2];
        else
            connect_peripheral = PERI_NONE;
    end

    // Read data
    always @(*) begin
        case (connect_peripheral)
            PERI_GPIO_OUT:    data_from_read = {24'h0, uo_out};
            PERI_GPIO_IN:     data_from_read = {24'h0, ui_in};
            PERI_GPIO_OUT_SEL:data_from_read = {23'h0, gpio_out_sel};
            PERI_UART:        data_from_read = {24'h0, uart_rx_data};
            PERI_UART_STATUS: data_from_read = {30'h0, uart_rx_valid, uart_tx_busy};
            PERI_DEBUG_UART_STATUS: data_from_read = {31'h0, debug_uart_tx_busy};
            PERI_SPI:         data_from_read = {24'h0, spi_data};
            PERI_SPI_STATUS:  data_from_read = {31'h0, spi_busy};
            PERI_GAME_1:      data_from_read = {20'h0,controller1_data};
            PERI_GAME_2:      data_from_read = {20'h0,controller2_data};
            default:          data_from_read = 0;
        endcase
    end

    // GPIO Out
    always @(posedge clk) begin
        if (!rst_reg_n) begin
            gpio_out_sel <= 0;
            gpio_out <= 0;
        end
        if (write_n != 2'b11) begin
            if (connect_peripheral == PERI_GPIO_OUT) gpio_out <= data_to_write[7:0];
            if (connect_peripheral == PERI_GPIO_OUT_SEL) gpio_out_sel <= data_to_write[8:0];
        end
    end

    uart_tx #(.CLK_HZ(50_000_000), .BIT_RATE(115_200)) i_uart_tx(
        .clk(clk),
        .resetn(rst_reg_n),
        .uart_txd(uart_txd),
        .uart_tx_en(uart_tx_start),
        .uart_tx_data(data_to_write[7:0]),
        .uart_tx_busy(uart_tx_busy) 
    );

    uart_rx #(.CLK_HZ(50_000_000), .BIT_RATE(115_200)) i_uart_rx(
        .clk(clk),
        .resetn(rst_reg_n),
        .uart_rxd(uart_rxd),
        .uart_rts(uart_rts),
        .uart_rx_read(connect_peripheral == PERI_UART),
        .uart_rx_valid(uart_rx_valid),
        .uart_rx_data(uart_rx_data) 
    );

    uart_tx #(.CLK_HZ(50_000_000), .BIT_RATE(4_000_000)) i_debug_uart_tx(
        .clk(clk),
        .resetn(rst_reg_n),
        .uart_txd(debug_uart_txd),
        .uart_tx_en(debug_uart_tx_start),
        .uart_tx_data(data_to_write[7:0]),
        .uart_tx_busy(debug_uart_tx_busy) 
    );

    spi_ctrl i_spi(
        .clk(clk),
        .rstn(rst_reg_n),

        .spi_miso(spi_miso),
        .spi_select(spi_cs),
        .spi_clk_out(spi_sck),
        .spi_mosi(spi_mosi),
        .spi_dc(spi_dc),

        .dc_in(data_to_write[9]),
        .end_txn(data_to_write[8]),
        .data_in(data_to_write[7:0]),
        .start(spi_start),
        .data_out(spi_data),
        .busy(spi_busy),

        .set_config(connect_peripheral == PERI_SPI_STATUS && write_n != 2'b11),
        .divider_in(data_to_write[3:0]),
        .read_latency_in(data_to_write[8])
    );

    pwm_ctrl i_pwm(
        .clk(clk),
        .rstn(rst_reg_n),

        .pwm(pwm_out),

        .level(data_to_write[7:0]),
        .set_level(connect_peripheral == PERI_PWM && write_n != 2'b11)
    );

    tt_game i_game (
        .clk(clk),
        .rstn(rst_reg_n),

        .game_latch(game_latch),
        .game_clk(game_clk),
        .game_data(game_data),

        .controller_1(controller1_data),
        .controller_2(controller2_data)
    );

    // List all unused inputs to prevent warnings
    wire _unused = &{ena, uio_in[7:6], uio_in[3], uio_in[0], 1'b0};

endmodule
