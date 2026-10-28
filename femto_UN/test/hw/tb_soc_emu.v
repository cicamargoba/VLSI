// Banco de co-simulación: chip tt_um_femto (silicio f15fccd) + silicon_spi_mem (FPGA/CPLD en la placa)
module tb_soc_emu(input wire clk, input wire rst_n, input wire rxd, output wire txd, output wire led);
    wire [7:0] uo;
    wire f_miso, r_miso;
    wire [7:0] ui = {5'b0, rxd, r_miso, f_miso};
    tt_um_femto dut (.ui_in(ui), .uo_out(uo), .uio_in(8'b0), .uio_out(), .uio_oe(), .ena(1'b1), .clk(clk), .rst_n(rst_n));
    silicon_spi_mem emu (.clk(clk),
        .f_sck(uo[5]), .f_csn(uo[2]), .f_mosi(uo[0]), .f_miso(f_miso),
        .r_sck(uo[4]), .r_csn(uo[3]), .r_mosi(uo[1]), .r_miso(r_miso));
    assign txd = uo[7];
    assign led = uo[6];
endmodule
