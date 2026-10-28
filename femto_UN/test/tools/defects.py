# SPDX-License-Identifier: Apache-2.0
"""Catálogo de defectos del silicio f15fccd y su asociación con pruebas."""

DEFECTS = {
    "DEF-F1": dict(mod="MappedSPIFlash", sev="Crítico",
                   title="El primer bit del comando SPI se pierde en 1 de cada 3 fases del divisor",
                   cause="SCK corre libre; CS_N baja en cualquier fase y MOSI se desplaza antes del primer flanco de subida: "
                         "la flash ve 0x06 en vez de 0x03. Como cada instrucción tarda 195 ciclos (múltiplo de 3) la fase "
                         "es constante: en la fase mala TODAS las lecturas fallan."),
    "DEF-F2": dict(mod="MappedSPIFlash", sev="Crítico",
                   title="Los datos de lectura llegan desplazados 1 bit (D31 se pierde, el LSB es el MSB de la palabra siguiente)",
                   cause="El maestro muestrea 1 ciclo después del flanco de bajada de SCK, cuando el esclavo ya cambió al bit siguiente."),
    "DEF-R1": dict(mod="SoC / reset", sev="Alto",
                   title="La primera lectura tras reset se pierde: la instrucción de la dirección 0 nunca se ejecuta",
                   cause="La CPU emite rstrb en su primer ciclo, pero el controlador de flash sigue en START (necesita 1 ciclo)."),
    "DEF-S1": dict(mod="MappedSPIRAM", sev="Crítico",
                   title="Se pierde el primer bit del comando SPI en 4 de cada 11 fases (lecturas y escrituras)",
                   cause="Igual que DEF-F1 con divisor=10 (fases 6..9 del contador)."),
    "DEF-S2": dict(mod="MappedSPIRAM", sev="Alto",
                   title="La lectura captura 31 bits: el bit 31 de rdata es el LSB de la lectura anterior",
                   cause="rcv_bitcount termina un tick antes y rcv_data no se limpia."),
    "DEF-S3": dict(mod="MappedSPIRAM / SoC", sev="Alto",
                   title="SB/SH/LB/LH/LBU/LHU sobre SPI RAM son incorrectos",
                   cause="El controlador ignora mem_wmask (escribe 4 copias del byte) y envía la dirección de bytes sin alinear "
                         "(la CPU espera la palabra alineada)."),
    "DEF-C1": dict(mod="SPI (ambos)", sev="Medio",
                   title="CS_N y SCK cambian en el mismo instante en algunas fases (setup 0 ns)",
                   cause="Falta de sincronía entre el inicio de la transacción y el divisor de reloj."),
    "DEF-U1": dict(mod="uart", sev="Alto",
                   title="Baud real = f_clk/208: sólo es 115200 con f_clk ≈ 23.96 MHz (a 27 MHz es 129.8 kbaud, +12.7 %)",
                   cause="divisor = freq/baud/16 = 14 (truncado) y el contador recarga divisor-1 -> periodo de 13 ciclos."),
    "DEF-U2": dict(mod="uart", sev="Medio",
                   title="El receptor evalúa el bit de parada un bit tarde: no detecta stop erróneo y corrompe tramas consecutivas",
                   cause="rx_bitcount==10 en lugar de ==9."),
    "INFO-A1": dict(mod="femtorv32_quark", sev="Info",
                    title="ADDR_WIDTH=24: AUIPC y direcciones load/store se truncan a 24 bits (alias cada 16 MiB)", cause="Parámetro de diseño."),
    "INFO-A2": dict(mod="femtorv32_quark", sev="Info",
                    title="FENCE no soportado; ECALL/EBREAK/SYSTEM = RDCYCLE; sólo accesos alineados", cause="Diseño minimalista."),
    "INFO-A3": dict(mod="SoC", sev="Info",
                    title="Direcciones sin mapear hacen alias a la flash; registros y 'cycles' arrancan con valores indeterminados",
                    cause="decodificador por defecto y ausencia de reset en el banco de registros."),
}

# prueba (sufijo del nombre) -> lista de defectos que explican su fallo en el silicio
TEST_DEFECTS = {
    # unitarias SPI RAM
    "unit_spiram": {
        "test_read_protocol_and_data": ["DEF-S2"], "test_write_then_read_roundtrip": ["DEF-S1"],
        "test_read_all_divider_phases": ["DEF-S1", "DEF-S2"], "test_write_all_divider_phases": ["DEF-S1"],
        "test_spi_signal_timing": ["DEF-C1"], "test_random_mixed_traffic": ["DEF-S1", "DEF-S2"],
        "test_miso_output_delay_tolerance": ["DEF-S2"], "test_adjacent_words_do_not_overlap": ["DEF-S1", "DEF-S2"],
        "test_write_protocol_and_data": ["DEF-S1"], "test_reset_during_transaction": ["DEF-S2"],
    },
    "unit_spiflash": {
        "test_read_protocol_and_data": ["DEF-F2"], "test_byte_order_little_endian": ["DEF-F2"],
        "test_sequential_reads_distinct_words": ["DEF-F2"], "test_command_and_address_integrity_all_phases": ["DEF-F1"],
        "test_data_integrity_all_phases": ["DEF-F1", "DEF-F2"], "test_address_range": ["DEF-F2"],
        "test_spi_signal_timing": ["DEF-C1"], "test_miso_output_delay_tolerance": ["DEF-F2"],
        "test_reset_during_transaction": ["DEF-F2"],
    },
    "unit_uart": {
        "test_tx_baud_rate_vs_spec": ["DEF-U1"], "test_rx_from_ideal_115200_sender": ["DEF-U1"],
        "test_rx_framing_error": ["DEF-U2"], "test_rx_back_to_back_frames": ["DEF-U2"],
    },
    "integration": {
        "test_i00_first_instruction_after_reset_is_executed": ["DEF-R1"],
        "test_i05_cpu_spiram_full_32bit_words": ["DEF-S2"], "test_i06_cpu_spiram_byte_halfword_access": ["DEF-S3"],
    },
    "functional": {"test_f10_ram_subword_store_load": ["DEF-S3"]},
    "e2e": {"test_e06_isa_selftest": ["DEF-S3"]},
    "acceptance": {
        "test_req02_isa_selftest_all_groups_pass": ["DEF-S3"], "test_req03_spiram_32bit_data_integrity": ["DEF-S2"],
        "test_req05b_uart_tx_baud_at_27mhz": ["DEF-U1"], "test_req06b_uart_rx_back_to_back": ["DEF-U2"],
        "test_req06c_uart_rx_from_pc_27mhz": ["DEF-U1"],
        "test_req08_commercial_spi_memories": ["DEF-F1", "DEF-F2"],
    },
}
LEVELS = [("unit_quark", "Unit", "FemtoRV32 Quark"), ("unit_spiram", "Unit", "MappedSPIRAM"),
          ("unit_spiflash", "Unit", "MappedSPIFlash"), ("unit_uart", "Unit", "UART"),
          ("integration", "Integration", "SoC"), ("functional", "Functional", "SoC"),
          ("e2e", "End-to-End", "Chip (pines)"), ("acceptance", "Acceptance", "Chip (requisitos)"),
          ("hw_emulator", "HW co-sim", "Chip + emulador RTL")]
