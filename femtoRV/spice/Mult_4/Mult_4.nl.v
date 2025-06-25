// This is the unpowered netlist.
module Mult_4 (clk,
    done,
    init,
    rst,
    A,
    B,
    pp);
 input clk;
 output done;
 input init;
 input rst;
 input [7:0] A;
 input [3:0] B;
 output [7:0] pp;

 wire _020_;
 wire _021_;
 wire _022_;
 wire _023_;
 wire _024_;
 wire _025_;
 wire _026_;
 wire _027_;
 wire _028_;
 wire _029_;
 wire _030_;
 wire _031_;
 wire _032_;
 wire _033_;
 wire _034_;
 wire _035_;
 wire _036_;
 wire _037_;
 wire _038_;
 wire _039_;
 wire _040_;
 wire _041_;
 wire _042_;
 wire _043_;
 wire _044_;
 wire _045_;
 wire _046_;
 wire _047_;
 wire _048_;
 wire _049_;
 wire _050_;
 wire _051_;
 wire _052_;
 wire _053_;
 wire _054_;
 wire _055_;
 wire _056_;
 wire _057_;
 wire _058_;
 wire _059_;
 wire _060_;
 wire _061_;
 wire _062_;
 wire _063_;
 wire _064_;
 wire _065_;
 wire _066_;
 wire _067_;
 wire _068_;
 wire _069_;
 wire _070_;
 wire _071_;
 wire _072_;
 wire _073_;
 wire _074_;
 wire _075_;
 wire _076_;
 wire _077_;
 wire _078_;
 wire _079_;
 wire _080_;
 wire _081_;
 wire _082_;
 wire _083_;
 wire _084_;
 wire _085_;
 wire _086_;
 wire _087_;
 wire _088_;
 wire _089_;
 wire _090_;
 wire _091_;
 wire _092_;
 wire _093_;
 wire _094_;
 wire _095_;
 wire _096_;
 wire _097_;
 wire _098_;
 wire _099_;
 wire _100_;
 wire _101_;
 wire _102_;
 wire _103_;
 wire _104_;
 wire _105_;
 wire _106_;
 wire _107_;
 wire _108_;
 wire _109_;
 wire _110_;
 wire _111_;
 wire _112_;
 wire _113_;
 wire _114_;
 wire _115_;
 wire _116_;
 wire _117_;
 wire _118_;
 wire _119_;
 wire _120_;
 wire _121_;
 wire _122_;
 wire _123_;
 wire _124_;
 wire _125_;
 wire _126_;
 wire _127_;
 wire _128_;
 wire _129_;
 wire _130_;
 wire _131_;
 wire _132_;
 wire _133_;
 wire _134_;
 wire _135_;
 wire _136_;
 wire _137_;
 wire _138_;
 wire \acc0.A[0] ;
 wire \acc0.A[1] ;
 wire \acc0.A[2] ;
 wire \acc0.A[3] ;
 wire \acc0.A[4] ;
 wire \acc0.A[5] ;
 wire \acc0.A[6] ;
 wire \acc0.A[7] ;
 wire clknet_0__113_;
 wire clknet_0__114_;
 wire clknet_0_clk;
 wire clknet_1_0__leaf__113_;
 wire clknet_1_0__leaf__114_;
 wire clknet_1_0__leaf_clk;
 wire clknet_1_1__leaf__113_;
 wire clknet_1_1__leaf__114_;
 wire clknet_1_1__leaf_clk;
 wire \comp0.B[0] ;
 wire \comp0.B[1] ;
 wire \comp0.B[2] ;
 wire \comp0.B[3] ;
 wire \control0.add ;
 wire \control0.count[0] ;
 wire \control0.count[1] ;
 wire \control0.count[2] ;
 wire \control0.count[3] ;
 wire \control0.reset ;
 wire \control0.sh ;
 wire \control0.state[0] ;
 wire \control0.state[1] ;
 wire \control0.state[2] ;
 wire net1;
 wire net10;
 wire net11;
 wire net12;
 wire net13;
 wire net14;
 wire net15;
 wire net16;
 wire net17;
 wire net18;
 wire net19;
 wire net2;
 wire net20;
 wire net21;
 wire net22;
 wire net23;
 wire net24;
 wire net25;
 wire net26;
 wire net27;
 wire net28;
 wire net29;
 wire net3;
 wire net30;
 wire net31;
 wire net32;
 wire net33;
 wire net34;
 wire net35;
 wire net36;
 wire net37;
 wire net38;
 wire net39;
 wire net4;
 wire net40;
 wire net41;
 wire net42;
 wire net43;
 wire net44;
 wire net45;
 wire net46;
 wire net47;
 wire net48;
 wire net49;
 wire net5;
 wire net50;
 wire net51;
 wire net52;
 wire net53;
 wire net54;
 wire net55;
 wire net56;
 wire net57;
 wire net58;
 wire net59;
 wire net6;
 wire net60;
 wire net61;
 wire net62;
 wire net63;
 wire net64;
 wire net65;
 wire net66;
 wire net67;
 wire net68;
 wire net69;
 wire net7;
 wire net70;
 wire net71;
 wire net72;
 wire net8;
 wire net9;

 sky130_fd_sc_hd__decap_3 FILLER_0_0_109 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_0_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_0_121 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_0_27 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_29 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_3 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_0_41 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_0_49 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_0_55 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_0_57 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_0_61 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_66 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_0_78 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_85 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_0_97 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_10_103 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_10_111 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_10_13 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_10_22 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_10_49 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_10_57 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_10_83 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_10_9 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_10_99 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_11_110 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_11_113 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_11_119 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_11_53 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_11_57 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_11_6 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_11_98 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_12_120 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_12_24 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_12_29 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_12_3 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_13_12 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_13_16 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_13_26 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_13_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_13_36 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_13_91 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_14_101 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_14_26 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_14_37 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_14_6 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_14_75 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_14_82 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_15_103 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_15_108 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_15_118 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_15_18 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_15_49 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_15_57 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_15_6 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_15_68 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_15_80 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_15_92 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_16_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_16_21 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_16_3 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_16_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_16_60 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_16_66 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_16_74 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_16_79 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_16_83 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_16_85 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_16_92 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_17_102 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_17_121 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_17_26 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_17_36 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_17_7 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_17_87 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_18_14 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_18_22 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_18_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_18_45 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_18_54 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_18_72 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_19_103 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_19_111 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_19_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_19_121 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_19_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_19_27 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_19_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_19_39 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_19_57 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_19_76 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_19_95 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_1_106 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_1_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_1_121 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_1_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_1_27 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_1_3 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_1_80 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_1_94 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_20_100 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_20_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_20_121 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_20_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_27 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_20_29 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_20_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_37 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_20_47 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_55 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_20_57 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_65 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_20_69 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_20_79 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_83 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_20_85 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_20_93 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_2_114 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_2_122 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_2_15 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_2_23 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_2_29 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_2_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_2_45 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_2_78 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_3_107 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_3_111 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_3_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_3_121 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_3_27 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_3_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_3_65 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_3_74 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_3_85 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_4_102 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_4_114 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_4_122 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_4_27 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_4_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_4_60 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_4_93 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_5_106 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_5_113 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_5_121 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_5_18 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_5_28 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_5_54 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_5_6 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_5_80 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_5_99 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_6_121 ();
 sky130_fd_sc_hd__decap_8 FILLER_0_6_15 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_6_23 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_6_3 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_6_40 ();
 sky130_ef_sc_hd__decap_12 FILLER_0_6_69 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_6_81 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_7_100 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_7_24 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_7_39 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_7_6 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_7_61 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_7_65 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_7_82 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_7_86 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_7_94 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_8_3 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_8_52 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_8_56 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_8_60 ();
 sky130_fd_sc_hd__decap_4 FILLER_0_9_12 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_9_53 ();
 sky130_fd_sc_hd__decap_6 FILLER_0_9_57 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_9_6 ();
 sky130_fd_sc_hd__fill_1 FILLER_0_9_63 ();
 sky130_fd_sc_hd__fill_2 FILLER_0_9_83 ();
 sky130_fd_sc_hd__decap_3 FILLER_0_9_93 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Left_21 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_0_Right_0 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Left_31 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_10_Right_10 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Left_32 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_11_Right_11 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Left_33 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_12_Right_12 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_13_Left_34 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_13_Right_13 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_14_Left_35 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_14_Right_14 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_15_Left_36 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_15_Right_15 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_16_Left_37 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_16_Right_16 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_17_Left_38 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_17_Right_17 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_18_Left_39 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_18_Right_18 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_19_Left_40 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_19_Right_19 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Left_22 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_1_Right_1 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_20_Left_41 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_20_Right_20 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Left_23 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_2_Right_2 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Left_24 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_3_Right_3 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Left_25 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_4_Right_4 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Left_26 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_5_Right_5 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Left_27 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_6_Right_6 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Left_28 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_7_Right_7 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Left_29 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_8_Right_8 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Left_30 ();
 sky130_fd_sc_hd__decap_3 PHY_EDGE_ROW_9_Right_9 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_42 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_43 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_44 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_0_45 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_10_64 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_10_65 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_66 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_11_67 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_68 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_12_69 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_13_70 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_13_71 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_14_72 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_14_73 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_15_74 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_15_75 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_16_76 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_16_77 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_17_78 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_17_79 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_18_80 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_18_81 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_19_82 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_19_83 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_1_46 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_1_47 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_20_84 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_20_85 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_20_86 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_20_87 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_48 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_2_49 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_3_50 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_3_51 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_52 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_4_53 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_5_54 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_5_55 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_56 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_6_57 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_7_58 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_7_59 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_60 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_8_61 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_9_62 ();
 sky130_fd_sc_hd__tapvpwrvgnd_1 TAP_TAPCELL_ROW_9_63 ();
 sky130_fd_sc_hd__inv_2 _139_ (.A(\control0.reset ),
    .Y(_137_));
 sky130_fd_sc_hd__and2_1 _140_ (.A(_137_),
    .B(\control0.sh ),
    .X(_138_));
 sky130_fd_sc_hd__clkbuf_2 _141_ (.A(_138_),
    .X(_051_));
 sky130_fd_sc_hd__buf_2 _142_ (.A(\control0.reset ),
    .X(_052_));
 sky130_fd_sc_hd__nor2_2 _143_ (.A(_052_),
    .B(\control0.sh ),
    .Y(_053_));
 sky130_fd_sc_hd__a22o_1 _144_ (.A1(_052_),
    .A2(net8),
    .B1(_053_),
    .B2(\acc0.A[7] ),
    .X(_054_));
 sky130_fd_sc_hd__a21o_1 _145_ (.A1(net52),
    .A2(_051_),
    .B1(_054_),
    .X(_039_));
 sky130_fd_sc_hd__buf_2 _146_ (.A(_137_),
    .X(_055_));
 sky130_fd_sc_hd__nand2_1 _147_ (.A(_137_),
    .B(\control0.sh ),
    .Y(_056_));
 sky130_fd_sc_hd__or2_1 _148_ (.A(\control0.reset ),
    .B(\control0.sh ),
    .X(_057_));
 sky130_fd_sc_hd__or2_1 _149_ (.A(\acc0.A[6] ),
    .B(_057_),
    .X(_058_));
 sky130_fd_sc_hd__o221a_1 _150_ (.A1(_055_),
    .A2(net7),
    .B1(_056_),
    .B2(net59),
    .C1(_058_),
    .X(_038_));
 sky130_fd_sc_hd__a22o_1 _151_ (.A1(_052_),
    .A2(net6),
    .B1(_053_),
    .B2(\acc0.A[5] ),
    .X(_059_));
 sky130_fd_sc_hd__a21o_1 _152_ (.A1(net54),
    .A2(_051_),
    .B1(_059_),
    .X(_037_));
 sky130_fd_sc_hd__a22o_1 _153_ (.A1(_052_),
    .A2(net5),
    .B1(_053_),
    .B2(net54),
    .X(_060_));
 sky130_fd_sc_hd__a21o_1 _154_ (.A1(net65),
    .A2(_051_),
    .B1(_060_),
    .X(_036_));
 sky130_fd_sc_hd__a22o_1 _155_ (.A1(_052_),
    .A2(net4),
    .B1(_053_),
    .B2(\acc0.A[3] ),
    .X(_061_));
 sky130_fd_sc_hd__a21o_1 _156_ (.A1(net57),
    .A2(_051_),
    .B1(_061_),
    .X(_035_));
 sky130_fd_sc_hd__a22o_1 _157_ (.A1(_052_),
    .A2(net3),
    .B1(_053_),
    .B2(net57),
    .X(_062_));
 sky130_fd_sc_hd__a21o_1 _158_ (.A1(net60),
    .A2(_051_),
    .B1(_062_),
    .X(_034_));
 sky130_fd_sc_hd__a22o_1 _159_ (.A1(_052_),
    .A2(net2),
    .B1(_053_),
    .B2(\acc0.A[1] ),
    .X(_063_));
 sky130_fd_sc_hd__a21o_1 _160_ (.A1(net56),
    .A2(_051_),
    .B1(_063_),
    .X(_033_));
 sky130_fd_sc_hd__a22o_1 _161_ (.A1(net1),
    .A2(_052_),
    .B1(_053_),
    .B2(net56),
    .X(_032_));
 sky130_fd_sc_hd__buf_2 _162_ (.A(\control0.add ),
    .X(_064_));
 sky130_fd_sc_hd__or2_1 _163_ (.A(\acc0.A[6] ),
    .B(net22),
    .X(_065_));
 sky130_fd_sc_hd__or2_1 _164_ (.A(\acc0.A[5] ),
    .B(net21),
    .X(_066_));
 sky130_fd_sc_hd__nand2_1 _165_ (.A(\acc0.A[4] ),
    .B(net20),
    .Y(_067_));
 sky130_fd_sc_hd__or2_1 _166_ (.A(\acc0.A[4] ),
    .B(net20),
    .X(_068_));
 sky130_fd_sc_hd__and2_1 _167_ (.A(_067_),
    .B(_068_),
    .X(_069_));
 sky130_fd_sc_hd__or2_1 _168_ (.A(\acc0.A[3] ),
    .B(net19),
    .X(_070_));
 sky130_fd_sc_hd__or2_1 _169_ (.A(\acc0.A[2] ),
    .B(net18),
    .X(_071_));
 sky130_fd_sc_hd__nand2_1 _170_ (.A(net56),
    .B(net16),
    .Y(_072_));
 sky130_fd_sc_hd__nor2_1 _171_ (.A(\acc0.A[1] ),
    .B(net17),
    .Y(_073_));
 sky130_fd_sc_hd__nand2_1 _172_ (.A(\acc0.A[1] ),
    .B(net17),
    .Y(_074_));
 sky130_fd_sc_hd__o21ai_1 _173_ (.A1(_072_),
    .A2(_073_),
    .B1(_074_),
    .Y(_075_));
 sky130_fd_sc_hd__and2_1 _174_ (.A(\acc0.A[2] ),
    .B(net18),
    .X(_076_));
 sky130_fd_sc_hd__a221o_1 _175_ (.A1(\acc0.A[3] ),
    .A2(net19),
    .B1(_071_),
    .B2(_075_),
    .C1(_076_),
    .X(_077_));
 sky130_fd_sc_hd__nand2_1 _176_ (.A(\acc0.A[5] ),
    .B(net21),
    .Y(_078_));
 sky130_fd_sc_hd__nand2_1 _177_ (.A(_067_),
    .B(_078_),
    .Y(_079_));
 sky130_fd_sc_hd__a31o_1 _178_ (.A1(_069_),
    .A2(_070_),
    .A3(_077_),
    .B1(_079_),
    .X(_080_));
 sky130_fd_sc_hd__nand2_1 _179_ (.A(\acc0.A[6] ),
    .B(net22),
    .Y(_081_));
 sky130_fd_sc_hd__inv_2 _180_ (.A(_081_),
    .Y(_082_));
 sky130_fd_sc_hd__a31oi_1 _181_ (.A1(_065_),
    .A2(_066_),
    .A3(_080_),
    .B1(_082_),
    .Y(_083_));
 sky130_fd_sc_hd__xor2_1 _182_ (.A(\acc0.A[7] ),
    .B(net23),
    .X(_084_));
 sky130_fd_sc_hd__nor2_1 _183_ (.A(_083_),
    .B(_084_),
    .Y(_085_));
 sky130_fd_sc_hd__inv_2 _184_ (.A(\control0.add ),
    .Y(_086_));
 sky130_fd_sc_hd__a21o_1 _185_ (.A1(_083_),
    .A2(_084_),
    .B1(_086_),
    .X(_087_));
 sky130_fd_sc_hd__o221a_1 _186_ (.A1(net67),
    .A2(_064_),
    .B1(_085_),
    .B2(_087_),
    .C1(_055_),
    .X(_031_));
 sky130_fd_sc_hd__nand2_1 _187_ (.A(_081_),
    .B(_065_),
    .Y(_088_));
 sky130_fd_sc_hd__nand2_1 _188_ (.A(_066_),
    .B(_080_),
    .Y(_089_));
 sky130_fd_sc_hd__xor2_1 _189_ (.A(_088_),
    .B(_089_),
    .X(_090_));
 sky130_fd_sc_hd__or2_1 _190_ (.A(_064_),
    .B(net72),
    .X(_091_));
 sky130_fd_sc_hd__o211a_1 _191_ (.A1(_086_),
    .A2(_090_),
    .B1(_091_),
    .C1(_055_),
    .X(_030_));
 sky130_fd_sc_hd__nand3_1 _192_ (.A(_069_),
    .B(_070_),
    .C(_077_),
    .Y(_092_));
 sky130_fd_sc_hd__a22oi_1 _193_ (.A1(_067_),
    .A2(_092_),
    .B1(_078_),
    .B2(_066_),
    .Y(_093_));
 sky130_fd_sc_hd__a41o_1 _194_ (.A1(_066_),
    .A2(_067_),
    .A3(_092_),
    .A4(_078_),
    .B1(_086_),
    .X(_094_));
 sky130_fd_sc_hd__o221a_1 _195_ (.A1(_064_),
    .A2(net64),
    .B1(_093_),
    .B2(_094_),
    .C1(_055_),
    .X(_029_));
 sky130_fd_sc_hd__a21o_1 _196_ (.A1(_070_),
    .A2(_077_),
    .B1(_069_),
    .X(_095_));
 sky130_fd_sc_hd__a21o_1 _197_ (.A1(_092_),
    .A2(_095_),
    .B1(_086_),
    .X(_096_));
 sky130_fd_sc_hd__o211a_1 _198_ (.A1(_064_),
    .A2(net58),
    .B1(_096_),
    .C1(_055_),
    .X(_028_));
 sky130_fd_sc_hd__nand2_1 _199_ (.A(\acc0.A[2] ),
    .B(net18),
    .Y(_097_));
 sky130_fd_sc_hd__and3_1 _200_ (.A(_097_),
    .B(_071_),
    .C(_075_),
    .X(_098_));
 sky130_fd_sc_hd__nand2_1 _201_ (.A(\acc0.A[3] ),
    .B(net19),
    .Y(_099_));
 sky130_fd_sc_hd__a2bb2o_1 _202_ (.A1_N(_076_),
    .A2_N(_098_),
    .B1(_099_),
    .B2(_070_),
    .X(_100_));
 sky130_fd_sc_hd__or2b_1 _203_ (.A(_077_),
    .B_N(_070_),
    .X(_101_));
 sky130_fd_sc_hd__nand3_1 _204_ (.A(_064_),
    .B(_100_),
    .C(_101_),
    .Y(_102_));
 sky130_fd_sc_hd__o211a_1 _205_ (.A1(_064_),
    .A2(net62),
    .B1(_102_),
    .C1(_055_),
    .X(_027_));
 sky130_fd_sc_hd__a21oi_1 _206_ (.A1(_097_),
    .A2(_071_),
    .B1(_075_),
    .Y(_103_));
 sky130_fd_sc_hd__o21ai_1 _207_ (.A1(_098_),
    .A2(_103_),
    .B1(_064_),
    .Y(_104_));
 sky130_fd_sc_hd__o211a_1 _208_ (.A1(_064_),
    .A2(net61),
    .B1(_104_),
    .C1(_055_),
    .X(_026_));
 sky130_fd_sc_hd__or2_1 _209_ (.A(\acc0.A[1] ),
    .B(net17),
    .X(_105_));
 sky130_fd_sc_hd__nand2_1 _210_ (.A(_074_),
    .B(_105_),
    .Y(_106_));
 sky130_fd_sc_hd__xor2_1 _211_ (.A(_072_),
    .B(_106_),
    .X(_107_));
 sky130_fd_sc_hd__or2_1 _212_ (.A(\control0.add ),
    .B(net17),
    .X(_108_));
 sky130_fd_sc_hd__o211a_1 _213_ (.A1(_086_),
    .A2(_107_),
    .B1(_108_),
    .C1(_055_),
    .X(_025_));
 sky130_fd_sc_hd__a21o_1 _214_ (.A1(net56),
    .A2(_064_),
    .B1(net69),
    .X(_109_));
 sky130_fd_sc_hd__o211a_1 _215_ (.A1(_086_),
    .A2(_072_),
    .B1(_109_),
    .C1(_055_),
    .X(_024_));
 sky130_fd_sc_hd__or2_1 _216_ (.A(net48),
    .B(_057_),
    .X(_110_));
 sky130_fd_sc_hd__o221a_1 _217_ (.A1(_055_),
    .A2(net11),
    .B1(_056_),
    .B2(net45),
    .C1(_110_),
    .X(_023_));
 sky130_fd_sc_hd__or2_1 _218_ (.A(\comp0.B[1] ),
    .B(_057_),
    .X(_111_));
 sky130_fd_sc_hd__o221a_1 _219_ (.A1(_137_),
    .A2(net10),
    .B1(_056_),
    .B2(net48),
    .C1(_111_),
    .X(_022_));
 sky130_fd_sc_hd__or2_1 _220_ (.A(\comp0.B[0] ),
    .B(_057_),
    .X(_112_));
 sky130_fd_sc_hd__o221a_1 _221_ (.A1(_137_),
    .A2(net9),
    .B1(_056_),
    .B2(net50),
    .C1(_112_),
    .X(_021_));
 sky130_fd_sc_hd__a22o_1 _222_ (.A1(_052_),
    .A2(net12),
    .B1(_053_),
    .B2(net45),
    .X(_020_));
 sky130_fd_sc_hd__buf_1 _223_ (.A(clknet_1_1__leaf_clk),
    .X(_113_));
 sky130_fd_sc_hd__inv_2 _224__1 (.A(clknet_1_0__leaf__113_),
    .Y(net24));
 sky130_fd_sc_hd__inv_2 _225__2 (.A(clknet_1_0__leaf__113_),
    .Y(net25));
 sky130_fd_sc_hd__inv_2 _226__3 (.A(clknet_1_0__leaf__113_),
    .Y(net26));
 sky130_fd_sc_hd__inv_2 _227__4 (.A(clknet_1_0__leaf__113_),
    .Y(net27));
 sky130_fd_sc_hd__inv_2 _228__5 (.A(clknet_1_1__leaf__113_),
    .Y(net28));
 sky130_fd_sc_hd__inv_2 _229__6 (.A(clknet_1_1__leaf__113_),
    .Y(net29));
 sky130_fd_sc_hd__inv_2 _230__7 (.A(clknet_1_1__leaf__113_),
    .Y(net30));
 sky130_fd_sc_hd__inv_2 _231__8 (.A(clknet_1_1__leaf__113_),
    .Y(net31));
 sky130_fd_sc_hd__inv_2 _232__9 (.A(clknet_1_1__leaf__113_),
    .Y(net32));
 sky130_fd_sc_hd__inv_2 _233__10 (.A(clknet_1_0__leaf__113_),
    .Y(net33));
 sky130_fd_sc_hd__buf_1 _234_ (.A(clknet_1_1__leaf_clk),
    .X(_114_));
 sky130_fd_sc_hd__inv_2 _235__11 (.A(clknet_1_0__leaf__114_),
    .Y(net34));
 sky130_fd_sc_hd__inv_2 _236__12 (.A(clknet_1_0__leaf__114_),
    .Y(net35));
 sky130_fd_sc_hd__inv_2 _237__13 (.A(clknet_1_1__leaf__114_),
    .Y(net36));
 sky130_fd_sc_hd__inv_2 _238__14 (.A(clknet_1_1__leaf__114_),
    .Y(net37));
 sky130_fd_sc_hd__inv_2 _239__15 (.A(clknet_1_1__leaf__114_),
    .Y(net38));
 sky130_fd_sc_hd__inv_2 _240__16 (.A(clknet_1_1__leaf__114_),
    .Y(net39));
 sky130_fd_sc_hd__inv_2 _241__17 (.A(clknet_1_1__leaf__114_),
    .Y(net40));
 sky130_fd_sc_hd__inv_2 _242__18 (.A(clknet_1_1__leaf__114_),
    .Y(net41));
 sky130_fd_sc_hd__inv_2 _243__19 (.A(clknet_1_0__leaf__114_),
    .Y(net42));
 sky130_fd_sc_hd__inv_2 _244__20 (.A(clknet_1_0__leaf__114_),
    .Y(net43));
 sky130_fd_sc_hd__inv_2 _245_ (.A(net71),
    .Y(_115_));
 sky130_fd_sc_hd__nor2_1 _246_ (.A(net14),
    .B(\control0.state[2] ),
    .Y(_116_));
 sky130_fd_sc_hd__mux2_1 _247_ (.A0(net13),
    .A1(\comp0.B[0] ),
    .S(\control0.state[0] ),
    .X(_117_));
 sky130_fd_sc_hd__and3b_1 _248_ (.A_N(\control0.state[0] ),
    .B(\control0.state[1] ),
    .C(_116_),
    .X(_118_));
 sky130_fd_sc_hd__or4_1 _249_ (.A(\comp0.B[2] ),
    .B(\comp0.B[1] ),
    .C(\comp0.B[0] ),
    .D(\comp0.B[3] ),
    .X(_119_));
 sky130_fd_sc_hd__a32o_1 _250_ (.A1(_115_),
    .A2(_116_),
    .A3(_117_),
    .B1(_118_),
    .B2(_119_),
    .X(_040_));
 sky130_fd_sc_hd__and2_1 _251_ (.A(\control0.state[0] ),
    .B(_116_),
    .X(_120_));
 sky130_fd_sc_hd__clkbuf_1 _252_ (.A(_120_),
    .X(_041_));
 sky130_fd_sc_hd__and3_1 _253_ (.A(\control0.count[0] ),
    .B(\control0.count[1] ),
    .C(\control0.count[2] ),
    .X(_121_));
 sky130_fd_sc_hd__xnor2_1 _254_ (.A(\control0.count[3] ),
    .B(_121_),
    .Y(_122_));
 sky130_fd_sc_hd__xor2_1 _255_ (.A(\control0.count[0] ),
    .B(\control0.count[1] ),
    .X(_123_));
 sky130_fd_sc_hd__a21oi_1 _256_ (.A1(\control0.count[0] ),
    .A2(\control0.count[1] ),
    .B1(\control0.count[2] ),
    .Y(_124_));
 sky130_fd_sc_hd__nor2_1 _257_ (.A(_121_),
    .B(_124_),
    .Y(_125_));
 sky130_fd_sc_hd__nor2_1 _258_ (.A(_123_),
    .B(_125_),
    .Y(_126_));
 sky130_fd_sc_hd__o21ai_1 _259_ (.A1(_122_),
    .A2(_126_),
    .B1(net68),
    .Y(_127_));
 sky130_fd_sc_hd__or4_1 _260_ (.A(\control0.state[0] ),
    .B(_115_),
    .C(\control0.state[2] ),
    .D(_119_),
    .X(_128_));
 sky130_fd_sc_hd__nor3_2 _261_ (.A(net14),
    .B(\control0.state[0] ),
    .C(\control0.state[1] ),
    .Y(_129_));
 sky130_fd_sc_hd__nor2_1 _262_ (.A(_116_),
    .B(_129_),
    .Y(_130_));
 sky130_fd_sc_hd__a21oi_1 _263_ (.A1(_127_),
    .A2(_128_),
    .B1(_130_),
    .Y(_042_));
 sky130_fd_sc_hd__and2_1 _264_ (.A(\control0.state[2] ),
    .B(_129_),
    .X(_131_));
 sky130_fd_sc_hd__or2_1 _265_ (.A(net14),
    .B(\control0.state[2] ),
    .X(_132_));
 sky130_fd_sc_hd__a21oi_1 _266_ (.A1(_052_),
    .A2(_132_),
    .B1(_129_),
    .Y(_133_));
 sky130_fd_sc_hd__nor2_1 _267_ (.A(_131_),
    .B(_133_),
    .Y(_043_));
 sky130_fd_sc_hd__a21o_1 _268_ (.A1(net66),
    .A2(_130_),
    .B1(_118_),
    .X(_044_));
 sky130_fd_sc_hd__a22o_1 _269_ (.A1(net71),
    .A2(_041_),
    .B1(_130_),
    .B2(_064_),
    .X(_045_));
 sky130_fd_sc_hd__o21a_1 _270_ (.A1(net44),
    .A2(_129_),
    .B1(_132_),
    .X(_046_));
 sky130_fd_sc_hd__or3_1 _271_ (.A(net14),
    .B(\control0.state[0] ),
    .C(\control0.state[1] ),
    .X(_134_));
 sky130_fd_sc_hd__mux2_1 _272_ (.A0(_131_),
    .A1(_134_),
    .S(\control0.count[0] ),
    .X(_135_));
 sky130_fd_sc_hd__clkbuf_1 _273_ (.A(_135_),
    .X(_047_));
 sky130_fd_sc_hd__a22o_1 _274_ (.A1(net63),
    .A2(_134_),
    .B1(_131_),
    .B2(_123_),
    .X(_048_));
 sky130_fd_sc_hd__a22o_1 _275_ (.A1(net46),
    .A2(_134_),
    .B1(_131_),
    .B2(_125_),
    .X(_049_));
 sky130_fd_sc_hd__inv_2 _276_ (.A(_122_),
    .Y(_136_));
 sky130_fd_sc_hd__a22o_1 _277_ (.A1(net47),
    .A2(_134_),
    .B1(_131_),
    .B2(_136_),
    .X(_050_));
 sky130_fd_sc_hd__dfxtp_1 _278_ (.CLK(net24),
    .D(_020_),
    .Q(\comp0.B[3] ));
 sky130_fd_sc_hd__dfxtp_1 _279_ (.CLK(net25),
    .D(net51),
    .Q(\comp0.B[0] ));
 sky130_fd_sc_hd__dfxtp_1 _280_ (.CLK(net26),
    .D(net49),
    .Q(\comp0.B[1] ));
 sky130_fd_sc_hd__dfxtp_1 _281_ (.CLK(net27),
    .D(_023_),
    .Q(\comp0.B[2] ));
 sky130_fd_sc_hd__dfxtp_1 _282_ (.CLK(net28),
    .D(net70),
    .Q(net16));
 sky130_fd_sc_hd__dfxtp_1 _283_ (.CLK(net29),
    .D(_025_),
    .Q(net17));
 sky130_fd_sc_hd__dfxtp_1 _284_ (.CLK(net30),
    .D(_026_),
    .Q(net18));
 sky130_fd_sc_hd__dfxtp_1 _285_ (.CLK(net31),
    .D(_027_),
    .Q(net19));
 sky130_fd_sc_hd__dfxtp_1 _286_ (.CLK(net32),
    .D(_028_),
    .Q(net20));
 sky130_fd_sc_hd__dfxtp_1 _287_ (.CLK(net33),
    .D(_029_),
    .Q(net21));
 sky130_fd_sc_hd__dfxtp_1 _288_ (.CLK(net34),
    .D(_030_),
    .Q(net22));
 sky130_fd_sc_hd__dfxtp_1 _289_ (.CLK(net35),
    .D(_031_),
    .Q(net23));
 sky130_fd_sc_hd__dfxtp_1 _290_ (.CLK(net36),
    .D(_032_),
    .Q(\acc0.A[0] ));
 sky130_fd_sc_hd__dfxtp_1 _291_ (.CLK(net37),
    .D(_033_),
    .Q(\acc0.A[1] ));
 sky130_fd_sc_hd__dfxtp_1 _292_ (.CLK(net38),
    .D(_034_),
    .Q(\acc0.A[2] ));
 sky130_fd_sc_hd__dfxtp_1 _293_ (.CLK(net39),
    .D(_035_),
    .Q(\acc0.A[3] ));
 sky130_fd_sc_hd__dfxtp_1 _294_ (.CLK(net40),
    .D(_036_),
    .Q(\acc0.A[4] ));
 sky130_fd_sc_hd__dfxtp_1 _295_ (.CLK(net41),
    .D(net55),
    .Q(\acc0.A[5] ));
 sky130_fd_sc_hd__dfxtp_1 _296_ (.CLK(net42),
    .D(_038_),
    .Q(\acc0.A[6] ));
 sky130_fd_sc_hd__dfxtp_1 _297_ (.CLK(net43),
    .D(net53),
    .Q(\acc0.A[7] ));
 sky130_fd_sc_hd__dfxtp_1 _298_ (.CLK(clknet_1_0__leaf_clk),
    .D(_040_),
    .Q(\control0.state[0] ));
 sky130_fd_sc_hd__dfxtp_1 _299_ (.CLK(clknet_1_0__leaf_clk),
    .D(_041_),
    .Q(\control0.state[1] ));
 sky130_fd_sc_hd__dfxtp_1 _300_ (.CLK(clknet_1_0__leaf_clk),
    .D(_042_),
    .Q(\control0.state[2] ));
 sky130_fd_sc_hd__dfxtp_1 _301_ (.CLK(clknet_1_1__leaf_clk),
    .D(_043_),
    .Q(\control0.reset ));
 sky130_fd_sc_hd__dfxtp_1 _302_ (.CLK(clknet_1_0__leaf_clk),
    .D(_044_),
    .Q(\control0.sh ));
 sky130_fd_sc_hd__dfxtp_1 _303_ (.CLK(clknet_1_1__leaf_clk),
    .D(_045_),
    .Q(\control0.add ));
 sky130_fd_sc_hd__dfxtp_1 _304_ (.CLK(clknet_1_0__leaf_clk),
    .D(_046_),
    .Q(net15));
 sky130_fd_sc_hd__dfxtp_1 _305_ (.CLK(clknet_1_0__leaf_clk),
    .D(_047_),
    .Q(\control0.count[0] ));
 sky130_fd_sc_hd__dfxtp_1 _306_ (.CLK(clknet_1_1__leaf_clk),
    .D(_048_),
    .Q(\control0.count[1] ));
 sky130_fd_sc_hd__dfxtp_1 _307_ (.CLK(clknet_1_1__leaf_clk),
    .D(_049_),
    .Q(\control0.count[2] ));
 sky130_fd_sc_hd__dfxtp_1 _308_ (.CLK(clknet_1_1__leaf_clk),
    .D(_050_),
    .Q(\control0.count[3] ));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0__113_ (.A(_113_),
    .X(clknet_0__113_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0__114_ (.A(_114_),
    .X(clknet_0__114_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_0_clk (.A(clk),
    .X(clknet_0_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f__113_ (.A(clknet_0__113_),
    .X(clknet_1_0__leaf__113_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f__114_ (.A(clknet_0__114_),
    .X(clknet_1_0__leaf__114_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_0__f_clk (.A(clknet_0_clk),
    .X(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f__113_ (.A(clknet_0__113_),
    .X(clknet_1_1__leaf__113_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f__114_ (.A(clknet_0__114_),
    .X(clknet_1_1__leaf__114_));
 sky130_fd_sc_hd__clkbuf_16 clkbuf_1_1__f_clk (.A(clknet_0_clk),
    .X(clknet_1_1__leaf_clk));
 sky130_fd_sc_hd__bufinv_8 clkload0 (.A(clknet_1_0__leaf_clk));
 sky130_fd_sc_hd__clkinvlp_4 clkload1 (.A(clknet_1_0__leaf__114_));
 sky130_fd_sc_hd__dlygate4sd3_1 hold1 (.A(net15),
    .X(net44));
 sky130_fd_sc_hd__dlygate4sd3_1 hold10 (.A(_039_),
    .X(net53));
 sky130_fd_sc_hd__dlygate4sd3_1 hold11 (.A(\acc0.A[4] ),
    .X(net54));
 sky130_fd_sc_hd__dlygate4sd3_1 hold12 (.A(_037_),
    .X(net55));
 sky130_fd_sc_hd__dlygate4sd3_1 hold13 (.A(\acc0.A[0] ),
    .X(net56));
 sky130_fd_sc_hd__dlygate4sd3_1 hold14 (.A(\acc0.A[2] ),
    .X(net57));
 sky130_fd_sc_hd__dlygate4sd3_1 hold15 (.A(net20),
    .X(net58));
 sky130_fd_sc_hd__dlygate4sd3_1 hold16 (.A(\acc0.A[5] ),
    .X(net59));
 sky130_fd_sc_hd__dlygate4sd3_1 hold17 (.A(\acc0.A[1] ),
    .X(net60));
 sky130_fd_sc_hd__dlygate4sd3_1 hold18 (.A(net18),
    .X(net61));
 sky130_fd_sc_hd__dlygate4sd3_1 hold19 (.A(net19),
    .X(net62));
 sky130_fd_sc_hd__dlygate4sd3_1 hold2 (.A(\comp0.B[3] ),
    .X(net45));
 sky130_fd_sc_hd__dlygate4sd3_1 hold20 (.A(\control0.count[1] ),
    .X(net63));
 sky130_fd_sc_hd__dlygate4sd3_1 hold21 (.A(net21),
    .X(net64));
 sky130_fd_sc_hd__dlygate4sd3_1 hold22 (.A(\acc0.A[3] ),
    .X(net65));
 sky130_fd_sc_hd__dlygate4sd3_1 hold23 (.A(\control0.sh ),
    .X(net66));
 sky130_fd_sc_hd__dlygate4sd3_1 hold24 (.A(net23),
    .X(net67));
 sky130_fd_sc_hd__dlygate4sd3_1 hold25 (.A(\control0.state[2] ),
    .X(net68));
 sky130_fd_sc_hd__dlygate4sd3_1 hold26 (.A(net16),
    .X(net69));
 sky130_fd_sc_hd__dlygate4sd3_1 hold27 (.A(_024_),
    .X(net70));
 sky130_fd_sc_hd__dlygate4sd3_1 hold28 (.A(\control0.state[1] ),
    .X(net71));
 sky130_fd_sc_hd__dlygate4sd3_1 hold29 (.A(net22),
    .X(net72));
 sky130_fd_sc_hd__dlygate4sd3_1 hold3 (.A(\control0.count[2] ),
    .X(net46));
 sky130_fd_sc_hd__dlygate4sd3_1 hold4 (.A(\control0.count[3] ),
    .X(net47));
 sky130_fd_sc_hd__dlygate4sd3_1 hold5 (.A(\comp0.B[2] ),
    .X(net48));
 sky130_fd_sc_hd__dlygate4sd3_1 hold6 (.A(_022_),
    .X(net49));
 sky130_fd_sc_hd__dlygate4sd3_1 hold7 (.A(\comp0.B[1] ),
    .X(net50));
 sky130_fd_sc_hd__dlygate4sd3_1 hold8 (.A(_021_),
    .X(net51));
 sky130_fd_sc_hd__dlygate4sd3_1 hold9 (.A(\acc0.A[6] ),
    .X(net52));
 sky130_fd_sc_hd__clkbuf_1 input1 (.A(A[0]),
    .X(net1));
 sky130_fd_sc_hd__clkbuf_1 input10 (.A(B[1]),
    .X(net10));
 sky130_fd_sc_hd__clkbuf_1 input11 (.A(B[2]),
    .X(net11));
 sky130_fd_sc_hd__clkbuf_1 input12 (.A(B[3]),
    .X(net12));
 sky130_fd_sc_hd__clkbuf_1 input13 (.A(init),
    .X(net13));
 sky130_fd_sc_hd__buf_1 input14 (.A(rst),
    .X(net14));
 sky130_fd_sc_hd__clkbuf_1 input2 (.A(A[1]),
    .X(net2));
 sky130_fd_sc_hd__clkbuf_1 input3 (.A(A[2]),
    .X(net3));
 sky130_fd_sc_hd__clkbuf_1 input4 (.A(A[3]),
    .X(net4));
 sky130_fd_sc_hd__clkbuf_1 input5 (.A(A[4]),
    .X(net5));
 sky130_fd_sc_hd__clkbuf_1 input6 (.A(A[5]),
    .X(net6));
 sky130_fd_sc_hd__clkbuf_1 input7 (.A(A[6]),
    .X(net7));
 sky130_fd_sc_hd__clkbuf_1 input8 (.A(A[7]),
    .X(net8));
 sky130_fd_sc_hd__clkbuf_1 input9 (.A(B[0]),
    .X(net9));
 sky130_fd_sc_hd__buf_2 output15 (.A(net15),
    .X(done));
 sky130_fd_sc_hd__buf_2 output16 (.A(net16),
    .X(pp[0]));
 sky130_fd_sc_hd__buf_2 output17 (.A(net17),
    .X(pp[1]));
 sky130_fd_sc_hd__buf_2 output18 (.A(net18),
    .X(pp[2]));
 sky130_fd_sc_hd__buf_2 output19 (.A(net19),
    .X(pp[3]));
 sky130_fd_sc_hd__clkbuf_4 output20 (.A(net20),
    .X(pp[4]));
 sky130_fd_sc_hd__clkbuf_4 output21 (.A(net21),
    .X(pp[5]));
 sky130_fd_sc_hd__clkbuf_4 output22 (.A(net22),
    .X(pp[6]));
 sky130_fd_sc_hd__buf_2 output23 (.A(net23),
    .X(pp[7]));
endmodule

