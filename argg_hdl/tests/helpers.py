from filecmp import dircmp
import os
import shutil

from argg_hdl import *

from argg_hdl.argg_hdl_base import sort_archetecture, set_sort_archetecture
from pathlib import Path


g_globals = {
    "file" : None
}
def printf(out_str):
    if g_globals["file"]:
        g_globals["file"].write(out_str)

def printff(*argv):
    ret = ""
    start = ""
    for arg in argv:  
        ret += start + str(value(arg))
        start = "; "

    printf(ret+'\n')
    
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
    
    left_only_filter = [x for x in dcmp.left_only if x != ".gitignore"]
    if left_only_filter:
        ret = False
        message += "Additional files "+ str(left_only_filter) +"\n"


    if dcmp.diff_files:
        ret = False
        for name in dcmp.diff_files:
            message += "diff_file "+ str(name) +"\n"

    
    for sub_dcmp in dcmp.subdirs.values():
        if not isSame(sub_dcmp,message):
            ret = False
    return ret, message


def mkdir_if_not_exist(FolderName):
    Path(FolderName).mkdir(parents=True, exist_ok=True)


def create_git_ignoreFile_for_folder(FolderName):
    with open(FolderName+".gitignore","w",newline="") as f:
        f.write("*")
    
def vhdl_conversion(func):
    def wrap(OutputPath):
        g_global_reset()
        sort_archetecture_old = sort_archetecture()
        set_sort_archetecture(True)
        mkdir_if_not_exist(OutputPath)
        mkdir_if_not_exist(OutputPath+"/output")
        mkdir_if_not_exist(OutputPath+"/reference")
        mkdir_if_not_exist(OutputPath+"/temp")
        
        create_git_ignoreFile_for_folder(OutputPath+ "/output/")
        print_cnvt_set_file(OutputPath+ "/output/"+"/printout.txt")
        tb = func(OutputPath)
        convert_to_hdl(tb, OutputPath+ "/output")
        print_cnvt_set_file()
        set_sort_archetecture(sort_archetecture_old)
        return Folders_isSame(OutputPath+"/output", OutputPath+'/reference') 
    
    return wrap


def do_simulation(func):
    def wrap(OutputPath, SimulationTime=3000):
        mkdir_if_not_exist(OutputPath)
        mkdir_if_not_exist(OutputPath+"/output")
        mkdir_if_not_exist(OutputPath+"/temp")
        
        create_git_ignoreFile_for_folder(OutputPath+ "/output/")
        g_global_reset()
        with open(OutputPath+"/output"+"/data.txt","w",newline="") as f:
            g_globals["file"] = f
            tb = func(OutputPath,f)
            run_simulation(tb, SimulationTime, OutputPath+"/temp/"+"data.vcd")
        
        g_globals["file"] = None
        
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