import os
import copy
from datetime import datetime
import configparser

CONFIG_FILE = "Config.ini"

class Prod_Info():
    __PROD_NAME = ""
    __G_SA = 0
    __D_SA = 0
    __OFFSET = 0
    __STATE_SKIP = []
    __VALID = 0
    
    def __init__(self, Prod_Name):
        if(os.path.isfile(CONFIG_FILE)):
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)
            for key in config:
                if(Prod_Name == key.upper()):
                    Prod_Name = key #Change upper or lower case to follow in config
                    self.__PROD_NAME = Prod_Name
                    self.__G_SA = int(config[Prod_Name]["gold"], 16)
                    self.__D_SA = int(config[Prod_Name]["dut"], 16)
                    self.__OFFSET = int(config[Prod_Name]["dut_offset"], 16)
                    temp = config[Prod_Name]["state_skip"]
                    if(temp != ""):
                        temp2 = temp.split(",")
                        self.__STATE_SKIP = [int(i) for i in temp2]
                    self.__VALID = 1
            if(self.__VALID == 0):
                print(f'{Prod_Name} is not a valid production name')
        else:
            print(f'{CONFIG_FILE} is not found')

    def is_valid(self):
        return self.__VALID
    
    def Gold_Slave_Address(self):
        return self.__G_SA
    
    def Dut_Slave_Address(self):
        return self.__D_SA
    
    def Site_Offset(self):
        return self.__OFFSET
    
    def State_Skip_Lines(self):
        return self.__STATE_SKIP

def header_atp(outfile, script_file, infile_name, outfile_name):
    now = datetime.now()
    # today = now.strftime('%Y-%m-%d %H:%M:%S')
    today = now.strftime('%Y-%m-%d')
    #timestamp = now.strftime('%Y%m%d%H%M%S')

    outfile.write("///////////////////////////////////////////////////\n")
    outfile.write("// atp file generator\n")
    outfile.write("// Script File : " + script_file + "\n")
    outfile.write("// Input File  : " + infile_name + "\n")
    outfile.write("// Output File : " + outfile_name + "\n")
    outfile.write(f"// Created     : {today}\n")
    outfile.write(f"// Copyright   : Point2 Technology\n")
    outfile.write("///////////////////////////////////////////////////\n\n")
    outfile.write("import tset ts1, ts2;\n\n")
    outfile.write("vm_vector($tset, SCL_G, SDA_G, SCL_D, SDA_D)\n")
    outfile.write("{\n")
    for i in range(10):
        outfile.write("                > ts1 1 1 1 1 ;\n")

def header_avc(outfile, script_file, infile_name, outfile_name, cmd_list = []):
    now = datetime.now()
    # today = now.strftime('%Y-%m-%d %H:%M:%S')
    today = now.strftime('%Y-%m-%d')
    #timestamp = now.strftime('%Y%m%d%H%M%S')

    outfile.write("###################################################\n")
    outfile.write("## avc file generator\n")
    outfile.write("## Script File : " + script_file + "\n")
    outfile.write("## Input File  : " + infile_name + "\n")
    outfile.write("## Output File : " + outfile_name + "\n")
    outfile.write(f"## Created     : {today}\n")
    outfile.write(f"## Copyright   : Point2 Technology\n")
    outfile.write("###################################################\n\n")
    
    if len(cmd_list) != 0:
        for i in cmd_list:
            outfile.write("# " + i + "\n")
        outfile.write("\n")
    
    outfile.write("FORMAT SCL18_G SDA18_G SCL18_D SDA18_D ;\n\n")
    
    for i in range(10):
        outfile.write("R1      ts1 1111 ;\n")

def footer_atp(outfile):
    outfile.write("                > ts1 1 1 1 1 ;\n")
    outfile.write("                > ts1 1 1 1 1 ;\n")
    outfile.write("halt            > ts1 1 1 1 1 ;\n")
    outfile.write("}\n")

def footer_avc(outfile):
    outfile.write("R1      ts1 1111 ;\n")
    outfile.write("R1      ts1 1111 ;\n")
    outfile.write("R1      ts1 1111 ;\n")

def idle_condition_atp(outfile, no_of_repeat):
    str_repeat = str(no_of_repeat).ljust(9)
    outfile.write(f"repeat {str_repeat}> ts1 1 1 1 1 ; // IDLE_WAIT\n")

def idle_condition_avc(outfile, no_of_repeat):
    str_repeat = str(no_of_repeat).ljust(7)
    outfile.write(f"R{str_repeat}ts1 1111 % IDLE_WAIT ;\n")

def start_condition_atp(outfile):
    outfile.write("repeat 100      > ts1 1 1 1 1 ; // Start Condition\n")
    outfile.write("repeat 50       > ts1 1 0 1 0 ; // Start Condition\n")
    outfile.write("repeat 50       > ts1 0 0 0 0 ; // Start Condition\n")

def start_condition_avc(outfile):
    outfile.write("R30     ts1 1111 % BUS Idle ;\n")
    outfile.write("R1      ts1 1111 % Start Condition ;\n")
    outfile.write("R1      ts1 1010 % Start Condition ;\n")
    outfile.write("R1      ts1 0000 ;\n")

def stop_condition_atp(outfile):
    outfile.write("repeat 100      > ts1 0 0 0 0 ; // Stop Condition\n")
    outfile.write("repeat 50       > ts1 1 0 1 0 ; // Stop Condition\n")
    outfile.write("repeat 50       > ts1 1 1 1 1 ; // Stop Condition\n")

def stop_condition_avc(outfile):
    outfile.write("R1      ts1 1010 % Stop Condition ;\n")
    outfile.write("R1      ts1 1111 % Stop Condition ;\n")
    outfile.write("R30     ts1 1111 % BUS Idle ;\n")

def repeated_start_condition_atp(outfile):
    outfile.write("repeat 10       > ts1 0 1 0 1 ; // Repeated Start Condition\n")
    outfile.write("repeat 10       > ts1 1 1 1 1 ; // Repeated Start Condition\n")
    outfile.write("repeat 10       > ts1 1 0 1 0 ; // Repeated Start Condition\n")
    outfile.write("repeat 10       > ts1 0 0 0 0 ; // Repeated Start Condition\n")

def slave_addr_atp(outfile, g_sa, d_sa):
    for i in range(8):
        g_bit = "1" if(g_sa & 2**(7-i) == 2**(7-i)) else "0"
        d_bit = "1" if(d_sa & 2**(7-i) == 2**(7-i)) else "0"
        if(i==0):
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ; // SA[0x{format(g_sa, "02X")} / 0x{format(d_sa, "02X")}]\n')
        else:
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ;\n')
    outfile.write(f'                > ts2 1 L 1 L ; // Ack\n')

def slave_addr_avc(outfile, g_sa, d_sa):
    for i in range(8):
        g_bit = "1" if(g_sa & 2**(7-i) == 2**(7-i)) else "0"
        d_bit = "1" if(d_sa & 2**(7-i) == 2**(7-i)) else "0"
        if(i==0):
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} % SA[0x{format(g_sa, "02X")} / 0x{format(d_sa, "02X")}] ;\n')
        else:
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} ;\n')
    outfile.write("R1      ts1 PLPL % Ack ;\n")
    outfile.write("R1      ts1 0000 ;\n")

def reg_or_data_atp(outfile, g_data, d_data, comment):
    for i in range(16):
        g_bit = "1" if(g_data & 2**(15-i) == 2**(15-i)) else "0"
        d_bit = "1" if(d_data & 2**(15-i) == 2**(15-i)) else "0"
        if(i==0):
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ; // {comment}[0x{format(g_data, "04X")} / 0x{format(d_data, "04X")}]\n')
        else:
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ;\n')
        if((i+1)%8==0):
            outfile.write(f'                > ts2 1 L 1 L ; // Ack\n')

def reg_or_data_read_atp(outfile, g_data, d_data, comment, mask_opt=0):
    for i in range(16):
        if mask_opt == 0:
            g_bit = "H" if(g_data & 2**(15-i) == 2**(15-i)) else "L"
            d_bit = "H" if(d_data & 2**(15-i) == 2**(15-i)) else "L"
        else:
            g_bit = "V"
            d_bit = "V"
        if(i==0):
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ; // {comment}[0x{format(g_data, "04X")} / 0x{format(d_data, "04X")}]\n')
        else:
            outfile.write(f'                > ts2 1 {g_bit} 1 {d_bit} ;\n')
        if((i+1)==8):
            outfile.write(f'                > ts2 1 0 1 0 ; // Master Ack\n')
        if((i+1)==16):
            outfile.write(f'                > ts2 1 1 1 1 ; // Master NAck\n')

def reg_or_data_avc(outfile, g_data, d_data, comment):
    for i in range(16):
        g_bit = "1" if(g_data & 2**(15-i) == 2**(15-i)) else "0"
        d_bit = "1" if(d_data & 2**(15-i) == 2**(15-i)) else "0"
        if(i==0):
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} % {comment}[0x{format(g_data, "04X")} / 0x{format(d_data, "04X")}] ;\n')
        else:
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} ;\n')
        
        if((i+1)%8==0):
            outfile.write(f'R1      ts1 PLPL % Ack ;\n')
            outfile.write(f'R1      ts1 0000 ;\n')

def reg_or_data_read_avc(outfile, g_data, d_data, comment, mask_opt=0):
    for i in range(16):
        if mask_opt == 0:
            g_bit = "H" if(g_data & 2**(15-i) == 2**(15-i)) else "L"
            d_bit = "H" if(d_data & 2**(15-i) == 2**(15-i)) else "L"
        elif mask_opt == 1:
            g_bit = "C"
            d_bit = "C"
        else:
            print(f'Wrong mask_option = {mask_opt}')
            
        if(i==0):
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} % {comment}[0x{format(g_data, "04X")} / 0x{format(d_data, "04X")}] ;\n')
        else:
            outfile.write(f'R1      ts1 P{g_bit}P{d_bit} ;\n')
        
        if((i+1)==8):
            outfile.write(f'R1      ts1 P0P0 % Master Ack ;\n')
            outfile.write(f'R1      ts1 0000 ;\n')
        if((i+1)==16):
            outfile.write(f'R1      ts1 P1P1 % Master NAck ;\n')
            outfile.write(f'R1      ts1 0000 ;\n')

def data_sort_state(infile, offset, skip_line = [-1]):
    dut_data = []
    gold_data = []
    cmd_list = []
    state_line = 0
    first_dut = 0
    dut_offset = 0
    for line in infile:
        line = line.strip()
        if(line.startswith("#")):
            continue
        #data = line.split(",")
        temp_data = line.split("#")
        data = temp_data[0].split(",")
        if len(skip_line) == 1:
            if data[0] == "Address":
                cmd_list.append("RD=ReadData / DC=DigitalCapture / IDLE=IDLE_WAIT repeat xxxx")
            else:
                cmd_list.append(line)
        if((len(data) == 2) | (len(data) == 3)):
            if(data[0] == "Address"):
                continue
            if(data[0] == "RD"):
                state = 1
                regaddr = int(data[1], 16)
                val = int(data[2], 16)
            elif(data[0] == "DC"):
                state = 2
                regaddr = int(data[1], 16)
                val = 0
            elif(data[0] == "IDLE"):
                state = 100
                regaddr = 0xF000
                val = int(data[1])
            else:
                state = 0
                regaddr = int(data[0], 16)
                val = int(data[1], 16)
            state_line += 1
            if(regaddr >= 0x1F000): # For 0x1FCFC will treats as DUT data
                if(first_dut == 0):
                    state_line = 1 #Initialize for the DUT
                    first_dut = 1
                tgt = "DUT"
                dut_offset = 0x10000
            elif(regaddr >= 0xF000):
                tgt = "GOLD"
                dut_offset = 0
            elif(regaddr < offset):
                tgt = "GOLD"
                dut_offset = 0
            else:
                if(first_dut == 0):
                    state_line = 1 #Initialize for the DUT
                    first_dut = 1
                tgt = "DUT"
                dut_offset = offset
                
            if not state_line in skip_line:
                if tgt == "DUT":
                    dut_data.append({"read":state, "reg":regaddr - dut_offset, "data":val, "target":"DUT"})
                else:
                    gold_data.append({"read":state, "reg":regaddr - dut_offset, "data":val, "target":"GOLD"})
    
    if(len(dut_data) != len(gold_data)):
        print(f'Number of register count is not matched : {len(gold_data)} vs {len(dut_data)}')

    if(len(dut_data) == 0):
        print("Gold data will be coppied to Dut data")
        dut_data = copy.deepcopy(gold_data)
    
    for idx in range(len(gold_data)):
        if(gold_data[idx]["reg"] != dut_data[idx]["reg"]):
            print(f'Error line:{idx} register address is not matched G={gold_data[idx]["reg"]} vs D={dut_data[idx]["reg"]}')
    
    return gold_data, dut_data, cmd_list

def data_sort_FW(infile):
    fw_data = []
    for line in infile:
        line = line.strip()
        if(line.startswith("#")):
            continue
        data = line.split(",")
        if(len(data) == 2):
            if(data[0] == "Address"):
                continue
            # Get Register information
            temp = data[0].strip()
            if(temp.startswith("0x")):
                reg = int(temp[2:], 16)
            else:
                reg = int(temp, 16)
            # Get Data information
            temp = data[1].strip()
            if(temp.startswith("0x")):
                data = int(temp[2:], 16)
            else:
                data = int(temp, 16)
            # Binding RA and Data
            fw_data.append({"reg":reg, "data":data})
    return fw_data