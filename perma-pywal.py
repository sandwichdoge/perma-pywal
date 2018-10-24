#!/bin/python3
import pathlib
import re
import subprocess
from os import path


'''
WHAT IS THIS?
>This will make your pywal color scheme permanent so you don't have to call it in .bashrc
>To improve startup time for your terminal

IMPORTANT
>You need to run wal to change your colors first before running this script
>It's best to run this on an already working terminal config, this will not magically fix your broken terminal

SUPPORTED TERMINALS SO FAR:
xfce-terminal, urxvt, gnome-terminal, terminator
'''


def fcopy(src, dst):
    f1 = open(src, "r")
    f2 = open(dst, "w")
    f2.write(f1.read())
    f1.close()
    f2.close()


#[urxvt]return color number if it's a color config line
def is_urxvt_color_conf_line(line):
    p = re.compile(r'\x2A\x2Ecolor(\d+)\x3A') #*.color0
    oRE = p.findall(line)
    if (oRE): return oRE[0]
    return None


#Apply configs and reload terminal if possible
def apply_configs(terminal):
    if (terminal == "urxvt" or terminal == "xterm"):
        subprocess.call("xrdb", HOMEDIR + "/.Xresources")
    elif (terminal == "gnome-terminal"):
        sub_in = open("gterm_conf.txt", "r")
        subprocess.Popen(["dconf", "load", "/org/gnome/terminal/"], stdin = sub_in)
        sub_in.flush()
        sub_in.close()
    #equalivalent to dconf load /org/gnome/terminal/ < gterm_conf.txt
    #https://askubuntu.com/questions/967517/backup-gnome-terminal



#MAIN
SUPPORTED_TERMINALS = ["xfce4-terminal", "urxvt", "xterm", "gnome-terminal", "terminator"]
HOMEDIR = str(pathlib.Path.home())


USER_TERMINALS = list()
for t in SUPPORTED_TERMINALS:
    out = subprocess.check_output(["whereis", t]).decode("utf-8")
    if (out != t+':'+'\n'): USER_TERMINALS.append(t)
    
print("Detected terminals:", USER_TERMINALS)


pywal_conf = open(HOMEDIR + "/.cache/wal/colors", "r")
colors_str = str(pywal_conf.read())
pywal_conf.close()

color_list = colors_str.splitlines()
total = len(color_list)
#print(color_list)

for TERMINAL in USER_TERMINALS:
    print("Configuring", TERMINAL)

    if TERMINAL == "xfce4-terminal":
        #XFCE-terminal
        config_path = HOMEDIR + "/.config/xfce4/terminal/terminalrc"
        if not path.exists(config_path):
            print("Error. Config file", config_path, "does not exist.")
            continue

        fcopy(config_path, config_path + ".bak")

        with open(config_path, "r") as conf_fd:
            content = conf_fd.read()

        conf_fd = open(config_path, "w+")
        new_palette = "ColorPalette=" + ";".join(color_list)

        lines = content.splitlines()
        for i in range(len(lines)):
            if (lines[i][:len("ColorPalette")] == "ColorPalette"):
                lines[i] = new_palette
            elif (lines[i][:len("ColorForeground=")] == "ColorForeground="):
                lines[i] = "ColorForeground=" + color_list[len(color_list)-1]
            elif (lines[i][:len("ColorBackground=")] == "ColorBackground="):
                lines[i] = "ColorBackground=" + color_list[0]
                

    elif TERMINAL == "urxvt" or TERMINAL == "xterm":
        #urxvt
        config_path = HOMEDIR + "/.Xresources"
        if not path.exists(config_path):
            print("Error. Config file", config_path, "does not exist.")
            continue

        fcopy(config_path, config_path + ".bak")

        with open(config_path, "r") as conf_fd:
            content = conf_fd.read()
        
        conf_fd = open(config_path, "w+")

        lines = content.splitlines()
        for i in range(len(lines)):
            color_no = is_urxvt_color_conf_line(lines[i])
            if (color_no):
                lines[i] = "*.color" + color_no + ":" + color_list[int(color_no)]
            elif (lines[i][:len("*.foreground:")] == "*.foreground:"):
                lines[i] = "*.foreground:" + color_list[len(color_list)-1]
            elif (lines[i][:len("*.background:")] == "*.background:"):
                lines[i] = "*.background:" + color_list[0]


    elif TERMINAL == "gnome-terminal":
        #gnome-terminal
        palette_exists = 0 #whether palette has been set in config file
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
                palette_exists = 1
            elif (lines[i][:len("foreground-color=")] == "foreground-color="):
                lines[i] = "foreground-color='" + color_list[len(color_list)-1] + "'"
            elif (lines[i][:len("background-color=")] == "background-color="):
                lines[i] = "background-color='" + color_list[0] + "'"

        if not palette_exists:
            lines.append(new_palette)
            lines.append("foreground-color='" + color_list[len(color_list)-1] + "'")
            lines.append("background-color='" + color_list[0] + "'")



    elif TERMINAL == "terminator":
        #terminator
        config_path = HOMEDIR + "/.config/terminator/config"
        if not path.exists(config_path):
            print("Error. Config file", config_path, "does not exist.")
            continue

        fcopy(config_path, config_path + ".bak")

        with open(config_path, "r") as conf_fd:
            content = conf_fd.read()

        conf_fd = open(config_path, "w+")
        new_palette = 'palette = "' + ':'.join(color_list) + '"'

        lines = content.splitlines()
        for i in range(len(lines)):
            lines[i] = lines[i].strip(' ')
            if (lines[i][:len('palette = "')] == 'palette = "'):
                lines[i] = new_palette
            elif (lines[i][:len('foreground_color = "')] == 'foreground_color = "'):
                lines[i] = 'foreground_color = "' + color_list[len(color_list)-1] + '"'
            elif (lines[i][:len('background_color = "')] == 'background_color = "'):
                lines[i] = 'background_color = "' + color_list[0] + '"'


    new_conf = "\n".join(lines)
    conf_fd.write(new_conf)
    conf_fd.close()

    apply_configs(TERMINAL) #apply configs and possibly reload terminal settings


print("Done. If there's no effect, try restarting your terminal.")