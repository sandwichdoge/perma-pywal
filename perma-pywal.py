#!/bin/python3
import pathlib
import re
import subprocess


'''
WHAT IS THIS?
>This will make your pywal color scheme permanent so you don't have to call it in .bashrc
>To improve startup time for your terminal

IMPORTANT
>You need to run wal to change your colors first before running this script
>It's best to run this on an already working terminal config, this will not magically fix your broken terminal

SUPPORTED TERMINALS SO FAR:
xfce-terminal, urxvt
'''


def fcopy(src, dst):
    f1 = open(src, "r")
    f2 = open(dst, "w")
    f2.write(f1.read())
    f1.close()
    f2.close()


def is_urxvt_color_conf_line(line):
    p = re.compile(r'\x2A\x2Ecolor(\d+)\x3A')
    oRE = p.findall(line)
    if (oRE): return oRE[0]
    return None


#Apply configs and refresh terminal if possible
def apply_configs(terminal):
    if (terminal == "urxvt"):
        subprocess.call("xrdb", HOMEDIR + "/.Xdefaults")
    elif (terminal == "gnome-terminal"):
        sub_in = open("gterm_conf.txt", "r")
        subprocess.Popen(["dconf", "load", "/org/gnome/terminal/"], stdin = sub_in)
        sub_in.flush()
        sub_in.close()
    #equalivalent to dconf load /org/gnome/terminal/ < gterm_conf.txt
    #https://askubuntu.com/questions/967517/backup-gnome-terminal



TERMINAL = "gnome-terminal"
HOMEDIR = str(pathlib.Path.home())

pywal_conf = open(HOMEDIR + "/.cache/wal/colors", "r")
colors_str = str(pywal_conf.read())
pywal_conf.close()

color_list = colors_str.splitlines()
total = len(color_list)

if TERMINAL == "xfce-terminal":
    #XFCE-terminal
    fcopy(HOMEDIR + "/.config/xfce4/terminal/terminalrc", HOMEDIR + "/.config/xfce4/terminal/terminalrc.bak")

    with open(HOMEDIR + "/.config/xfce4/terminal/terminalrc", "r") as conf_fd:
        content = conf_fd.read()

    conf_fd = open(HOMEDIR + "/.config/xfce4/terminal/terminalrc", "w+")
    new_palette = "ColorPalette=" + ";".join(color_list)

    lines = content.splitlines()
    for i in range(len(lines)):
        if (lines[i][:len("ColorPalette")] == "ColorPalette"):
            lines[i] = new_palette
        elif (lines[i][:len("ColorForeground=")] == "ColorForeground="):
            lines[i] = "ColorForeground=" + color_list[len(color_list)-1]
        elif (lines[i][:len("ColorBackground=")] == "ColorBackground="):
            lines[i] = "ColorBackground=" + color_list[0]
            

elif TERMINAL == "urxvt":
    #urxvt
    fcopy(HOMEDIR + "/.Xdefaults", HOMEDIR + "/.Xdefaults.bak")

    with open(HOMEDIR + "/.Xdefaults", "r") as conf_fd:
        content = conf_fd.read()
    
    conf_fd = open(HOMEDIR + "/.Xdefaults", "w+")

    lines = content.splitlines()
    for i in range(len(lines)):
        #print("li", lines[i][:len("*.color" + str(i)) -1], i)
        color_no = is_urxvt_color_conf_line(lines[i])
        if (color_no):
            lines[i] = "*.color" + color_no + ":" + color_list[int(color_no)]
        elif (lines[i][:len("*.foreground:")] == "*.foreground:"):
            lines[i] = "*.foreground:" + color_list[len(color_list)-1]
        elif (lines[i][:len("*.background:")] == "*.background:"):
            lines[i] = "*.foreground:" + color_list[0]


elif TERMINAL == "gnome-terminal":
    #gnome-terminal

    #dconf dump /org/gnome/terminal/
    content = subprocess.check_output(["dconf", "dump", "/org/gnome/terminal/"])
    if not content: exit()

    conf_fd = open("gterm_conf.txt", "w+")
    new_palette = "palette=['" + "', '".join(color_list) + "']"

    lines = content.splitlines()
    for i in range(len(lines)):
        lines[i] = lines[i].decode("utf-8")
        if (lines[i][:len("palette=[")] == "palette=["):
            lines[i] = new_palette



new_conf = "\n".join(lines)
conf_fd.write(new_conf)
conf_fd.close()

apply_configs(TERMINAL) #apply configs and possibly refresh terminal settings


print("Done")