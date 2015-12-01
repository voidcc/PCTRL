'''
Created on 2015.7.1.
@author: Cen
'''
from pox.core import core
import pox.openflow.libpof_02 as of
from pox.lib.revent.revent import EventMixin
from pox.forwarding.l2_multi import Switch

DEVICE_ID = 2215152430   # software switch, for test

device_map = { # HUAWEI switch
              "USTC"   : 2352562177,
              "CNIC"   : 2352388391,
              "IOA"    : 2352858652,
              "HUAWEI" : 4103510098,
              "IIE"    : 1055891609,
              }

def _add_protocol(protocol_name, field_list):
    """
    Define a new protocol, and save it to PMDatabase.
    
    protocol_name: string
    field_list:[("field_name", length)]
    """
    match_field_list = []
    total_offset = 0
    for field in field_list:
        field_id = core.PofManager.new_field(field[0], total_offset, field[1])   #field[0]:field_name, field[1]:length
        total_offset += field[1]
        match_field_list.append(core.PofManager.get_field(field_id))
    core.PofManager.add_protocol("protocol_name", match_field_list)
    
def add_protocol():   # TODO: add 10 different protocol
    field_list = [("DMAC",48), ("SMAC",48), ("Eth_Type",16), ("V_IHL_TOS",16), ("Total_Len",16),
                  ("ID_Flag_Offset",32), ("TTL",8), ("Protocol",8), ("Checksum",16), ("SIP",32), ("DIP",32),
                  ("UDP_Sport",16), ("UDP_Dport",16), ("UDP_Len",16), ("UDP_Checksum",16)]
    _add_protocol("ETH_IPV4_UDP", field_list)
    
def add_metadata():
    """
    Define the metadata, and save it to PMDatabase.
    field_list:[("field_name", length)]
    """
    metadata_list = [("Pkt_Len",16),("InPort",8),("Rsv",8),("DMAC",48),("SMAC",48),("Eth_Type",16),
                     ("V_IHL_TOS",16),("Total_Len",16),("ID_Flag_Offset",32),("TTL",8),("Protocol",8),("Checksum",16),
                     ("SIP",32),("DIP",32),("UDP_Sport",16),("UDP_Dport",16),("UDP_Len",16),("UDP_Checksum",16),
                     ("VxLan_Flag",8),("VxLan_Rsv_1",24),("VxLan_VNI",24),("VxLan_Rsv_2",8)]
    total_offset = 0
    for field in metadata_list:
        core.PofManager.new_metadata_field(field[0], total_offset, field[1])
        total_offset += field[1]
        
def add_table(device_id):
    core.PofManager.add_flow_table(device_id, 'FirstEntryTable', of.OF_MM_TABLE, 32, [core.PofManager.get_field("DMAC")[0]])
    core.PofManager.add_flow_table(device_id, 'L2PA', of.OF_MM_TABLE, 32,  [core.PofManager.get_field("Eth_Type")[0]])
    core.PofManager.add_flow_table(device_id, 'L3PA', of.OF_MM_TABLE, 32, [core.PofManager.get_field("Protocol")[0],core.PofManager.get_field("UDP_Dport")[0]])
    core.PofManager.add_flow_table(device_id, 'FIB', of.OF_LPM_TABLE, 32, [core.PofManager.get_metadata_field("DIP")])
    core.PofManager.add_flow_table(device_id, 'MacMap', of.OF_LINEAR_TABLE, 32)   #16
    core.PofManager.add_flow_table(device_id, 'VNI', of.OF_LINEAR_TABLE, 32)      #17
    core.PofManager.add_flow_table(device_id, 'VxLanEncap', of.OF_LINEAR_TABLE, 32)  #18
    core.PofManager.add_flow_table(device_id, 'FIB_DT', of.OF_LINEAR_TABLE, 32)   #19
    core.PofManager.add_flow_table(device_id, 'EPAT', of.OF_LINEAR_TABLE, 32)    #20
    core.PofManager.add_flow_table(device_id, 'VxLanDecap', of.OF_LINEAR_TABLE, 32)  #21
    
def add_entry_ustc():
    device_id = device_map["USTC"]
    #device_id = DEVICE_ID
    
    # FirstEntryTable (MM) 0
    table_id = core.PofManager.get_flow_table_id(device_id, 'FirstEntryTable')
    match = core.PofManager.get_field("DMAC")[0]
    # FirstEntryTable (MM) 0-0
    temp_matchx = core.PofManager.new_matchx(match, '6cf0498cd47b', 'FFFFFFFFFFFF')   #PC1, IOA
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)    #goto VNI-1
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-1
    temp_matchx = core.PofManager.new_matchx(match, '90e2ba2a22ca', 'FFFFFFFFFFFF')   #PC2, CNIC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)    #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-2
    temp_matchx = core.PofManager.new_matchx(match, '000000000003', 'FFFFFFFFFFFF')   #PC3, USTC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  #goto MACMAP
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-3
    temp_matchx = core.PofManager.new_matchx(match, '382c4ac5e439', 'FFFFFFFFFFFF')   #PC3, USTC, 3.11
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)   #goto EPAT:OUTPUT
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-4
    temp_matchx = core.PofManager.new_matchx(match, '70F3950B7EC7', 'FFFFFFFFFFFF')   #PC4, HUAWEI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 2, None)    #goto VNI-2
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-5
    temp_matchx = core.PofManager.new_matchx(match, '00e081e9e4bc', 'FFFFFFFFFFFF')   #PC5, IIE
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')   # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 3, None)    #goto VNI-3
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-6
    temp_matchx = core.PofManager.new_matchx(match, '643E8C394002', 'FFFFFFFFFFFF')   #USTC SW
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')   # 1
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)           #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-7
    temp_matchx = core.PofManager.new_matchx(match, 'FFFFFFFFFFFF', 'FFFFFFFFFFFF')   #ARP
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)            #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L2PA (MM) 1
    table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    match = core.PofManager.get_field("Eth_Type")[0]
    # L2PA (MM) 1-0
    temp_matchx = core.PofManager.new_matchx(match, '0800', 'FFFF')   #IPV4
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # L2PA (MM) 1-1
    temp_matchx = core.PofManager.new_matchx(match, '0806', 'FFFF')   #ARP
    temp_action = core.PofManager.new_action_output(0, 0, 0, 0, 0x1003a)
    temp_ins = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L3PA (MM) 2
    table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')  # 2
    match_1 = core.PofManager.get_field("Protocol")[0]
    match_2 = core.PofManager.get_field("UDP_Dport")[0]
    # L3PA (MM) 2-0
    temp_matchx_1 = core.PofManager.new_matchx(match_1, '11', 'FF')       # UDP
    temp_matchx_2 = core.PofManager.new_matchx(match_2, '12B5', 'FFFF')   # VxLan
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto VxLanDecap
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx_1, temp_matchx_2], [temp_ins])
    
    # MACMAP (LINEAR) 16
    table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    # MACMAP (LINEAR) 16-0
    temp_matchx = core.PofManager.new_matchx(0, '382c4ac5e439', 'FFFFFFFFFFFF')   # PC3, USTC
    temp_action = core.PofManager.new_action_set_field(temp_matchx)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # VNI (LINEAR) 17
    table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    # VNI (LINEAR) 17-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '72D6A6C1')  # SIP, USTC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '9FE23D4B')  # DIP, CNIC SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000032')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '72D6A6C1')  # SIP, USTC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, 'D24BE144')  # DIP, IOA SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000031')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-2
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '72D6A6C1')  # SIP, USTC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '3AFB9F4C')  # DIP, HUAWEI SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000034')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-3
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '72D6A6C1')  # SIP, USTC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '6FCCDBF5')  # DIP, IIE SW, 111.204.219.245
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000035')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    
    # VxLanEncap (LINEAR) 18
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    # VxLanEncap (LINEAR) 18-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(128, 16, '0800')  # ETH_TYPE, ipv4
    temp_ins_2 = core.PofManager.new_ins_write_metadata(144, 16, '4500')  # V_IHL_TOS
    temp_ins_3 = core.PofManager.new_ins_write_metadata(208, 16, '4011')  # TTL_PROTOCOL
    temp_ins_4 = core.PofManager.new_ins_write_metadata(320, 16, '12B5')  # UDP_Dport, VxLan
    temp_ins_5 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 1, None)   #goto VxLanEncap-1
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4, temp_ins_5])
    # VxLanEncap (LINEAR) 18-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(304, 16, '04d2')  # UDP_Sport, 1234
    temp_ins_2 = core.PofManager.new_ins_write_metadata(368, 8, '80')  # VxLan Flag
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 2, None)   #goto VxLanEncap-2
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-2
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("UDP_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("Total_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 3, None)   #goto VxLanEncap-3
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-3
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("UDP_Len"), 16, None)
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("Total_Len"), 36, None)
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 4, None)   #goto VxLanEncap-4
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-4
    temp_action = core.PofManager.new_action_calculate_checksum(1,1,224,16,144,160)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')
    temp_ins_2 = core.PofManager.new_ins_goto_table(device_id, next_table_id)  # goto FIB
    core.PofManager.add_flow_entry(device_id, 18, [], [temp_ins_1, temp_ins_2])
    
    # FIB (LPM) 8
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')  # 8
    match = core.PofManager.get_metadata_field("DIP")
    # FIB (LPM) 8-0
    temp_matchx = core.PofManager.new_matchx(match, "00000000", '00000000') 
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')   # 19
    temp_ins = core.PofManager.new_ins_goto_direct_table(19, 0, 0, 0, None)  # goto FIB-DT-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # FIB-DT (LINEAR) 19
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')  # 19
    # FIB-DT (LINEAR) 19-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(32, 48, '001244662000')  # DMAC, USTC Gateway MAC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')   # 20
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto EPAT-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # EPAT (LINEAR) 20
    table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    # EPAT (LINEAR) 20-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(80, 48, '643e8c394002')  # USTC SW MAC
    temp_action = core.PofManager.new_action_output(0, 32, 400, 0, 0x10041)
    temp_ins_2 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    # EPAT (LINEAR) 20-1
    temp_action = core.PofManager.new_action_output(0, 0, 0, 50, 0x10045)   # to PC3
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
    
    # VxLanDecap (LINEAR) 21
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')  # 20
    # VxLanDecap (LINEAR) 21-0
    temp_ins_1 = core.PofManager.new_ins_goto_table(device_id, 0, 50)  # goto First
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
    
    
def add_entry_cnic():
    device_id = device_map["CNIC"]
    #device_id = DEVICE_ID
    
    # FirstEntryTable (MM) 0
    table_id = core.PofManager.get_flow_table_id(device_id, 'FirstEntryTable')
    match = core.PofManager.get_field("DMAC")[0]
    # FirstEntryTable (MM) 0-0
    temp_matchx = core.PofManager.new_matchx(match, '6cf0498cd47b', 'FFFFFFFFFFFF')   #PC1, IOA
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)    #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-1
    temp_matchx = core.PofManager.new_matchx(match, '000000000002', 'FFFFFFFFFFFF')   #PC2, CNIC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)    #goto MACMAP
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-2
    temp_matchx = core.PofManager.new_matchx(match, '90e2ba2a22ca', 'FFFFFFFFFFFF')   #PC2, CNIC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)  #goto EPAT
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-3
    temp_matchx = core.PofManager.new_matchx(match, '382c4ac5e439', 'FFFFFFFFFFFF')   #PC3, USTC, 3.11
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)   #goto EPAT:OUTPUT
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-4
    temp_matchx = core.PofManager.new_matchx(match, '70F3950B7EC7', 'FFFFFFFFFFFF')   #PC4, HUAWEI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 2, None)    #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-5
    temp_matchx = core.PofManager.new_matchx(match, '00e081e9e4bc', 'FFFFFFFFFFFF')   #PC5, IIE
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 3, None)    #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # FirstEntryTable (MM) 0-5
    temp_matchx = core.PofManager.new_matchx(match, '643e8c369927', 'FFFFFFFFFFFF')   #CNIC SW
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)           #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-6
    temp_matchx = core.PofManager.new_matchx(match, 'FFFFFFFFFFFF', 'FFFFFFFFFFFF')   #ARP
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)            #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L2PA (MM) 1
    table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    match = core.PofManager.get_field("Eth_Type")[0]
    # L2PA (MM) 1-0
    temp_matchx = core.PofManager.new_matchx(match, '0800', 'FFFF')   #IPV4
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # L2PA (MM) 1-1
    temp_matchx = core.PofManager.new_matchx(match, '0806', 'FFFF')   #ARP
    temp_action = core.PofManager.new_action_output(0, 0, 0, 0, 0x1003a)
    temp_ins = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L3PA (MM) 2
    table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')  # 2
    match_1 = core.PofManager.get_field("Protocol")[0]
    match_2 = core.PofManager.get_field("UDP_Dport")[0]
    # L3PA (MM) 2-0
    temp_matchx_1 = core.PofManager.new_matchx(match_1, '11', 'FF')       # UDP
    temp_matchx_2 = core.PofManager.new_matchx(match_2, '12B5', 'FFFF')   # VxLan
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto VxLanDecap
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx_1, temp_matchx_2], [temp_ins])
    
    # MACMAP (LINEAR) 16
    table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    # MACMAP (LINEAR) 16-0
    temp_matchx = core.PofManager.new_matchx(0, '90e2ba2a22ca', 'FFFFFFFFFFFF')   # PC3, USTC
    temp_action = core.PofManager.new_action_set_field(temp_matchx)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # VNI (LINEAR) 17
    table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    # VNI (LINEAR) 17-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '9FE23D4B')  # SIP, CNIC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, 'D24BE144')  # DIP, IOA SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000021')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '9FE23D4B')  # SIP, CNIC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '72d6a6c1')  # DIP, USTC SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000023')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-2
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '9FE23D4B')  # SIP, CNIC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '3AFB9F4C')  # DIP, HUAWEI SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000024')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-3
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '9FE23D4B')  # SIP, CNIC SW
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '6FCCDBF5')  # DIP, IIE SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000025')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    
    
    # VxLanEncap (LINEAR) 18
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    # VxLanEncap (LINEAR) 18-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(128, 16, '0800')  # ETH_TYPE, ipv4
    temp_ins_2 = core.PofManager.new_ins_write_metadata(144, 16, '4500')  # V_IHL_TOS
    temp_ins_3 = core.PofManager.new_ins_write_metadata(208, 16, '4011')  # TTL_PROTOCOL
    temp_ins_4 = core.PofManager.new_ins_write_metadata(320, 16, '12B5')  # UDP_Dport, VxLan
    temp_ins_5 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 1, None)   #goto VxLanEncap-1
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4, temp_ins_5])
    # VxLanEncap (LINEAR) 18-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(304, 16, '04d2')  # UDP_Sport, 1234
    temp_ins_2 = core.PofManager.new_ins_write_metadata(368, 8, '80')  # VxLan Flag
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 2, None)   #goto VxLanEncap-2
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-2
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("UDP_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("Total_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 3, None)   #goto VxLanEncap-3
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-3
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("UDP_Len"), 16, None)
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("Total_Len"), 36, None)
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 4, None)   #goto VxLanEncap-4
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-4
    temp_action = core.PofManager.new_action_calculate_checksum(1,1,224,16,144,160)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')
    temp_ins_2 = core.PofManager.new_ins_goto_table(device_id, next_table_id)  # goto FIB
    core.PofManager.add_flow_entry(device_id, 18, [], [temp_ins_1, temp_ins_2])
    
    # FIB (LPM) 8
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')  # 8
    match = core.PofManager.get_metadata_field("DIP")
    # FIB (LPM) 8-0
    temp_matchx = core.PofManager.new_matchx(match, "00000000", '00000000') 
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')   # 19
    temp_ins = core.PofManager.new_ins_goto_direct_table(19, 0, 0, 0, None)  # goto FIB-DT-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # FIB-DT (LINEAR) 19
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')  # 19
    # FIB-DT (LINEAR) 19-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(32, 48, '90e2ba2a22cb')  # DMAC, CNIC Gateway MAC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')   # 20
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto EPAT-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # EPAT (LINEAR) 20
    table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    # EPAT (LINEAR) 20-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(80, 48, '643e8c369927')  # SMAC, CNIC SW MAC
    temp_action = core.PofManager.new_action_output(0, 32, 400, 0, 0x20000)
    temp_ins_2 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    # EPAT (LINEAR) 20-1
    temp_action = core.PofManager.new_action_output(0, 0, 0, 50, 0x20002)   # to PC2
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
    
    # VxLanDecap (LINEAR) 21
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')  # 20
    # VxLanDecap (LINEAR) 21-0
    temp_ins_1 = core.PofManager.new_ins_goto_table(device_id, 0, 50)  # goto First
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
    
    
def add_entry_iie():
    device_id = device_map["IIE"]
    #device_id = DEVICE_ID
    
    # FirstEntryTable (MM) 0
    table_id = core.PofManager.get_flow_table_id(device_id, 'FirstEntryTable')
    match = core.PofManager.get_field("DMAC")[0]
    # FirstEntryTable (MM) 0-0
    temp_matchx = core.PofManager.new_matchx(match, '6cf0498cd47b', 'FFFFFFFFFFFF')   #PC1, IOA
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)    #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-1
    temp_matchx = core.PofManager.new_matchx(match, '90e2ba2a22ca', 'FFFFFFFFFFFF')   #PC2, CNIC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)    #goto VNI-1
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-2
    temp_matchx = core.PofManager.new_matchx(match, '382c4ac5e439', 'FFFFFFFFFFFF')   #PC3, USTC, 3.11
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 2, None)   #goto VNI-2
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-3
    temp_matchx = core.PofManager.new_matchx(match, '70F3950B7EC7', 'FFFFFFFFFFFF')   #PC4, HUAWEI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 3, None)    #goto VNI-3
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-4
    temp_matchx = core.PofManager.new_matchx(match, '000000000005', 'FFFFFFFFFFFF')   #PC5, IIE
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)    #goto MACMAP
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-5
    temp_matchx = core.PofManager.new_matchx(match, '00e081e9e4bc', 'FFFFFFFFFFFF')   #PC5, IIE
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 1, None)  #goto EPAT
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-6
    temp_matchx = core.PofManager.new_matchx(match, '7ca23eefa09a', 'FFFFFFFFFFFF')   #IIE SW  #FIXME:
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)           #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # FirstEntryTable (MM) 0-7
    temp_matchx = core.PofManager.new_matchx(match, 'FFFFFFFFFFFF', 'FFFFFFFFFFFF')   #ARP
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)            #goto L2PA
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L2PA (MM) 1
    table_id = core.PofManager.get_flow_table_id(device_id, 'L2PA')  # 1
    match = core.PofManager.get_field("Eth_Type")[0]
    # L2PA (MM) 1-0
    temp_matchx = core.PofManager.new_matchx(match, '0800', 'FFFF')   #IPV4
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')
    temp_ins = core.PofManager.new_ins_goto_table(device_id, next_table_id)
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    # L2PA (MM) 1-1
    temp_matchx = core.PofManager.new_matchx(match, '0806', 'FFFF')   #ARP
    temp_action = core.PofManager.new_action_output(0, 0, 0, 0, 0x1003a)
    temp_ins = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # L3PA (MM) 2
    table_id = core.PofManager.get_flow_table_id(device_id, 'L3PA')  # 2
    match_1 = core.PofManager.get_field("Protocol")[0]
    match_2 = core.PofManager.get_field("UDP_Dport")[0]
    # L3PA (MM) 2-0
    temp_matchx_1 = core.PofManager.new_matchx(match_1, '11', 'FF')       # UDP
    temp_matchx_2 = core.PofManager.new_matchx(match_2, '12B5', 'FFFF')   # VxLan
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')
    temp_ins = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto VxLanDecap
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx_1, temp_matchx_2], [temp_ins])
    
    # MACMAP (LINEAR) 16
    table_id = core.PofManager.get_flow_table_id(device_id, 'MacMap')  # 16
    # MACMAP (LINEAR) 16-0
    temp_matchx = core.PofManager.new_matchx(0, '00e081e9e4bc', 'FFFFFFFFFFFF')   # PC5, IIE
    temp_action = core.PofManager.new_action_set_field(temp_matchx)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VNI-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # VNI (LINEAR) 17
    table_id = core.PofManager.get_flow_table_id(device_id, 'VNI')  # 17
    # VNI (LINEAR) 17-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '0A0A04F6')  # SIP, IIE SW, 10.10.4.246
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, 'D24BE144')  # DIP, IOA SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000051')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '0A0A04F6')  # SIP, IIE SW, 10.10.4.246
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '9FE23D4B')  # DIP, CNIC SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000052')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-2
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '0A0A04F6')  # SIP, IIE SW, 10.10.4.246
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '72d6a6c1')  # DIP, USTC SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000053')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    # VNI (LINEAR) 17-3
    temp_ins_1 = core.PofManager.new_ins_write_metadata(240, 32, '0A0A04F6')  # SIP, IIE SW, 10.10.4.246
    temp_ins_2 = core.PofManager.new_ins_write_metadata(272, 32, '3AFB9F4C')  # DIP, HUAWEI SW
    temp_ins_3 = core.PofManager.new_ins_write_metadata(400, 24, '000054')    # VNI
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap') # 18
    temp_ins_4 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)   #goto VxLanEncap-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4])
    
    # VxLanEncap (LINEAR) 18
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanEncap')  # 18
    # VxLanEncap (LINEAR) 18-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(128, 16, '0800')  # ETH_TYPE, ipv4
    temp_ins_2 = core.PofManager.new_ins_write_metadata(144, 16, '4500')  # V_IHL_TOS
    temp_ins_3 = core.PofManager.new_ins_write_metadata(208, 16, '4011')  # TTL_PROTOCOL
    temp_ins_4 = core.PofManager.new_ins_write_metadata(320, 16, '12B5')  # UDP_Dport, VxLan
    temp_ins_5 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 1, None)   #goto VxLanEncap-1
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3, temp_ins_4, temp_ins_5])
    # VxLanEncap (LINEAR) 18-1
    temp_ins_1 = core.PofManager.new_ins_write_metadata(304, 16, '04d2')  # UDP_Sport, 1234
    temp_ins_2 = core.PofManager.new_ins_write_metadata(368, 8, '80')  # VxLan Flag
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 2, None)   #goto VxLanEncap-2
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-2
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("UDP_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 1, core.PofManager.get_metadata_field("Total_Len"), 0, core.PofManager.get_metadata_field("Pkt_Len"))
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 3, None)   #goto VxLanEncap-3
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-3
    temp_ins_1 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("UDP_Len"), 16, None)
    temp_ins_2 = core.PofManager.new_ins_calculate_field(of.OFPCT_ADD, 0, core.PofManager.get_metadata_field("Total_Len"), 36, None)
    temp_ins_3 = core.PofManager.new_ins_goto_direct_table(table_id, 0, 0, 4, None)   #goto VxLanEncap-4
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2, temp_ins_3])
    # VxLanEncap (LINEAR) 18-4
    temp_action = core.PofManager.new_action_calculate_checksum(1,1,224,16,144,160)
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')
    temp_ins_2 = core.PofManager.new_ins_goto_table(device_id, next_table_id)  # goto FIB
    core.PofManager.add_flow_entry(device_id, 18, [], [temp_ins_1, temp_ins_2])
    
    # FIB (LPM) 8
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB')  # 8
    match = core.PofManager.get_metadata_field("DIP")
    # FIB (LPM) 8-0
    temp_matchx = core.PofManager.new_matchx(match, "00000000", '00000000') 
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')   # 19
    temp_ins = core.PofManager.new_ins_goto_direct_table(19, 0, 0, 0, None)  # goto FIB-DT-0
    core.PofManager.add_flow_entry(device_id, table_id, [temp_matchx], [temp_ins])
    
    # FIB-DT (LINEAR) 19
    table_id = core.PofManager.get_flow_table_id(device_id, 'FIB_DT')  # 19
    # FIB-DT (LINEAR) 19-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(32, 48, '04f938b83155')  # DMAC, IIE Gateway MAC
    next_table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')   # 20
    temp_ins_2 = core.PofManager.new_ins_goto_direct_table(next_table_id, 0, 0, 0, None)  # goto EPAT-0
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    
    # EPAT (LINEAR) 20
    table_id = core.PofManager.get_flow_table_id(device_id, 'EPAT')  # 20
    # EPAT (LINEAR) 20-0
    temp_ins_1 = core.PofManager.new_ins_write_metadata(80, 48, '7ca23eefa09a')  # SMAC, IIE SW MAC  #FIXME:
    temp_action = core.PofManager.new_action_output(0, 32, 400, 0, 0x20001)    #FIXME:
    temp_ins_2 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1, temp_ins_2])
    # EPAT (LINEAR) 20-1
    temp_action = core.PofManager.new_action_output(0, 0, 0, 50, 0x20003)   # to PC5   #FIXME:
    temp_ins_1 = core.PofManager.new_ins_apply_actions([temp_action])
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
    
    # VxLanDecap (LINEAR) 21
    table_id = core.PofManager.get_flow_table_id(device_id, 'VxLanDecap')  # 20
    # VxLanDecap (LINEAR) 21-0
    temp_ins_1 = core.PofManager.new_ins_goto_table(device_id, 0, 50)  # goto First
    core.PofManager.add_flow_entry(device_id, table_id, [], [temp_ins_1])
        
        
class Test (EventMixin):
    def __init__ (self):
        add_protocol()
        add_metadata()
        core.openflow.addListeners(self, priority=0)   # Listen to dependencies
            
    def _handle_ConnectionUp (self, event):
        add_table(event.dpid)  # add table
        
        #add entry
        if event.dpid == device_map.get("USTC"):
            add_entry_ustc()
        if event.dpid == device_map.get("CNIC"):
            add_entry_cnic()
        """
        if event.dpid == device_map.get("IOA"):
            add_entry_ioa()
        if event.dpid == device_map.get("HUAWEI"):
            add_entry_huawei()
        """
        if event.dpid == device_map.get("IIE"):
            add_entry_iie()
        
    def _handle_PortStatus(self, event):
        port_id = event.ofp.desc.port_id
        if event.dpid == device_map.get("USTC"):
            if port_id == 0x10041 or port_id == 0x10045:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        if event.dpid == device_map.get("CNIC"):
            if port_id == 0x20000 or port_id == 0x20002:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        if event.dpid == device_map.get("IOA"):
            if port_id == 0x10041 or port_id == 0x10043:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        if event.dpid == device_map.get("HUAWEI"):
            if port_id == 0x20001 or port_id == 0x20003:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        if event.dpid == device_map.get("IIE"):
            if port_id == 0x20001 or port_id == 0x20003:
                core.PofManager.set_port_of_enable(event.dpid, port_id)
        
def launch ():
    core.registerNew(Test)