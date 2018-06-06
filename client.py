from socket import *
from select import *
from time import sleep
from winsound import Beep
from Tkinter import *
import thread

###
### FUNCTIONS
###

#
## server functions
#

def create_client(): 
    client = socket(AF_INET,SOCK_STREAM)
    addr = ('localhost',int(read_port()))
    client.connect(addr)   
    return client
    
def read_port(): # reads the updated server's port
    f = open('information.txt','rb')
    port = f.readline()
    f.close()
    return port


def send_server(client): # send the entry's data to server
    data = command_line.get()
    if data:
        client.send(data)
        
def recv_server(client, addr): # ready to print any data from server
    global client_closed
    BUFFSIZ = 1024
    while not client_closed:
        data = client.recv(BUFFSIZ)
        if data == 'server is shutting down': # if the server is closing, close client as well
            client_closed = True
            send_btn['state'] = DISABLED
        if 'Beep' in data and 'sleep' in data: # if the data is music
            try: # try to play music
                exec(data)
            except: # if the client was so smart to send echo with the words beep and sleep in it, print the data... 
                show_massage(data)
        else: # print server reply
            show_massage(data)
    try: # the server is closed, disable the send button
        send_btn['state'] = DISABLED
    except:
        pass

        
def exit_server(client): # close the client and inform the server
    global client_closed
    data = 'exit'
    client.send(data)
    client_closed = True
    client.close()
    root.destroy()
    
#
## tkinter functions
#


def show_massage(massage): # shows the server's reply in listbox
    try:
        screen.insert(END,massage)
        screen.see(END)
    except:
        pass

###
### MAIN
###

    
client_closed = False
client = create_client()
thread.start_new_thread(recv_server,(client,'str')) # immediately tells the socket to expect data

            ### root's design ###

root = Tk()
root.title("Rozval's server")
bg_color = "#%02x%02x%02x" % (106, 150, 221) 
root["background"] = bg_color
fnt = ("Arial", 16)

scroll_bar = Scrollbar(root)
screen = Listbox(root,yscrollcommand = scroll_bar.set,width = 60,height = 15,font = fnt) # main screen
scroll_bar.config(command = screen.yview)
screen.grid(columnspan = 3)
scroll_bar.grid(row = 0,column = 3,rowspan = 3,sticky = N + S)

command_line = Entry(root,font = fnt)
command_line.grid(row = 1,columnspan = 3,sticky = W + E)

send_btn = Button(root,text = 'Send',font = fnt,command = lambda:send_server(client))
send_btn.grid(row = 2,column = 0,sticky = W + E)

exit_btn = Button(root,text = 'Exit',font = fnt,command = lambda:exit_server(client))
exit_btn.grid(row = 2,column = 2,sticky = W + E)




root.mainloop()
    
        










































