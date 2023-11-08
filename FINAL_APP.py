from pywinauto import Application
import tkinter as tk
from tkinter import font
import psutil
import csv
import threading
import time 
from PIL import ImageGrab
import os
import socket 
import sys 
FT = time.localtime()
FT = time.strftime("%H:%M:%S",FT).replace(':','_')
FILE = f"FILE {FT}.csv" 
SYS_FILE = 'APPLOCK.lock' 
def start_monitoring():
    global monitoring  
    monitoring = True
    label.config(text="Application Started", font=custom_font)
    with open(FILE, mode='w', newline='') as file_obj:
        writer = csv.writer(file_obj)
        header = ['Process ID', 'Process Name', 'Status', 'CPU Usage (%)', 'Memory Usage (MB)','Browser Tab']
        writer.writerow(header)

    def monitor_processes():
        count = 0
        url = 'None'
        while monitoring:
            process_list = psutil.process_iter()
            with open(FILE, mode='a', newline='') as file_obj:
                writer = csv.writer(file_obj)
                try:
                    app = Application(backend='uia')
                    app.connect(title_re=".*Chrome.*")
                    element_name="Address and search bar"
                    dlg = app.top_window()
                    url = dlg.child_window(title=element_name, control_type="Edit").get_value()
                except:
                    pass
                for process in process_list:
                    try:
                        process_info = process.as_dict(attrs=['pid', 'name', 'status', 'cpu_percent', 'memory_info']) 
                        if count == 0:
                            data = [
                            process_info['pid'],
                            process_info['name'],
                            process_info['status'],
                            process_info['cpu_percent'],
                            process_info['memory_info'].rss / (1024 * 1024),
                            url
                            ]
                        else:
                            data = [
                            process_info['pid'],
                            process_info['name'],
                            process_info['status'],
                            process_info['cpu_percent'],
                            process_info['memory_info'].rss / (1024 * 1024),
                            ] 
                        writer.writerow(data)
                    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                        pass
                    count = count +1
            root.update()
            time.sleep(30)
            count = 0
    
    def Save_Screen():
        while monitoring:
            screenshot = ImageGrab.grab()
            now = time.localtime()
            current_time = time.strftime("%H:%M:%S",now).replace(':','_')
            current_time = str(current_time)
            screenshot.save('SS' + current_time +'.jpg')
            time.sleep(300)
    
    
    monitoring_thread = threading.Thread(target=monitor_processes)
    monitoring_thread.daemon = True
    monitoring_thread.start()
    monitoring_thread1 = threading.Thread(target=Save_Screen)
    monitoring_thread1.daemon = True 
    monitoring_thread1.start()
    
# Function to stop monitoring processes
def stop_monitoring():
    global monitoring
    monitoring = False
    global label 
    label.config(text="Application Stopped", font=custom_font)


def exit_application():
    os.remove(SYS_FILE)
   # server_socket.close()
    root.destroy()

# Initialize the Tkinter window
def Started():
    global label
    global custom_font
    global root  
    root = tk.Tk()
    root.title("Process Monitor")
    x = (root.winfo_screenwidth() - 600)//2
    y = (root.winfo_screenheight() - 450)//2
    root.geometry(f'{600}x{550}+{x}+{y}')
    root.overrideredirect(1) 
    root.attributes("-topmost", True)
    root.attributes("-disabled",False)
    custom_font = font.Font(family="Helvetica", size=12, weight="bold", slant="italic")
    monitoring = False

    # Create GUI elements
    label = tk.Label(root, text='', font=custom_font)
    label.pack(pady=20)

    start_button = tk.Button(root, text="Start Application",padx=30,pady=30 ,font=custom_font, command=start_monitoring,activebackground='#0FFFF0')
    start_button.pack(pady=10)

    stop_button = tk.Button(root, text="Stop Application",padx=30,pady=30, font=custom_font, command=stop_monitoring,activebackground='#0FFFF0')
    stop_button.pack(pady=10)

    Hide_Button = tk.Button(root,text='Hide App',padx=58,pady=30, font=custom_font, command=Hide_Window,activebackground='#0FFFF0')
    Hide_Button.pack(pady=10)
    quit_button = tk.Button(root,text='Quit',padx=78,pady=30, font=custom_font, command=exit_application,activebackground='#0FFFF0')
    quit_button.pack(pady=10)
    
    def show_window():
       server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       server_socket.bind(('localhost', 12345))
       server_socket.listen(5)
       while True:
           client_socket, address = server_socket.accept()
           data = client_socket.recv(1024)
           if data.decode('utf-8') == 'Exit':
              root.deiconify()
       server_socket.close()
    temp_thread = threading.Thread(target=show_window)
    temp_thread.daemon = True 
    temp_thread.start()
    root.mainloop()
# Run the Tkinter main loop
def Hide_Window():
    root.withdraw()
def is_app_not_running():
    if not os.path.exists(SYS_FILE):
        with open(SYS_FILE,'w') as FILE_OBJ:
            FILE_OBJ.write("App has started!")
        return True
def Release_Window():

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = ('localhost', 12345)

    client_socket.connect(server_address)

    message = "Exit"
    client_socket.send(message.encode())

    client_socket.close()
    sys.exit()

if __name__=='__main__':
    if is_app_not_running():
        Started()
    else:
        Release_Window()
