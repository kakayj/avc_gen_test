import os
import sys
from Lib_Common import data_sort_state, header_avc, start_condition_avc, slave_addr_avc, reg_or_data_avc, stop_condition_avc, footer_avc, Prod_Info, reg_or_data_read_avc, idle_condition_avc

def run(state_file, project):

    prod = Prod_Info(project)
    if(prod.is_valid == 0):
        print("Error!!")
        exit(1)

    Script_File = os.path.basename(__file__)
    temp = os.path.splitext(state_file)
    file_name = temp[0]
    file_ext = temp[1][1:]#remove "." from file extension
    out_file = f'{file_name}.avc'
        
    outFile = open(out_file, "w")
    inFile = open(state_file, mode="r", encoding="utf-8")

    Offset = prod.Site_Offset()
    is_state_file = 1 if file_ext != "txt" else 0
    if is_state_file == 1:
        print("This is state file, state skip line will be applied!!")
        state_skip_lines = prod.State_Skip_Lines() # Only state file need R/O skip
    else:
        print("This is NOT state file!!")
        state_skip_lines = [-1]
    g_data, d_data, command_list = data_sort_state(inFile, Offset, state_skip_lines)
    inFile.close()

    if(len(g_data) == 0):
        print(f'Error!!! Please check format {state_file}')
        exit(1)
    if(len(g_data) != len(d_data)):
        print(f'Error!!! Please check length {state_file}')
        print(f'{len(g_data)} vs {len(d_data)}')
        exit(1)

    dut_slave_addr = prod.Dut_Slave_Address()
    gold_slave_addr = prod.Gold_Slave_Address()
    
    header_avc(outFile, Script_File, state_file, out_file, command_list)
    
    for line in range(len(g_data)):
        read_g = g_data[line]["read"]
        read_d = d_data[line]["read"]
        reg_addr = g_data[line]["reg"]
        reg_data_g = g_data[line]["data"]
        reg_data_d = d_data[line]["data"]
        
        if(read_g == read_d):
            if read_g == 1:
                opt_read = 1
            elif read_g ==2:
                opt_read = 2
            elif read_g ==100:
                opt_read = 100
            else:
                opt_read = 0
        else:   
            print("Error GOLD and DUT are not in same R/W Mode!!")
            outFile.close()
            exit(1)
        if (opt_read == 0):
            start_condition_avc(outFile)
            slave_addr_avc(outFile, gold_slave_addr, dut_slave_addr)
            reg_or_data_avc(outFile, reg_addr, reg_addr, "RA")
            reg_or_data_avc(outFile, reg_data_g, reg_data_d, "Data")
            stop_condition_avc(outFile)
        elif (opt_read == 100):
            idle_condition_avc(outFile, reg_data_g)
        else:
            start_condition_avc(outFile)
            slave_addr_avc(outFile, gold_slave_addr, dut_slave_addr)
            reg_or_data_avc(outFile, reg_addr, reg_addr, "RA")
            stop_condition_avc(outFile)
            start_condition_avc(outFile)
            slave_addr_avc(outFile, gold_slave_addr+1, dut_slave_addr+1)
            if opt_read == 1:
                reg_or_data_read_avc(outFile, reg_data_g, reg_data_d, "ReadData")
            else:
                reg_or_data_read_avc(outFile, reg_data_g, reg_data_d, "DigCap", 1)
            stop_condition_avc(outFile)
    footer_avc(outFile)
    outFile.close()

    print(f'Output File : {out_file}')

if __name__ == '__main__':
    
    if(len(sys.argv) != 3):
        print("useage : ")
        print(f'python {sys.argv[0]} Project P2T_state_file')
        exit(1)
    
    cur_path = os.path.abspath(os.getcwd())
    project_name = sys.argv[1].upper()
    p2t_state_file = os.path.basename(sys.argv[2])
    p2t_state_file_full_path = os.path.abspath(p2t_state_file)

    run(p2t_state_file_full_path, project_name)
    