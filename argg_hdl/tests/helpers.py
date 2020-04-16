from filecmp import dircmp
import os
import shutil

from argg_hdl import *

def compare_folders(FolderA,FolderB):
    dcmp = dircmp(FolderA, FolderB) 
    return dcmp

def Folders_isSame(FolderA,FolderB):
    dcmp =   compare_folders(FolderA,FolderB)
    return isSame(dcmp)

def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print("diff_file %s found in %s and %s"% (name, dcmp.left,
            dcmp.right))
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)

def isSame(dcmp,message="\n\n====================\n"):
    ret = True
    if dcmp.right_only:
        ret = False
        message += "Missing files "+ str(dcmp.right_only) +"\n"
    
    if dcmp.left_only:
        ret = False
        message += "Additional files "+ str(dcmp.left_only) +"\n"


    if dcmp.diff_files:
        ret = False
        for name in dcmp.diff_files:
            message += "diff_file "+ str(name) +"\n"

    
    for sub_dcmp in dcmp.subdirs.values():
        if not isSame(sub_dcmp,message):
            ret = False
    return ret, message


def mkdir_if_not_exist(path):
    try:
        os.mkdir(path)
    except:
        pass

def vhdl_conversion(func):
    def wrap(OutputPath):
        g_global_reset()
        mkdir_if_not_exist(OutputPath)
        mkdir_if_not_exist(OutputPath+"/output")
        mkdir_if_not_exist(OutputPath+"/reference")
        mkdir_if_not_exist(OutputPath+"/temp")

        print_cnvt_set_file(OutputPath+ "/output/"+"/printout.txt")
        tb = func(OutputPath)
        convert_to_hdl(tb, OutputPath+ "/output")
        print_cnvt_set_file()

        return Folders_isSame(OutputPath+"/output", OutputPath+'/reference') 
    
    return wrap


def do_simulation(func):
    def wrap(OutputPath):
        mkdir_if_not_exist(OutputPath)
        mkdir_if_not_exist(OutputPath+"/output")
        mkdir_if_not_exist(OutputPath+"/reference")
        mkdir_if_not_exist(OutputPath+"/temp")

        g_global_reset()
        with open(OutputPath+"/output"+"/data.txt","w") as f:
            tb = func(OutputPath,f)
            run_simulation(tb, 3000,OutputPath+"/temp/"+"data.vcd")
        
        return Folders_isSame(OutputPath+"/output", OutputPath+'/reference') 

    return wrap

def remove_old_files():
    root, dirs, files = next(os.walk('tests/'))


    for d in dirs:
        path_output = os.path.join(root, d, "output")
        shutil.rmtree(path_output,ignore_errors=True)
        mkdir_if_not_exist(path_output)

        path_temp = os.path.join(root, d, "temp")
        shutil.rmtree(path_temp,ignore_errors=True)
        mkdir_if_not_exist(path_temp)