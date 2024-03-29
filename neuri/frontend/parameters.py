import tkinter                              as tk
from PIL                                    import Image, ImageTk
from sys                                    import platform
from github                                 import Github
import serial.tools.list_ports
import customtkinter
import os
import socket
import webbrowser

class Parameters:

    def __init__(self):

        super(Parameters, self).__init__()

        self.frontend_path  = os.path.dirname(__file__)

        self.conf_file      = os.path.join(".", "settings.cfg")
        self.version        = '2.82.0' # TO-DO: Find a more elegant way to dynamically define the current version as this line here gets forgotten a lot
        self.ico_neuri      = os.path.join(self.frontend_path, "Neuri_logo.ico")

        # List elements:
        # First =   start code (int)
        #           The start code is the message that will be sent to 
        #           the boards in order to initiate signal transfer and
        #           will also define the samples per message. Might have to
        #           be separated in future
        # Second    Default sampling rate (int, Hz)
        # Third     Baud rate (int)
        self.board_characteristics = {
            "Neuri V1 by Helment":                  [2, 200, 115200],
            "Neuri-Lolin S3-PRO by Helment":        [2, 200, 115200],
            "BioAmp EXG Pill by Upside Down Labs":  [2, 125, 115200]
        }

        self.set_defaults() # Necessary to execute first in case user 
                            # parameter not found in configuration file
        # Loop up user settings
        self.load_parameters()

        # Build relay connection for other programs
        self.build_relay(self.udp_ip)

        self.get_screen_info()
        self.build_frontend()

        # This stops code execution until paramWin closed
        self.paramWin.mainloop()


    def build_relay(self, ip):
        # =================================================================
        # This connection will be used in order to transfer the incoming 
        # signal from the board to a dynamuically defined port via UDP
        # =================================================================

        self.udp_port   = self.search_free_com(ip)
        self.udp_ip     = ip
        self.send_sock  = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        print('Relay connection established at ' + self.udp_ip + ':' + str(self.udp_port))
        print('Use this connection to import signals in your own program!\n')
    

    def search_free_com(self, ip):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for iPort in range(12344, 12350):
            try:
                s = s.connect((ip, iPort))
            except:
                return iPort

        raise Exception('No available UDP port found for signal relay')


    def load_parameters(self):

        if not os.path.exists(self.conf_file):
            return
        
        with open(self.conf_file, 'r') as f:
            
            settings                        = f.readlines()
            
            for i, setting in enumerate(settings):
                if 'Darkmode' in setting and 'True' in setting:
                    self.darkmode           = True
                elif 'Darkmode' in setting and 'False' in setting:
                    self.darkmode           = False
                if 'Headless' in setting and 'True' in setting:
                    self.run_headless       = True
                elif 'Headless' in setting and 'False' in setting:
                    self.run_headless       = False
                elif 'SamplingRate' in setting:
                    try:
                        self.sample_rate    = int(setting[setting.find('=')+1:])
                    except:
                        print("Could not load \"SamplingRate\" from configuration")
                elif 'AmountChannels' in setting:
                    try:
                        self.max_chans      = int(setting[setting.find('=')+1:])
                    except:
                        print("Could not load \"AmountChannels\" from configuration")
                elif 'TimeRange' in setting:
                    try:
                        self.buffer_length  = int(setting[setting.find('=')+1:])
                    except:
                        print("Could not load \"TimeRange\" from configuration")
                elif 'PGA' in setting:
                    try:
                        self.PGA            = int(setting[setting.find('=')+1:])
                    except:
                        print("Could not load \"PGA\" from configuration")
                elif 'Port' in setting:
                    try:
                        self.port           = str(setting[setting.find('=')+1:])
                        if '\n' in self.port:
                            self.port = self.port.replace('\n', '')
                        ports = [port.device for port in list(serial.tools.list_ports.comports())]
                        if len([p for p in ports if p == self.port]) == 0:
                            self.port = ''
                    except:
                        print("Could not load \"Port\" from configuration")
                elif 'Board' in setting:
                    try:
                        self.board          = str(setting[setting.find('=')+1:])
                        if '\n' in self.board:
                            self.board = self.board.replace('\n', '')
                    except:
                        print("Could not get board information from configuration")
                elif 'DownsamplingFactor' in setting:
                    try:
                        self.s_down         = int(setting[setting.find('=')+1:])
                    except:
                        print("Could not load \"DownsamplingFactor\" from configuration")

        print("Loaded user-defined settings")

        # Missing: self.selected_chans


    def save_parameters(self):

        end_line = "\n"

        if not os.path.exists(self.conf_file): # File generation

            with open(self.conf_file, 'w') as f:

                settings = [
                    "".join(["Darkmode=", str(self.darkmode), end_line]),
                    "".join(["SamplingRate=", str(self.sample_rate), end_line]),
                    "".join(["AmountChannels=", str(self.max_chans), end_line]),
                    "".join(["TimeRange=", str(self.buffer_length), end_line]),
                    "".join(["PGA=", str(self.PGA), end_line]),
                    "".join(["Port=", str(self.port), end_line]),
                    "".join(["Board=", str(self.board), end_line]),
                    "".join(["DownsamplingFactor=", str(self.s_down), end_line]),
                    "".join(["Headless=", str(self.run_headless), end_line])
                    ]

                f.write("".join(settings))

        else:

            with open(self.conf_file, 'r') as f:
            
                settings                        = f.readlines()
                
                for i, setting in enumerate(settings): # Update values
                    if 'Darkmode' in setting:
                        settings[i]             = "".join(["Darkmode=", str(self.darkmode), end_line])
                    elif 'SamplingRate' in setting:
                        settings[i]             = "".join(["SamplingRate=", str(self.sample_rate), end_line])
                    elif 'AmountChannels' in setting:
                        settings[i]             = "".join(["AmountChannels=", str(self.max_chans), end_line])
                    elif 'TimeRange' in setting:
                        settings[i]             = "".join(["TimeRange=", str(self.buffer_length), end_line])
                    elif 'PGA' in setting:
                        settings[i]             = "".join(["PGA=", str(self.PGA), end_line])
                    elif 'Port' in setting:
                        settings[i]             = "".join(["Port=", str(self.port), end_line])
                    elif 'Board' in setting:
                        settings[i]             = "".join(["Board=", str(self.board), end_line])
                    elif 'DownsamplingFactor' in setting:
                        settings[i]             = "".join(["DownsamplingFactor=", str(self.s_down), end_line])
                    elif 'Headless' in setting:
                        settings[i]             = "".join(["Headless=", str(self.run_headless), end_line])

                new_settings = []
                if len([s for s in settings if "Darkmode" in s]) == 0:
                    new_settings.append("".join(["Darkmode=", str(self.darkmode), end_line]))
                if len([s for s in settings if "SamplingRate" in s]) == 0:
                    new_settings.append("".join(["SamplingRate=", str(self.sample_rate), end_line]))
                if len([s for s in settings if "AmountChannels" in s]) == 0:
                    new_settings.append("".join(["AmountChannels=", str(self.max_chans), end_line]))
                if len([s for s in settings if "TimeRange" in s]) == 0:
                    new_settings.append("".join(["TimeRange=", str(self.buffer_length), end_line]))
                if len([s for s in settings if "PGA" in s]) == 0:
                    new_settings.append("".join(["PGA=", str(self.PGA), end_line]))
                if len([s for s in settings if "Port" in s]) == 0:
                    new_settings.append("".join(["Port=", str(self.port), end_line]))
                if len([s for s in settings if "Board" in s]) == 0:
                    new_settings.append("".join(["Board=", str(self.board), end_line]))
                if len([s for s in settings if "DownsamplingFactor" in s]) == 0:
                    new_settings.append("".join(["DownsamplingFactor=", str(self.s_down), end_line]))
                if len([s for s in settings if "Headless" in s]) == 0:
                    new_settings.append("".join(["Headless=", str(self.run_headless), end_line]))

            with open(self.conf_file, 'w') as f:
                f.write("".join(settings + new_settings))


    def set_defaults(self):

        self.all_set        = False
        self.darkmode       = False
        self.run_headless   = False

        #Session-specific parameters
        self.yrange         = [-0, 0] # List of scalars ([negative, positive]) in order to set figure y axis range
        self.notch          = 50 # Integer 0 (Off), 50 (50 Hz) or 60 (60 Hz)
        self.bpass          = 0 # Integer -1 to 3 according to number of options in "frequency_bands" below
        self.dispenv        = False # Boolean 0 (Off), 1 (On)
        self.set_customsession = False

        #Signal arrays
        self.sample_rate    = self.board_characteristics["Neuri V1 by Helment"][1] #Hertz
        self.max_chans      = 8 #scalar (Max. amount of input channels of board)
        self.selected_chans = [True] * self.max_chans
        self.buffer_length  = 10 #scalar (seconds)
        self.buffer_add     = 4 #scalar (seconds), we add this to the buffer for filtering to avoid edge artifacts
        self.saving_interval= 1 #scalar (seconds)
        self.PGA            = 24 #scalar

        #Signal reception
        self.baud_rate      = self.board_characteristics["Neuri V1 by Helment"][2] #scalar default baudrate for connection
        self.port           = '' #Leave blank
        self.board          = '' #Leave blank
        self.start_code     = self.board_characteristics["Neuri V1 by Helment"][0]
        self.time_out       = None #Wait for message

        # Signal relay
        self.udp_ip         = "127.0.0.1" # Loopback ip for on-device communication

        #Plotting
        # self.plot_intv       = 200 #scalar defining update rate of figure (ms) OBSOLETE PARAMETER
        self.s_down         = 1 #Desired downsampling factor (buffer_length*sample_rate/s_down must be convertable to integer)


        #Signal processing
        self.filter_order   = 3 #scalar
        self.frequency_bands= {
            'LineNoise':    (48, 52),
            'LineNoise60':  (58, 62),
            'Sleep':        (1, 30),
            'Theta':        (4, 8),
            'Whole':        (0.5, 45)}


    def build_frontend(self):

        self.framePadX          = 20
        self.framePadY          = 10
        self.widgetPadX         = 10
        self.widgetPadY         = 20
        
        # Build GUI
        # -----------------------------------------------------------------
        self.paramWin           = customtkinter.CTk()
        pixels_x, pixels_y      = int(
            round(0.8*self.screen_width)), int(round(0.9*self.screen_height))
        x_cordinate, y_cordinate= int((self.screen_width/2) - (pixels_x/2)), int(0)
        self.paramWin.geometry("{}x{}+{}+{}".format(
            pixels_x, pixels_y, x_cordinate, y_cordinate))

        if self.darkmode:
            customtkinter.set_appearance_mode("dark")
        else:
            customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        # Decorations
        self.paramWin.title('Neuri GUI: Settings')
        photo = ImageTk.PhotoImage(Image.open(self.ico_neuri))
        self.paramWin.wm_iconphoto(True, photo)
        

        # Add options
        self.display_version(self.paramWin)

        # Elements to place into srollable frame
        frameScroll = self.add_scrollable_frame(self.paramWin)
        self.display_board_version(self.add_frame_ext_x(frameScroll))
        self.display_ports(self.add_frame_ext_x(frameScroll))
        
        # Only used by the Neuri boards which can send data via Bluetooth
        # (currently not implemented in Neuri)
        # self.display_protocol(self.add_frame_ext_x(frameScroll))
        
        self.display_gains(self.add_frame_ext_x(frameScroll))
        self.display_samplingrate(self.add_frame_ext_x(frameScroll))
        self.display_timerange(self.add_frame_ext_x(frameScroll))
        self.display_channels(self.add_frame_ext_x(frameScroll))
        self.display_output_name(self.add_frame_ext_x(frameScroll))
        # self.display_speed_up(self.add_frame_ext_x(frameScroll))
        self.display_headless(self.add_frame_ext_x(frameScroll))
        self.display_validate(self.paramWin)
        
        # Set GUI interaction behavior
        self.paramWin.lift()
        self.paramWin.attributes("-topmost", True)
        self.paramWin.after_idle(self.paramWin.attributes, '-topmost', False)

        # Set closing sequence
        # -----------------------------------------------------------------
        # Just closing the window makes the sampling process hang. We 
        # prevent this by setting up a protocol.
        self.paramWin.protocol('WM_DELETE_WINDOW', self.on_closing)


    def add_frame_ext_x(self, master):
        frameMain               = customtkinter.CTkFrame(master=master)
        frameMain.pack(pady=self.framePadY, padx=self.framePadX,
                       fill="both", expand=True)
        return frameMain


    def add_scrollable_frame(self, master):
        frameScroll             = customtkinter.CTkScrollableFrame(
            master=master, bg_color="transparent", fg_color="transparent")
        frameScroll.pack(pady=self.framePadY, padx=self.framePadX,
                         fill="both", expand=True)
        return frameScroll
    

    def display_version(self, master):

        frameVersion             = customtkinter.CTkFrame(
            master=master, bg_color="transparent", fg_color="transparent")
        frameVersion.pack(pady=0, padx=self.framePadX, fill=tk.X,
                          expand=False, side=tk.TOP)

        repository = "davidmarcelbaum/NeuriGUI"

        g = Github()
        
        try:
            latest_release = g.get_repo(repository).get_latest_release()
            v = latest_release.title.replace("V","")
            v = v.replace("v","")
            v = v.replace(".", "")
            ver_latest = int(v)

            thisv = int(self.version.replace(".", ""))

            if thisv < ver_latest:

                target_webpage = "https://github.com/davidmarcelbaum/NeuriGUI/releases/tag/{}".format(latest_release.title)

                button = customtkinter.CTkButton(
                    frameVersion, text="Download latest version",
                    command=lambda: self.open_webpage(target_webpage))
                button.pack(
                        pady=self.widgetPadY, padx=self.widgetPadX,
                        fill=tk.BOTH, expand=False, side=tk.RIGHT)
                
                customtkinter.CTkLabel(master=frameVersion, 
                justify=customtkinter.RIGHT,
                text="".join(["Realease version ",
                              str(latest_release.title.replace("V","")),
                              " available"]),
                text_color='red').pack(
                    pady=self.widgetPadY, padx=self.widgetPadX,
                    fill=tk.BOTH, expand=False, side=tk.RIGHT)
        except:
            pass

        customtkinter.CTkLabel(master=frameVersion, 
            justify=customtkinter.RIGHT,
            text="".join(["GUI version: ", self.version])).pack(
                pady=self.widgetPadY, padx=self.widgetPadX,
                fill=tk.BOTH, expand=False, side=tk.RIGHT)
        

    def open_webpage(self, target):
        webbrowser.open(target)
        
    
    def get_screen_info(self):

        root = tk.Tk()
        # Get information about screen to center the windows
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        root.destroy()

    
    def display_board_version(self, master):
        
        if self.board == '': 
            defaultBoard = list(self.board_characteristics.keys())[0]
            self.board   = defaultBoard
        else:
            defaultBoard = self.board

        labelBoard = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Select board')
        labelBoard.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)
        BoardMenu = customtkinter.CTkOptionMenu(master,
                                                values=list(self.board_characteristics.keys()),
                                               command=self.select_board)
        BoardMenu.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)
        BoardMenu.set(defaultBoard)


    def select_board(self, event):

        self.board       = str(event)
        print('Board set to {}'.format(self.board))

        self.board_characteristics = {
            "Neuri V1 by Helment":                  [2, 200, 115200],
            "Neuri-Lolin S3-PRO by Helment":        [2, 200, 115200],
            "BioAmp EXG Pill by Upside Down Labs":  [2, 125, 115200]
        }

        if self.board == "Neuri V1 by Helment":
            self.select_channel_amount(2)
            self.predefine_sampling_rate(200)
            self.baud_rate = self.board_characteristics["Neuri V1 by Helment"][2]
        elif self.board == "Neuri-Lolin S3-PRO by Helment":
            self.select_channel_amount(8)
            self.predefine_sampling_rate(200)
            self.baud_rate = self.board_characteristics["Neuri-Lolin S3-PRO by Helment"][2]
        elif self.board == "BioAmp EXG Pill by Upside Down Labs":
            self.select_channel_amount(1)
            self.predefine_sampling_rate(125)
            self.baud_rate = self.board_characteristics["BioAmp EXG Pill by Upside Down Labs"][2]


    def display_ports(self, master):

        ports = [port.device for port in list(serial.tools.list_ports.comports())]
        if len(ports) == 0:
            defaultPort = 'No port available'
        else:
            if self.port == '': 
                defaultPort = ports[0]
                self.port   = defaultPort # If no change, select_port does not get triggered
            else:
                defaultPort = self.port

        labelPort = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Select port')
        labelPort.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)
        portMenu = customtkinter.CTkOptionMenu(master, values=ports,
                                               command=self.select_port)
        portMenu.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)
        portMenu.set(defaultPort)

        infoText = """
            You seem to use a GNU/Linux-based OS. Make sure you are part of
            the "dialout" and "uucp" groups by running:
                > sudo usermod -a -G dialout $USER
                > sudo usermod -a -G uucp $USER
            in the terminal in order to use the system's ports without root.
        """

        if platform == "linux" or platform == "linux2":
            labelLinux = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text=infoText)
            labelLinux.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.RIGHT)


    def select_port(self, event):

        self.port       = event
        print('Port set to {}'.format(self.port))


    # def display_protocol(self, master):

    #     labelProt = customtkinter.CTkLabel(master=master, 
    #                                         justify=customtkinter.LEFT,
    #                                         text='Select connection protocol')
    #     labelProt.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

    #     self.prot_var  = tk.DoubleVar(value=self.neuri_start_signal)

    #     protocolKeys = list(self.neuri_start_signals.keys())
    #     protocolVals = list(self.neuri_start_signals.values())

    #     for i in range(len(self.neuri_start_signals)):
    #         rb = customtkinter.CTkRadioButton(master=master,
    #                                           variable=self.prot_var,
    #                                           value=protocolVals[i],
    #                                           text=str(protocolKeys[i]),
    #                                           command=self.select_protocol)
    #         rb.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)


    # def select_protocol(self):
        
    #     self.firmfeedback = self.prot_var.get()
    #     print('Will send a \"{}\" to board'.format(self.firmfeedback))


    def display_gains(self, master):

        gains = ['1', '2', '4', '6', '8', '12', '24']
        idx_def = [i for i in range(len(gains)) if int(gains[i]) == self.PGA]

        labelGain = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Select gain')
        labelGain.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)
        gainMenu = customtkinter.CTkOptionMenu(master, values=gains,
                                                    command=self.select_gain)
        gainMenu.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)
        gainMenu.set(gains[int(idx_def[0])])


    def select_gain(self, event):

        self.PGA = int(event)
        print('PGA set to {}'.format(self.PGA))


    def display_samplingrate(self, master):
        
        self.labelSfr = customtkinter.CTkLabel(master=master, 
            justify=customtkinter.LEFT,
            text='Optional: Set sampling rate')
        self.labelSfr.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

        self.masterSfr              = customtkinter.CTkFrame(master=master, bg_color="transparent", fg_color="transparent")
        self.masterSfr.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)
        self.frameSfr              = customtkinter.CTkFrame(master=self.masterSfr, bg_color="transparent", fg_color="transparent")
        self.frameSfr.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)

        self.labelInfo = customtkinter.CTkLabel(master=self.frameSfr, 
            justify=customtkinter.LEFT,
            text='Caution: Setting wrong values will corrupt data visualization')
        self.labelInfo.pack(pady=(0, self.widgetPadY), padx=self.widgetPadX, side=tk.BOTTOM)

        self.textSfr = customtkinter.CTkEntry(master=self.frameSfr,
                                           width=200, height=15,
                                           placeholder_text=str(self.sample_rate))
        self.textSfr.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, fill=tk.X, expand=True)

        self.buttonValidate = customtkinter.CTkButton(master=self.frameSfr,
                                                 command=self.select_sampling_rate,
                                                 text='Validate')
        self.buttonValidate.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)


    def select_sampling_rate(self):

        try:
            newSR = int(self.textSfr.get())

            if newSR >= 100:
                self.sample_rate = newSR
                self.labelInfo.configure(text='Sampling rate set to {} Hz'.format(self.sample_rate),
                                        text_color='green')
                print('Sampling rate set to {} Hz.'.format(self.sample_rate))
            else:
                print('Sampling rate must be at least 100 Hz. Reverting back to {} Hz'.format(self.sample_rate))
                self.labelInfo.configure(text='Sampling rate must be at least 100 Hz. Reverting back to {} Hz'.format(self.sample_rate),
                                        text_color='red')
                self.textSfr.configure(placeholder_text='Sampling rate changed to ' + str(self.sample_rate))
        except:
            print('Please enter an integer value. Reverting back to {} Hz'.format(self.sample_rate))
            self.labelInfo.configure(text='Please enter an integer value. Reverting back to {} Hz'.format(self.sample_rate),
                                     text_color='red')


    def predefine_sampling_rate(self, sfr):
        self.sample_rate = sfr

        self.frameSfr.destroy()
        self.frameSfr              = customtkinter.CTkFrame(master=self.masterSfr, bg_color="transparent", fg_color="transparent")
        self.frameSfr.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)

        self.labelInfo = customtkinter.CTkLabel(master=self.frameSfr, 
            justify=customtkinter.LEFT,
            text='Changed to default sampling rate of selected board: {} Hz.'.format(self.sample_rate))
        self.labelInfo.pack(pady=(0, self.widgetPadY), padx=self.widgetPadX, side=tk.BOTTOM)

        self.textSfr = customtkinter.CTkEntry(master=self.frameSfr,
                                           width=200, height=15,
                                           placeholder_text=str(self.sample_rate))
        self.textSfr.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, fill=tk.X, expand=True)

        self.buttonValidate = customtkinter.CTkButton(master=self.frameSfr,
                                                 command=self.select_sampling_rate,
                                                 text='Validate')
        self.buttonValidate.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

        print('Changed to default sampling rate of selected board: {} Hz.'.format(self.sample_rate))


    def display_timerange(self, master):

        labelRange = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Select time range to display')
        labelRange.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)
        
        ranges          = [5, 10, 20]
        idx_def         = [i for i in range(len(ranges)) if int(ranges[i]) == self.buffer_length]

        self.range_var = customtkinter.IntVar(value=ranges[int(idx_def[0])])

        for i in range(len(ranges)):
            rb = customtkinter.CTkRadioButton(master=master,
                                              variable=self.range_var,
                                              value=ranges[i],
                                              text=str(ranges[i]) + ' s',
                                              command=self.select_timerange)
            rb.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)


    def select_timerange(self):
        
        self.buffer_length = self.range_var.get()
        print('Time range to display set to {} s'.format(self.buffer_length))


    def display_channels(self, master):

        labelChans = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Channels to display\n(Only affects the visualization)')
        labelChans.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

        self.channelInfo = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.RIGHT,
                                            text="")
        self.channelInfo.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.RIGHT)

        self.masterChannels              = customtkinter.CTkFrame(master=master, bg_color="transparent", fg_color="transparent")
        self.masterChannels.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)
        self.frameChannels              = customtkinter.CTkFrame(master=self.masterChannels, bg_color="transparent", fg_color="transparent")
        self.frameChannels.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)
        self.channels = []
        for i in range(self.max_chans):
            self.channels.append(tk.BooleanVar())
            cb = customtkinter.CTkCheckBox(master=self.frameChannels,
                                            text='Ch. ' + str(i+1),
                                            command=self.select_channels,
                                            variable=self.channels[i],
                                            onvalue=True,
                                            offvalue=False,
                                            width=50)
            cb.select()
            cb.pack(pady=self.widgetPadY, padx=0, side=tk.LEFT, expand=True, fill=None)


    def select_channel_amount(self, numchans):

        self.max_chans      = numchans
        self.selected_chans = [True] * self.max_chans
        self.frameChannels.destroy()
        self.frameChannels              = customtkinter.CTkFrame(master=self.masterChannels, bg_color="transparent", fg_color="transparent")
        self.frameChannels.pack(pady=0, padx=0, fill="both", expand=True, side=tk.RIGHT)
        self.channels       = []
        for i in range(self.max_chans):
            self.channels.append(tk.BooleanVar())
            cb = customtkinter.CTkCheckBox(master=self.frameChannels,
                                            text='Ch. ' + str(i+1),
                                            command=self.select_channels,
                                            variable=self.channels[i],
                                            onvalue=True,
                                            offvalue=False)
            cb.select()
            cb.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)
        self.channelInfo.configure(text="")


    def select_channels(self):

        for i, channel in enumerate(self.channels):
            if self.selected_chans[i] != channel.get():
                self.selected_chans[i] = channel.get()
                if channel.get():
                    print('Channel {} enabled'.format(i))
                else:
                    print('Channel {} disabled'.format(i))

        if not any(self.selected_chans):
            self.channelInfo.configure(text="Select at least one channel",
                text_color='red')
        else:
            self.channelInfo.configure(text="")


    def display_output_name(self, master):
        
        self.sessionName = 'Neuri_[timestamp]'
        self.labelSession = customtkinter.CTkLabel(master=master, 
            justify=customtkinter.CENTER,
            text='Optional: Set a session name')
        self.labelSession.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

        self.sessionInfo = customtkinter.CTkLabel(master=master, 
            justify=customtkinter.LEFT,
            text='')
        self.sessionInfo.pack(pady=(0, self.widgetPadY), padx=self.widgetPadX, side=tk.BOTTOM)

        self.textSession = customtkinter.CTkEntry(master=master,
                                           width=250, height=15,
                                           placeholder_text='Default: ' + self.sessionName)
        self.textSession.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, fill=tk.X, expand=True)

        self.sessionValidate = customtkinter.CTkButton(master=master,
                                                 command=self.select_output_name,
                                                 text='Validate')
        self.sessionValidate.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)


    def select_output_name(self):

        newSessionName      = str(self.textSession.get())

        if len(newSessionName) > 0:
            self.sessionName    = newSessionName
            self.sessionName    = self.sessionName.replace('\n', '')
            self.set_customsession = True
            self.sessionInfo.configure(text='Session name changed to ' + str(self.sessionName),
                             text_color='green')
            print('Session named \"{}\".'.format(self.sessionName))
        else:
            self.sessionInfo.configure(text='Custom name can not be empty',
                             text_color='red')
            print('Session name can not be empty')


    def display_speed_up(self, master):

        down_facotr = ['1', '2', '5', '10'] # TO-DO: Fix GUI freezing when chosing '1' (no downsampling)
        idx_def     = [i for i in range(len(down_facotr)) if int(down_facotr[i]) == self.s_down]

        labelSpeed  = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Optional: Select downsampling intensity')
        labelSpeed.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)
        SpeedMenu   = customtkinter.CTkOptionMenu(master, values=down_facotr,
                                                    command=self.select_speed_up)
        SpeedMenu.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)
        SpeedMenu.set(down_facotr[int(idx_def[0])])

        infoText    = """
            Selecting high amounts of channels and long time ranges to display can have impacts on the performance.
            You might try to compensate this by setting a higher downsampling factor. This will downsample the data
            for visualization (not the recorded data itself)
            """

        labelInfo   = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text=infoText)
        labelInfo.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.RIGHT)


    def select_speed_up(self, event):

        self.s_down = int(event)
        print('Downsampling intensity set to {}'.format(self.s_down))


    def display_headless(self, master):

        labelHeadless = customtkinter.CTkLabel(master=master, 
                                            justify=customtkinter.LEFT,
                                            text='Sample data without GUI (headless)')
        labelHeadless.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT)

        self.toggled_headless = tk.BooleanVar()
        cb = customtkinter.CTkCheckBox(master=master,
                                        text='',
                                        command=self.set_headless,
                                        variable=self.toggled_headless,
                                        onvalue=True,
                                        offvalue=False)
        if self.run_headless:
            cb.select()
        cb.pack(pady=self.widgetPadY, padx=self.widgetPadX, side=tk.LEFT, expand=True)


    def set_headless(self):

        self.run_headless = self.toggled_headless.get()


    def display_validate(self, master):

        customtkinter.CTkFrame(master, height=1, bg_color='transparent').pack(side=tk.LEFT, fill=tk.X)
        customtkinter.CTkFrame(master, height=1, bg_color='transparent').pack(side=tk.RIGHT, fill=tk.X)

        customtkinter.CTkButton(master,
            text="Save & Start",
            border_width=2,
            border_color="#3B8ED0",
            text_color="#3B8ED0",
            fg_color="white",
            hover_color= "#B8C8D4",
            command=self.on_validating).pack(
                pady=self.framePadY, padx=self.framePadX, side=tk.LEFT)
        
        customtkinter.CTkButton(master,
            text="Reset & Quit",
            border_width=2,
            border_color="#c54040",
            text_color="#c54040",
            fg_color="white",
            hover_color= "#EDC5C5",
            command=self.on_reset).pack(
                pady=self.framePadY, padx=self.framePadX, side=tk.RIGHT)


    def on_validating(self):
        
        print("Parameters set")
        self.save_parameters()
        print("".join(["Parameters stored in ", self.conf_file]))
        self.paramWin.destroy()
        print("Starting GUI now...")


    def on_reset(self):
        
        self.set_defaults()
        print("Parameters have been reset")
        self.save_parameters()
        print("".join(["Settings in ", self.conf_file, "have been reset"]))
        print("Please start the GUI again")
        quit()


    def on_closing(self):

        print("Chose to quit program")
        quit()