###
### IMPORTING SECTION
###


from socket import *
from select import *
from time import *
from math import *


###
### FUNCTIONS
###

#
## server functions
#

def create_server(): # returns the listening socket and its port
    mainsocket = socket(AF_INET,SOCK_STREAM)
    mainsocket.bind(("localhost",0))
    port = mainsocket.getsockname()[1]
    mainsocket.listen(5)
    return mainsocket, port 

def add_data(massages,socket,data): # adds reply to the last place in queue
    massages[socket].insert(0,data)

def add_data_all(massages,data): # adds urget reply to first place in queue
    for connection in massages: # for each socket
        massages[connection].insert(-1,data)
    
def del_data(massages,socket): # dels data that have already been sent
    massages[socket].pop(-1)

def services(data,socket,massages): # adds the optimal response
    if not valid_input(data): # data isn't interpreted to aany function...
        add_data(massages,socket,'\ninvalid input, try again')
    else:
        info = split_info(data)
        if info[0] == '-e': 
            echo(data,socket,massages)
        else:
            if info[0] == '-c':
                calculator(info[-1],socket,massages)
            elif info[0] == '-t':
                time(socket,massages)
            elif info[0] == '-m':
                music(info[-1],socket,massages)
            elif info[0] == '-h':
                send_help(info[-1],socket,massages)
            elif info[0] == '-s':
                shut_down(info[-1],socket,massages)
            elif info[0] == '-p':
                change_password(info,socket,massages)
            elif info[0] == '-d':
                distance(info,socket,massages)
                
        

#   
## data functions
#

def iliminate_spaces(lst):   
    lst = list(set(lst))
    if lst[0] == '':
        del lst[0]
    return lst

def valid_input(data): # checks if the request is one of the 8 functions
    operands = ['-c','-t','-s','-m','-h','-e','-p','-d']
    info = split_info(data)
    if info[0] in operands:
        return True
    return False

def split_info(data): 
    return str(data).split(' ')

#
## file functions
#

def save_port(port): # write the port for the client
    f = open('information.txt','r+')
    f.write(str(port))
    f.close()

def read_file(index): # read the right song from file by his index
    f = open('information.txt','r+')
    song = f.read().split('*')[int(index)]
    return song

#
## services functions
#   

def calculator(exercise,socket,massages): # returns solved exercise
    try: # tries to solve the exercise
        reply = '\nthe answer is --> %s' % str(eval(exercise)) 
    except:
        reply = '\ninvalid exercise, try again'
    add_data(massages,socket,reply) # adds the reply to the socket's queue


def time(socket,massages): # returns server's time
    now = strftime('%c')   
    reply = "\nCurrent date & time %s" % now
    add_data(massages,socket,reply)

   
def music(index,socket,massages): #  return the requested song by index
    try: # checks for integer
        int(index) 
    except:
        reply = '\ninvalid song number, try again'
    else:
        if 1 <= int(index) <= 3: # checks that index is one of the three songs
            reply = read_file(index)
        else:
            reply = '\ninvalid song number, try again'
    add_data(massages,socket,reply)


def echo(data,socket,massages): # echoes data
    data = data.split(' ')
    data.remove('-e') # removing '-e' from data
    data = ' '.join(data)
    add_data(massages,socket,data)


def send_help(index,socket,massages): # send detailed information about each function
    reply = ["-c [solves exercise ,etc: '-c 234*234']","-c [exercise]","-t [return server's time ,etc:'-t']","-m [plays song, etc:'-m 1']","-m [1-starwars/2-mario/3-happybirthday]","-p [change password, etc:'-p 4512 123']","-p [current password] [new password]","-e [echos, etc:'-e hi']","-e [data to echo]","-h [you already knows what -h does..]","-s [shutdown server, etc:'-s 4512']","-s [server's password]","-d [how far a shooting arrow will get from you, etc:'-d 4 30']","-d [velocity] [angle]"] 
    for r in reply:
        add_data(massages,socket,r)

def change_password(info,socket,massages):
    if len(info) != 3: # search for three parameters
        reply = 'invalid input, try again'
    else:
        current_p = read_file(4) # gets current password from file
        if current_p != info[1]: 
            reply = 'wrong password, try again'
        else: # if the first parameter is the current password, allow the client to change it
            f = open('information.txt','rb+')
            text = f.read().split('*')
            text[4] = info[2] # replace the old password in file
            text = '*'.join(text)
            f.close()
            f = open('information.txt','wb+')
            f.write(text) # writes the new information file
            f.close()
            reply = 'password has changed succesfully'
    add_data(massages,socket,reply)
    
    

def shut_down(key,socket,massages):
    global server_closed
    password = read_file(4) # reads the current password from file
    if key == password: # if the client gave the right password...
        reply = 'server is shutting down'
        add_data_all(massages,reply) # sends the warning to all clients
        server_closed = True
    else:
        reply = 'wrong password, try again'
        add_data(massages,socket,reply)

def distance(info,socket,massages):
    if len(info) != 3: # searches for 3 parameters
        reply = 'invalid input, try again'
    else:
        try: # checks that parameters aren't strings
            float(info[1])
            float(info[2])
        except:
            reply = 'invalid input, try again'        
        else:
            info[1] = float(info[1])
            info[2] = float(info[2])
            if info[1] < 0 or info[2] < 0 or info[2] > 180: # checks that parameters are positive
                reply = 'requirements: speed >= 0, 0 <= theta <= 180'
            else: # calculate the arrow's movement (physics time!)
                v = info[1] # m/s
                theta = info[2]*pi/180 # degree
                g = 10 # m/s^2
                t = v*sin(theta)/g
                d = v*cos(theta)*2*t
                reply = 'the arrow will get to %.2f meters in %.2f seconds' % (d,2*t)
    add_data(massages,socket,reply)
        

    


        
        




###
### MAIN
###

mainsocket, port = create_server()
save_port(port) # saves the new port

inputs = [mainsocket] # adds listening socket to inputs
outputs = []
massages = {}
server_closed = False
BUFFSIZ = 1024
times = {}

while inputs and not server_closed: # while server isn't close
    readables,writeables,exeptions = select(inputs,outputs,inputs + outputs)

    
    for socket in readables:
        if socket is mainsocket: # new connection
            new_client, addr = socket.accept()
            inputs.append(new_client) 
            massages[new_client] = [] # gives the client new 'massages queue'
            times[new_client] = clock() # saves the last time the client was active
            if new_client not in outputs:
                outputs.append(new_client)
            print '%s has connected' % socket
        else: # connected client
            try:
                data = socket.recv(BUFFSIZ)
            except:
                data = 'exit'
            times[socket] = clock() # refresh the last time that the client was active
            if data == 'exit': # deleting client from the input output lists (no data)
                if socket in outputs:
                    outputs.remove(socket)
                if socket in writeables:
                    writeables.remove(socket)
                inputs.remove(socket)
                del massages[socket]
                del times[socket]
                socket.close()
                print '%s has disconnected' % socket
            elif data: # if data, adding the right output to the client's queue
                if socket not in outputs:
                    outputs.append(socket)
                services(data,socket,massages) # 

    for socket in times:
        reply = 'nooooo'
        if clock() - times[socket] > 30: # if the client wasn't active in the last half minute
            add_data(massages,socket,reply)
            times[socket] = clock() # refresh client's active time

    for socket in writeables: 
        if len(massages[socket]) != 0: # if the socket's massaeges queue isn't empty
            data = massages[socket][-1] # sends the first data in queue
            socket.send(data) 
            del_data(massages,socket) # dels the data from queue
            
mainsocket.close()







        
