#!/usr/bin/env python
# -*- coding: gbk -*- 
import uuid
import json
import re
import string
import time

from fabric.api import cd
from fabric.api import env
from fabric.api import put
from fabric.api import get
from fabric.api import run
from fabric.api import sudo
from fabric.context_managers import settings
from fabric.contrib.console import confirm
from fabric.tasks import execute
from fabric.utils import abort


def get_settings():
    with open("server.conf") as config:
        return json.load(config)

def get_serverconf():
    config = get_settings()
    return config["Servers"]

servers = get_serverconf()

zone = ""

jarname = ""

server_dir = ""

ss = servers[0]

def getConfig(count):
    global ss
    global zone
    global jarname
    global server_dir
   
    ss = servers[count]
    sendhosts = ss["user"] + "@" + ss["ip"]
    sendpwd = ss["password"]
    
       
    print "sendhosts", sendhosts
    print "sendpwd", sendpwd
    
    env.hosts = [sendhosts]
    env.password = sendpwd
    zone = ss["target"]
    jarname = ss["jarname"]
    server_dir = ss["server_dir"]
  
    
def put_task(): 
    
    try:
    
        targetpath = zone + "/" + server_dir
        sudo("mkdir -p " + targetpath)
        
        try:
           
            with cd(targetpath):  
                with settings(warn_only=True):
                
                    pathstr = ""
                
                    while 1:
                        print "��ǰĿ¼���ļ���:\n"
                        pathstr = run("ls -F | grep '/$'")
                        inputls = raw_input("���� 1.����Ŀ¼ 2.ɾ��Ŀ¼ \n����Enter������:\n")
                        if inputls == "":
                            break
                        if inputls == "1":
                            inputnewpath = raw_input("�����µ�Ŀ¼:\n")
                            run("mkdir -p " + inputnewpath)
                        if inputls == "2":
                            inputnewpath = raw_input("��Ҫɾ���ľ�Ŀ¼��:\n")
                            run("rm -R " + inputnewpath)
                
                    pathlist = re.split("/\r\n|/", pathstr)
                    
                    print "pathlist:", pathlist
                
                    input_upstream = raw_input("������Ҫ�ϴ���Ŀ¼��:\n" + pathstr + "\n����Enter���ϴ��������ļ���")
                
                    if input_upstream == "":
                        result = put(server_dir + ".tar.gz", server_dir + ".tar.gz")
                        run("tar -zxvf " + server_dir + ".tar.gz")
                        count = 1;
                        for plist in pathlist:
                            print "upstream dir:" , plist
                            if string.strip(plist) == "":
                                continue
#                             ����jar��
                            if count == 1: 
                                count = count + 1
                                sudo("mkdir -p " + plist + "/backupjar")
                                run("find " + targetpath + "/" + plist + "/backupjar/* " + "-mtime +7 -name \"*\" -exec rm -rf {} \;")                              
                                
                                x = time.localtime()
                                t = time.strftime('%Y-%m-%d_%H:%M:%S', x)
                                run("cp -Rp " + plist + "/" + jarname + " " + plist + "/backupjar/" + jarname + "." + t)                              
                                    
                                
                            run("cp -Rp " + server_dir + "/* " + plist + "/")
                    elif  input_upstream in pathlist:
                        print "upstream dir:" , input_upstream
                        result = put(server_dir + ".tar.gz", server_dir + ".tar.gz")
                        run("tar -zxvf " + server_dir + ".tar.gz")
                        run("cp -Rp " + server_dir + "/* " + input_upstream + "/")
            if result.failed and not confirm("put file failed, Continue[Y/N]?"): 
                abort("Aborting file put task!")  
        finally:
            run("rm -R " + targetpath + "/" + server_dir + ".tar.gz")
            run("rm -R " + targetpath + "/" + server_dir)
    
    except:
        print "put error..."
    

def task_javaprogram():  
    
    
        targetpath = zone + "/" + server_dir
        
        try:
           
            with cd(targetpath):  
                with settings(warn_only=True):
                   
                    pathstr = run("ls -F | grep '/$'")   
                    pathlist = re.split("/\r\n|/", pathstr)
                    print "��ǰĿ¼:"
                    for ll in pathlist:
                        if string.strip(ll) == "":
                                continue
                        run("ls " + ll + "/*.jar")
                    
                    run(" kill -9 $(ps -ef | grep " + jarname + " | grep -v 'grep' | awk '{print $2}')")
                    print "killed pid..."                  
                    
                    print "restarting......"
                    for ll in pathlist:
                        if string.strip(ll) == "":
                                continue
                        strjar = run("ls " + ll + "/" + jarname)
                        if strjar.endswith(jarname):
                            with cd(ll + "/"):
                                sudo("chmod -R 777 start.sh")
                                sudo("./start.sh")
#                     for ll in pathlist:
#                         if string.strip(ll) == "":
#                                 continue
#                         strjar = run("ls " + ll + "/" + jarname)
#                         if strjar.endswith(jarname):
#                             with cd(ll + "/"):
#                                 time.sleep(3)
#                                 run("tail nohup.out")
                                     
#                     result = run("./start.sh") 
#                     print result 
        except:
            print "restart error..."

          
def upstream():
    
    try:
        
        str1 = "���� 0:�����ϼ�\n"
        ct = 1
        serverlist = []
        for sv in servers:
            str1 = str1 + str(ct) + ":" + str(sv["name"]) + "\n"
            serverlist.append(str(ct))
            ct = ct + 1
     
        while 1:
            input_A = raw_input(str1)
            if str(input_A) == ("0"):
                break
            if  str(input_A) not in serverlist:
                continue
            print "continue"
            getConfig(int(input_A) - 1)
            execute(put_task)
    except:
        print "upstream error..."

def restart():
    try:
        
        str1 = "���� 0:�����ϼ�\n"
        ct = 1
        serverlist = []
        for sv in servers:
            str1 = str1 + str(ct) + ":" + str(sv["name"]) + "\n"
            serverlist.append(str(ct))
            ct = ct + 1
        while 1:
            input_A = raw_input(str1)
            if str(input_A) == ("0"):
                break
            if  str(input_A) not in serverlist:
                continue
            print "continue"
            getConfig(int(input_A) - 1)
            execute(task_javaprogram)  
    except:
        print "restart error..."
      
    
def testStart():
    try:
        
        str1 = "���� 0:�����ϼ�\n"
        ct = 1
        serverlist = []
        for sv in servers:
            str1 = str1 + str(ct) + ":" + str(sv["name"]) + "\n"
            serverlist.append(str(ct))
            ct = ct + 1
        while 1:
            input_A = raw_input(str1)
            if str(input_A) == ("0"):
                break
            if  str(input_A) not in serverlist:
                continue
            print "continue"
            getConfig(int(input_A) - 1)
            execute(startDemo)  
    except:
        print "restart error..."

def startDemo():
    
    with cd("/mydata/sdkserver/bin"):
        run("pwd")
        run("ls")
        sudo("chmod -R 777 start.sh")
        sudo("./start.sh")
        time.sleep(10)
        get("nohup.out", uuid.uuid4() + "nohup.out") 
        
def runcmd():
    
    input_A = raw_input("��������:")
    run(input_A);  
        
def testRunCmd():
    
    try:
        
        str1 = "���� 0:�����ϼ�\n"
        ct = 1
        serverlist = []
        for sv in servers:
            str1 = str1 + str(ct) + ":" + str(sv["name"]) + "\n"
            serverlist.append(str(ct))
            ct = ct + 1
        while 1:
            input_A = raw_input(str1)
            if str(input_A) == ("0"):
                break
            if  str(input_A) not in serverlist:
                continue
            print "continue"
            getConfig(int(input_A) - 1)
            execute(runcmd)  
    except:
        print "run error..."

if __name__ == "__main__":
    
#     execute(host_type)
    
    
#     testStart()
    
#     testRunCmd();

    input_start = ""
    while 1:
        input_start = raw_input("Entert:\n1:�ϴ���Ŀ\n2:���²���\n")
        if str(input_start) == "1":
            upstream()
        if str(input_start) == "2":
            restart()
            
      

#     execute(get_version)

#       execute(task_javaprogram)
      
    



