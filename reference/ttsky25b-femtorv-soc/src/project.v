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
  assign uio_out = {qspi_ram_b_select, qspi_ram_a_select, qspi_data_out[3:2], 
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
  wire [31:0] data_from_read;

  wire is_mem = addr[27:25] == 3'b000;
  reg [7:0] gpio_out;

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
    .data_from_read(data_from_read),

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
    .mem_rdata((is_mem || instr_ready) ? data_from_read : {16'd0, gpio_out, ui_in}),
    .mem_read_n(read_n),
    .mem_ready(is_mem ? data_ready : 1'b1)
  );

  always @(posedge clk) begin
    if (!rst_reg_n) gpio_out <= 0;
    if (!is_mem) gpio_out <= data_to_write[7:0];
  end

  assign uo_out = gpio_out;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in[7:6], uio_in[3], uio_in[0], 1'b0};

endmodule
