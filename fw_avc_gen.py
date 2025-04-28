import os
import sys
from Lib_Common import data_sort_FW, header_avc, start_condition_avc, slave_addr_avc, reg_or_data_avc, stop_condition_avc, footer_avc, Prod_Info

def run(fw_file, project):

    prod = Prod_Info(project)
    if(prod.is_valid == 0):
        print("Error!!")
        exit(1)

    Script_File = os.path.basename(__file__)
    temp = os.path.splitext(fw_file)[0]
    out_file = f'{temp}.avc'

    outFile = open(out_file, "w")
    inFile = open(fw_file, mode="r", encoding="utf-8")

    fw_data = data_sort_FW(inFile)
    inFile.close()

    dut_slave_addr = prod.Dut_Slave_Address()
    gold_slave_addr = prod.Gold_Slave_Address()
    
    header_avc(outFile, Script_File, fw_file, out_file)

    for line in range(len(fw_data)):
        reg_addr = fw_data[line]["reg"]
        reg_data_g = fw_data[line]["data"]
        reg_data_d = reg_data_g
        start_condition_avc(outFile)
        slave_addr_avc(outFile, gold_slave_addr, dut_slave_addr)
        reg_or_data_avc(outFile, reg_addr, reg_addr, "RA")
        reg_or_data_avc(outFile, reg_data_g, reg_data_d, "Data")
        stop_condition_avc(outFile)
    footer_avc(outFile)
    outFile.close()
    print(f'Output File : {out_file}')

    # FW Burst File generation #################################################################
    temp = os.path.splitext(fw_file)[0]
    out_file = f'{temp}_Burst.avc'
        
    outFile = open(out_file, "w")
    inFile = open(fw_file, mode="r", encoding="utf-8")

    first_addr_done = 0

    header_avc(outFile, Script_File, fw_file, out_file)

    for line in range(len(fw_data)):
        reg_addr = fw_data[line]["reg"]
        reg_data_g = fw_data[line]["data"]
        reg_data_d = reg_data_g
        if(first_addr_done == 0):
            start_condition_avc(outFile)
            slave_addr_avc(outFile, gold_slave_addr, dut_slave_addr)
            reg_or_data_avc(outFile, reg_addr, reg_addr, "RA")
            reg_or_data_avc(outFile, reg_data_g, reg_data_d, "Data")
            first_addr_done = 1
        else:
            reg_or_data_avc(outFile, reg_data_g, reg_data_d, "Data")
    
    stop_condition_avc(outFile)
    footer_avc(outFile)
    outFile.close()
    print(f'Output File : {out_file}')

if __name__ == '__main__':
    
    if(len(sys.argv) != 3):
        print("useage : ")
        print(f'python {sys.argv[0]} Project P2T_FW_file')
        exit(1)
        
    cur_path = os.path.abspath(os.getcwd())
    project_name = sys.argv[1].upper()
    p2t_fw_file = os.path.basename(sys.argv[2])
    p2t_fw_file_full_path = os.path.abspath(p2t_fw_file)

    run(p2t_fw_file_full_path, project_name)
    