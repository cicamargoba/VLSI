#SOC_flash_TB.uut.clk
#SOC_flash_TB.uut.resetn
#SOC_flash_TB.uut.spi_miso
#SOC_flash_TB.uut.spi_mosi
#SOC_flash_TB.uut.spi_cs_n
#SOC_flash_TB.uut.spi_clk

from vcdvcd import VCDVCD

vcd_file = "SOC_flash_TB.vcd" #Nombre del vcd generado de GTKWave 
signal_name = "SOC_flash_TB.uut.spi_miso"  # ← nombre de la señal
output_file = "spi_miso.pwl" #Nombre del archivo pwl

vcd = VCDVCD(vcd_file, signals=[signal_name], store_tvs=True)
tvs = vcd[signal_name].tv

volt_map = {'0': 0.0, '1': 1.8}

with open(output_file, 'w') as f:
    for time, val in tvs:
        if val in volt_map:
            f.write(f"{time} {volt_map[val]}\n")


#Vclk clk 0 PWL FILE="spi_miso.pwl"