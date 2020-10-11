import socket
import pickle
import errno
import threading
import tkinter
from tkinter import *
from tkinter import messagebox
import sys


HEADER_LENGTH = 10
IP = "192.168.1.105"
PORT = 1234
protocol = 'utf-8'
global running
running = True

stroot = Tk()
stroot.geometry('150x100')
stroot.title("Welcome")
stroot.resizable(height = False, width = False)
userlbl = Label(text = "Please type in a username")
userentry = Entry(width = 10)
def connect():

    global username
    username = userentry.get()
    global client_socket, running
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        client_socket.setblocking(False)
        stroot.destroy()
    except IOError as e:
        if e.errno == errno.ECONNREFUSED:
            messagebox.showerror('Connect', 'Could not connect')
            print("No connection")
            # sys.exit()
            # running = False

connectbtn = Button(text = "Connect", command = connect)
userlbl.grid(column = 0, row = 0)
userentry.grid(column = 0, row = 1)
connectbtn.grid(column = 0, row = 2)
stroot.mainloop()

username_header = f"{len(username):<{HEADER_LENGTH}}".encode(protocol)
client_socket.send(username_header + username.encode(protocol))

def send():
    message = EntryBox.get("1.0",'end-1c').strip()
    EntryBox.delete("0.0", END)
    if message != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You> " + message + '\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)
    
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode(protocol)
        client_socket.send(message_header + message.encode(protocol))
   
global ChatLog

root = Tk()
root.title(IP)
root.geometry("400x500")
root.resizable(width=FALSE, height=FALSE)
ChatLog = Text(root, bd=0, bg="white", height="8", width="50", font="Arial",)
ChatLog.config(state=DISABLED)
scrollbar = Scrollbar(root, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set
SendButton = Button(root, font=("Verdana",12,'bold'), text="Send", width="5", height=5, bg = "White", command= send )
EntryBox = Text(root, bd=0, bg="white",width="29", height="5", font="Arial")
scrollbar.place(x=376,y=6, height=386)
ChatLog.place(x=6,y=6, height=386, width=370)
EntryBox.place(x=6, y=401, height=90, width=265)
SendButton.place(x=325, y=401, height=40)

def update_chat():
    global running
    while running:
        global ChatLog
        try:
            while True:
                message_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by sever")
                #message_header = message_header.decode(protocol)
                #message_header = message_header.strip()
                message_length = int(message_header.decode(protocol).strip())
                message = client_socket.recv(message_length).decode(protocol)
                ChatLog.config(state=NORMAL)
                ChatLog.insert(END, message + '\n')
                ChatLog.config(foreground="#442265", font=("Verdana", 12 ))
                ChatLog.config(state=DISABLED)
                ChatLog.yview(END)

                print(message)
        
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                if e.errno == errno.ECONNRESET:
                    print("Server closed connection")
                    running = False
                print("Reading Error", str(e))
            
            continue

        except Exception as e:
            print("Genral Error", str(e))
            running = False

updatemsg = threading.Thread(target=update_chat)
updatemsg.start()
root.mainloop()
running = False
sys.exit()