import tkinter
from tkinter import *
import time
import datetime
import pyaudio
import socket
import threading
import os

dir_path = os.path.dirname(os.path.realpath(__file__))+'\\elec.ico'


master = Tk()
master.iconbitmap(r'{}'.format(dir_path))
master.geometry('500x250')
master.title('Electors Sender App')
master.configure(background='orange')

ip_host = StringVar(master=master)
ip_port = IntVar(master=master)
emergencyVar = BooleanVar(master)
liveVar = BooleanVar(master)
bellVar = BooleanVar(master)
stopFlagVar = BooleanVar(master)
isConnected = StringVar(master)
#------------------------------------------------------------------------------------------------------------------------
pausing = False

is_live = False

class Live_Client(object):
    def __init__(self, ip, port):
        super(Live_Client, self).__init__()
        self.ip = ip
        self.port = port
        self.frames = []
        self.addresses = (self.ip, self.port)
        self.resume_playing()
        FORMAT = pyaudio.paInt16
        CHUNK = 1024
        self.chunk = CHUNK
        CHANNELS = 2
        RATE = 44100
        datetime.datetime.now().strftime("%H:%M:%S.%f")
        self.Audio = pyaudio.PyAudio()
        self.stream = self.Audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK,
                            )
        self.AudioThread = threading.Thread(target=self.record,daemon=True)
        self.udpThread = threading.Thread(target=self.udpStream, daemon=True)
        self.AudioThread.start()
        self.udpThread.start()
        
    def udpStream(self):
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.z1 = udp
        while True:
            if pausing:
                break
            while True:
                if pausing:
                    break
                if len(self.frames) > 0:
                    frames_mod = self.frames.pop(0)
                    self.z1.sendto(frames_mod, self.addresses)
        print("closing socket")
        udp.close()

    def record(self):
        while True:
            if pausing:
                break
            self.frames.append(self.stream.read(self.chunk))
        print("closing recording")
        self.stream.stop_stream()
        self.stream.close()
        self.Audio.terminate()

    def stop_playing(self):
        global pausing
        pausing = True

    def resume_playing(self):
        global pausing
        pausing = False
#------------------------------------------------------------------------------------------------------------------------
class sender_gui(object):
    def __init__(self):
        super(sender_gui,self).__init__()
        self.f = "name.txt"
        
        self.b0 = Button(text="Settings", fg='black', bg="white", relief='solid', font=('arial', 8, 'bold'), width='6',
                    height='1', command=self.show_settings)
        self.b1 = Button(master, text='Emergency Alarm', command=self.alarm, fg='black', bg='white', relief='solid',
                    width=20,
                    font=('arial', 19, 'bold'))
        # b2 = Button(master, text="Browse", command=self.browse_button, fg='black', bg="white", relief='solid', width=6,
        #             font=('arial', 12, 'bold'), height=2)
        self.b3 = tkinter.Button(master, text='Live Anouncement', command=self.live, fg='black', bg='white', relief='solid',
                    width=20,
                    font=('arial', 19, 'bold'))
        self.b4 = tkinter.Button(master, text='Stop', command=self.stop, fg='black', bg='white', width=12,
                    font=('arial', 10, 'bold'))
        self.b5 = Button(master, text='Hourly Bell', command=self.bell, fg='black', bg='white', relief='solid', width=20,
                    font=('arial', 19, 'bold'))
        
        self.b0.place(x=0, y=0)
        self.b1.place(x=90, y=10)
        # b2.place(x=415, y=10)
        self.b3.place(x=90, y=150)
        self.b4.place(x=280, y=215)
        self.b5.place(x=90, y=80)

        self.b3['state'] = 'disabled'
        self.b1['state'] = 'disabled'
        self.b5['state'] = 'disabled'
        isConnected.set('Not yet Connected!')
        ip_host.set('0.0.0.0')
        ip_port.set(8080)
        self.show_clk()
        mainloop()
        

    def show_settings(self):
        self.top = tkinter.Toplevel(master=master)
        self.top.iconbitmap(r'{}'.format(dir_path))
        L1 = Label(self.top, text="IP Address: ", font=('arial', 10, 'bold'), bg='orange')
        L1.place(x=25, y=10)
        L2 = Label(self.top, text="Port Address: ", font=('arial', 10, 'bold'), bg='orange')
        L2.place(x=25, y=50)
        L3 = Label(self.top, textvariable=isConnected, bg='white', fg='blue' )
        L3.place(x=30, y=100)
        E1 = Entry(self.top, bd=5, textvariable=ip_host, )
        E1.place(x=130, y=10)
        E2 = Entry(self.top, bd=5, textvariable=ip_port)
        E2.place(x=130, y=50)
        set_button = Button(self.top, text='Set', command=self.connect_ip, fg='black', bg='white', relief='solid',
                            width=6, height=2,
                            font=('arial', 10, 'bold'))
        set_button.place(x=210, y=90)
        self.top.geometry('340x150')
        self.top.configure(background='orange')
        self.top.title("Settings")
        self.top.mainloop()

    def connect_ip(self):
        host = ip_host.get()
        port = ip_port.get()
        threading.Thread(target=self.init_connect, args=(host,port,), daemon=True).start()


    def init_connect(self, host, port):
        print("Connecting at IP address: "+host+"   Port: "+str(port))
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
        except:
            print("Connection unsuccessful. Try again")
            self.off_limit_button()
        else:
            print("Connected at IP adress: "+host+"   Port: "+str(port))
            self.top.withdraw()
            self.check_connection()

    def check_connection(self):
        if liveVar:
            self.b3['state'] = 'normal'
        if emergencyVar:
            self.b1['state'] = 'normal'
        if bellVar:
            self.b5['state'] = 'normal'
        isConnected.set('Connected successfully!')

    def off_limit_button(self):
        self.b3['state'] = 'disabled'
        self.b1['state'] = 'disabled'
        self.b5['state'] = 'disabled'
        isConnected.set('Failed to connect! Try again')



    def show_clk(self):
        self.clock = Label(master, font=('arial', 10, 'bold'), fg='black', bg='white', width=12)
        self.clock.place(x=120, y=215)
        self.time1()

    def time1(self):
        timenow = time.strftime('%H:%M:%S %p')
        self.clock.config(text=timenow)
        self.clock.after(200, self.time1)

    def exit1(self):
        exit()

    def stop(self):
        global pausing, is_live
        pausing = True
        MESSAGE1 = 'stop'
        self.sock.send(bytes(MESSAGE1, 'ascii'))
        if is_live:
            self.b3['state'] = 'disabled'
            is_live = False
        threading.Thread(target=self.disable_timer, daemon=True).start()
        
        
    def disable_timer(self):
        i = 0
        sec = 5
        while i < sec:
            time.sleep(1)
            i += 1
        self.b3['state'] = 'normal'
        

    def alarm(self):
        global pausing
        pausing = True
        MESSAGE2 = 'alarm'
        self.sock.send(bytes(MESSAGE2, 'ascii'))
        time.sleep(0.1)


    def bell(self):
        global pausing
        pausing = True
        MESSAGE3 = 'bell'
        self.sock.send(bytes(MESSAGE3, 'ascii'))
        time.sleep(0.1)

    def live(self):
        ip = ip_host.get()
        port = ip_port.get()
        global is_live
        is_live = True
        MESSAGE3 = 'live'
        self.sock.send(bytes(MESSAGE3, 'ascii'))
        self.b3['state'] = 'disabled'
        Live_Client(ip, port)
        time.sleep(0.1)
        
#------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    run1 = sender_gui()
