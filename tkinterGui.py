from tkinter import *
import tkinter as tk
from tkinter import filedialog as fd
import customtkinter
from floatSpinBox import *
from PIL import ImageTk,Image
import matplotlib
import matplotlib.pyplot as plt
from tkinter import ttk
from ClusteredFileProcessing_v2 import *
from HitCountImg import *
from SpectImg import *
from TkinterGraphing import *
from ImageSpectrumAnalysis import *
from ImageHitRateAnalysis import *

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)


customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green
root = customtkinter.CTk()

###############################################################################
#################################----VARIABLES-----############################
global processedData

#Clustering params
timeStep_s = 0.2
time_max_s= 0.2*20
energy_max = 100


analysisFrame = customtkinter.CTkFrame(root)
analysisFrame.pack(side=BOTTOM, fill="both", expand=True)

RightPannelFrame = customtkinter.CTkFrame(root)
RightPannelFrame.pack(side=RIGHT, fill=BOTH, expand=True)

ConnectionPannel_Frame = customtkinter.CTkFrame(RightPannelFrame)
ConnectionPannel_Frame.pack(side=TOP, fill=BOTH, expand=True)

ImageFrame = customtkinter.CTkFrame(RightPannelFrame)
ImageFrame.pack(side=TOP, fill=BOTH, expand=True)

# Create a graphing object
TKG = Tkinter_Graphing(ImageFrame)
#Fill with dummy data - make it show some default stuff
#arr = np.zeros((4,4))
#arr[1,2] = 1
#arr[0,3] = 2
#Tkinter_Graphing.show_image(TKG, arr)

################################################################################################
###############################-----CONNECTION PANEL-----#######################################
class ConnectionPannelContents:
    def __init__(self, master):
        #Variables
        self.COM_NAME = StringVar()
        self.lbl_COM_name = customtkinter.CTkLabel(master,text='Select the COM port')
        self.lbl_COM_name.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM = customtkinter.CTkComboBox(master, variable=self.COM_NAME, command= self.COM_changed)
        self.cb_selCOM.configure(values = ["dummy1", "dummy2", "dummy3", "dummy4"])
        self.cb_selCOM.configure(state = 'readonly')
        self.cb_selCOM.pack(side=LEFT, fill=BOTH)
        self.cb_selCOM.bind('<<ComboBoxSelected>>', self.COM_changed)

        self.btn_Connect = customtkinter.CTkButton(master, text="Connect", command=self.Connect_click)
        self.btn_Connect.pack(side=LEFT, fill=BOTH)
        
        self.lbl_device_state = customtkinter.CTkLabel(master,text='Device state')
        self.lbl_device_state.pack(side=LEFT, fill=BOTH)

    def Connect_click(self):
        pass

    def COM_changed(self):
        pass
    



################################################################################################
###############################-----CONTROL PANEL-----##########################################
CtrlFrame = customtkinter.CTkFrame(root)
CtrlFrame.pack(side=LEFT, fill=BOTH, expand=1)

class AcquisitionSetup:
    def __init__(self, master):
        #Variables
        self.clusteredFilePath = ""
        #UI
        self.lbl_SelClusFile = customtkinter.CTkLabel(master,text='Select measurement file name:')
        self.lbl_SelClusFile.pack(side=TOP, fill=BOTH, pady=(30,0))
        selFileFrame = customtkinter.CTkFrame(master)
        selFileFrame.pack(side=TOP)
        self.tb_ClusFilePath = customtkinter.CTkEntry(selFileFrame, state="disabled")
        self.tb_ClusFilePath.pack(side=LEFT, fill=BOTH)
        self.btn_sel_clusFile = customtkinter.CTkButton(selFileFrame, text="Select", command=self.SelectFile_click)
        self.btn_sel_clusFile.pack(side=LEFT, fill=BOTH)

        self.NF_period = IntVar()
        self.Comp_lvl = DoubleVar()
        filePeriodSpecFrame = customtkinter.CTkFrame(master)
        filePeriodSpecFrame.pack(side=TOP, fill=BOTH)
        self.lbl_paramsSel = customtkinter.CTkLabel(filePeriodSpecFrame, text="New file period: ")
        self.lbl_paramsSel.pack(side=LEFT, fill=BOTH)
        self.tb_NF_period = customtkinter.CTkEntry(filePeriodSpecFrame, textvariable=self.NF_period)
        self.tb_NF_period.pack(side=LEFT, fill=BOTH, expand=1)

        paramSpecFrame = customtkinter.CTkFrame(master)
        paramSpecFrame.pack(side=TOP, fill=BOTH)

        self.lbl_Comp_lvl = customtkinter.CTkLabel(paramSpecFrame, text="Comp. level: ")
        self.lbl_Comp_lvl.pack(side=LEFT)
        self.tb_Comp_lvl = customtkinter.CTkEntry(paramSpecFrame, textvariable=self.Comp_lvl)
        self.tb_Comp_lvl.pack(side=LEFT, fill=BOTH, expand=1)
        #self.lbl_maxE = customtkinter.CTkLabel(energy_max_Frame, text="Max E:")
        #self.lbl_maxE.pack(side=LEFT)
        #self.tb_maxE = customtkinter.CTkEntry(energy_max_Frame, textvariable=self.Max_Energy)
        #self.tb_maxE.pack(side=LEFT, fill=BOTH, expand=1)


        self.btn_sel_acq_path = customtkinter.CTkButton(master, text="Select", command=self.ClusProcess_click)
        self.btn_sel_acq_path.pack(side=TOP, fill=BOTH)

    def SelectFile_click(self):
        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        #Show open file dialog
        self.clusteredFilePath = fd.askopenfilename(title='Select a measurement file', filetypes=filetypes)
        
        self.tb_ClusFilePath["state"] = "normal"
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.clusteredFilePath)[1]) 
        self.tb_ClusFilePath["state"] = "disabled"

    def ClusProcess_click(self):      
        filetypes = (('pickle files', '*.pickle'), ('All files', '*.*'))
        #Show save file dialog
        processed_fileName = fd.asksaveasfile(initialfile = 'Untitled.pickle', defaultextension=".pickle",filetypes=filetypes)
        #Process
        global processedData
        processedData = histogram_matrix_v2(256, 256, self.Max_Energy.get(), self.TimeStep.get())
        histogram_matrix_v2.getProcessedData(processedData, self.clusteredFilePath, processed_fileName.name)

 
class ProcessedFileLoad:
    def __init__(self, master):
        #Variables
        self.processedFilePath = ""
        #UI
        self.lbl_SelClusFile = customtkinter.CTkLabel(master,text='Select processed file:')
        self.lbl_SelClusFile.pack(side=TOP, fill=BOTH, pady=(30,0))
        selFileFrame = customtkinter.CTkFrame(master)
        selFileFrame.pack(side=TOP)
        self.tb_ClusFilePath = customtkinter.CTkEntry(selFileFrame, state="disabled")
        self.tb_ClusFilePath.pack(side=LEFT, fill=BOTH)
        self.btn_sel_clusFile = customtkinter.CTkButton(selFileFrame, text="Select", command=self.selProcesssedFile_click)
        self.btn_sel_clusFile.pack(side=LEFT, fill=BOTH)
        self.btn_process_clusFile = customtkinter.CTkButton(master, text="Load File", command=self.loadProcessedFile_click)
        self.btn_process_clusFile.pack(side=TOP, fill=BOTH)

    def selProcesssedFile_click(self):
        filetypes = (('pickle files', '*.pickle'), ('All files', '*.*'))
        #Show open file dialog
        self.processedFilePath = fd.askopenfilename(title='Select a processed file', filetypes=filetypes)   

        self.tb_ClusFilePath["state"] = "normal"
        self.tb_ClusFilePath.delete(0,END)
        self.tb_ClusFilePath.insert(0,os.path.split(self.processedFilePath)[1])  
        self.tb_ClusFilePath["state"] = "disabled"

    def loadProcessedFile_click(self):
        picklefile = open(self.processedFilePath, 'rb')
        global processedData
        processedData = pickle.load(picklefile)

acq_ctrl_box = AcquisitionSetup(CtrlFrame)
conn_ctrl_box = ConnectionPannelContents(ConnectionPannel_Frame)

# Tabs:
tabControl = customtkinter.CTkTabview(analysisFrame)#ttk.Notebook(analysisFrame)
tabControl.add('Basics')#(tab_basic, text ='Basics')
tabControl.add('Spectral')#(tab_spectral, text ='Spectral')
tabControl.add('Hit rates')#(tab_hitRates, text ='Hit rates')
tabControl.pack(side = TOP, expand = 1, fill ="both")

tab_basic = tabControl.tab("Basics")
tab_spectral = tabControl.tab("Spectral")
tab_hitRates = tabControl.tab("Hit rates")


##########################################################################################################
##########################---------Basics tab--------#####################################################
basics_left = customtkinter.CTkFrame(tab_basic)
basics_left.pack(side=LEFT, expand=1, fill=BOTH,anchor="w")


class ImgTypeSel:
    def __init__(self, master):
        #  Radio button mode    
        self.useSpectral = IntVar()
        self.rb_CNT_IMG = customtkinter.CTkRadioButton(basics_left, text="CNT mode", variable=self.useSpectral, value=0, command=self.rb_sel)
        self.rb_CNT_IMG.pack(side=TOP, expand=1,anchor="w")
        self.rb_spect_IMG = customtkinter.CTkRadioButton(basics_left, text="Spectral mode",  variable=self.useSpectral, value=1, command=self.rb_sel)
        self.rb_spect_IMG.pack(side=TOP, expand=1, anchor="w")
        
    def rb_sel(self):
        if(self.useSpectral.get() == 0):
            # Disable the energy controls
            E1.cb_E_sel.set(0)
            E2.cb_E_sel.set(0)
            E3.cb_E_sel.set(0)
            E1.cb_E_sel_change()
            E2.cb_E_sel_change()
            E3.cb_E_sel_change()
            E1.cb_E.configure(state="disabled")
            E2.cb_E.configure(state="disabled")
            E3.cb_E.configure(state="disabled")
            #E2.cb_E["state"] = "disabled"
            #E3.cb_E["state"] = "disabled"
            #E1.cb_E["state"] = "disabled"
        else:
            E1.cb_E.configure(state="normal")
            E2.cb_E.configure(state="normal")
            E3.cb_E.configure(state="normal")
            #E1.cb_E["state"] = "normal"
            #E2.cb_E["state"] = "normal"
            #E3.cb_E["state"] = "normal"

ImgType_checkboxes = ImgTypeSel(basics_left)

class energySelect:

    def __init__(self, master):
        self.cb_E_sel = IntVar()
        self.sb_E_min_val = IntVar()
        self.sb_E_max_val = IntVar()
        self.E_frame = customtkinter.CTkFrame(master)
        self.E_frame.pack(side = TOP, expand = 1, fill ="both")
        self.cb_E = customtkinter.CTkSwitch(self.E_frame, text='Add energy range', variable=self.cb_E_sel, onvalue=1, offvalue=0, command=self.cb_E_sel_change)#CTkCheckButton(self.E_frame, text='Add energy range', variable=self.cb_E_sel, onvalue=1, offvalue=0, command=self.cb_E_sel_change)
        self.cb_E.pack(side=TOP)
        self.lbl_E = customtkinter.CTkLabel(self.E_frame, text ='Select the energy range:', state="disabled") 
        self.lbl_E.pack(side=LEFT)
        self.sb_e_min = FloatSpinbox(self.E_frame, state="disabled", from_=0, to=100, step_size=1, command=self.min_spinBoxChange, textVariable=self.sb_E_min_val)#, command=self.sb_min_value_changed)
        self.sb_e_min.pack(side=LEFT)
        self.lbl_E_to = customtkinter.CTkLabel(self.E_frame, text =' to:') 
        self.lbl_E_to.pack(side=LEFT)
        self.sb_e_max = FloatSpinbox(self.E_frame, state="disabled", from_=0, to=100, step_size=1, command=self.max_spinBoxChange,  textVariable=self.sb_E_max_val)#, command=self.sb_max_value_changed)
        self.sb_e_max.pack(side=LEFT)
        
    def min_spinBoxChange(self):
        self.sb_E_min_val = self.sb_e_min.get()
    def max_spinBoxChange(self):
        self.sb_E_max_val = self.sb_e_max.get()

    def cb_E_sel_change(self):
        if(self.cb_E_sel.get()==0):
            self.sb_e_max.setDisabled()
            self.sb_e_min.setDisabled()
            self.lbl_E["state"] = "disabled"
            
        else:
            self.sb_e_max.setNormal()
            self.sb_e_min.setNormal()
            self.lbl_E["state"] = "normal"
            
    
    def sb_min_value_changed(self):
          self.sb_E_min_val = self.sb_e_min.get()
    
    
    def sb_max_value_changed(self):
          self.sb_E_max_val = self.sb_e_max.get()

# Show energy ranges    
E1 = energySelect(basics_left)
E2 = energySelect(basics_left)
E3 = energySelect(basics_left)
# Set default image type selection (count)
ImgType_checkboxes.rb_sel()

basics_right = customtkinter.CTkFrame(tab_basic)
basics_right.pack(side=RIGHT)

class BasicImshowButtons:
    def __init__(self, master):
        self.CNT_show = customtkinter.CTkButton(master, text="Show image",command=self.show_IMG)
        self.CNT_show.pack(side=TOP)
        #self.EGY_RANGE_show = Button(master, text="Show energy range image", command=self.show_EGY_IMG)
        #self.EGY_RANGE_show.pack(side=TOP)

    def show_IMG(self):
        if(ImgType_checkboxes.useSpectral.get() == 0):
            hitCntIMG = getHitCountImage(processedData)
        
            Tkinter_Graphing.show_image(TKG, hitCntIMG)
        else:
            ranges = list()
            if(E1.cb_E_sel.get()==1):
                ranges.append([E1.sb_e_min.get(), E1.sb_e_max.get()])
            if(E2.cb_E_sel.get()==1):
                ranges.append([int(E2.sb_e_min.get()), int(E2.sb_e_max.get())])
            if(E3.cb_E_sel.get()==1):
                ranges.append([int(E3.sb_e_min.get()), int(E3.sb_e_max.get())])
            
            energyIMG = getSpectralImage(processedData.hist, ranges)

            # Show
            TKG.show_image(energyIMG)
            pass

    def show_EGY_IMG(self):
        #Compute and show the energy image
        pass


ShowImgButtons = BasicImshowButtons(tab_basic)

######################################################################################################
#######################-----SPECTRAL TAB-----#########################################################
spect_left = customtkinter.CTkFrame(tab_spectral, width=20)
spect_left.pack(side=LEFT, fill=BOTH)

class spectrumSelectionUI:
    
    def __init__(self, master, type, promptLabel):
        self.selectedSpectrum = StringVar()
        self.data_type = type
        self.lbl_spectSel = customtkinter.CTkLabel(master, text=promptLabel)
        self.lbl_spectSel.pack(side=TOP, fill=BOTH)
        self.cb_selSpectrumType = customtkinter.CTkComboBox(master, variable=self.selectedSpectrum, command= self.spectType_changed)
        self.cb_selSpectrumType.configure(values = ["Total", "Pixel", "Row", "Column"])
        self.cb_selSpectrumType.configure(state = 'readonly')
        self.cb_selSpectrumType.pack(side=TOP, fill=BOTH)
        self.cb_selSpectrumType.bind('<<ComboBoxSelected>>', self.spectType_changed)

        self.Px_selectionFrame = customtkinter.CTkFrame(master)
        self.Px_selectionFrame.pack(side=TOP)
        self.x_pos = IntVar()
        self.y_pos = IntVar()
        self.lbl_x = customtkinter.CTkLabel(self.Px_selectionFrame, text ='x:', state="disabled") 
        self.lbl_x.pack(side=LEFT)
        self.sb_x_pos = FloatSpinbox(self.Px_selectionFrame, state="disabled", from_=0, to=255, step_size=1, command=self.x_spinBoxChange, textVariable=self.x_pos)
        self.sb_x_pos.pack(side=LEFT)
        self.lbl_y = customtkinter.CTkLabel(self.Px_selectionFrame, text ='y:', state="disabled") 
        self.lbl_y.pack(side=LEFT)
        self.sb_y_pos = FloatSpinbox(self.Px_selectionFrame, state="disabled", from_=0, to=255, step_size=1, command=self.y_spinBoxChange, textVariable=self.y_pos)
        self.sb_y_pos.pack(side=LEFT)

        self.x_pos.trace('w', self.coordinatesUpdated)
        self.y_pos.trace('w', self.coordinatesUpdated)

    def x_spinBoxChange(self):
        self.x_pos = self.sb_x_pos.get()
        self.spectType_changed(None)
    def y_spinBoxChange(self):
        self.y_pos = self.sb_y_pos.get()
        self.spectType_changed(None)

    def spectType_changed(self,event):
        selected = self.selectedSpectrum.get()
        global processedData
        if(selected == "Total"):
            # Disable the buttons
            self.sb_x_pos['state'] = 'disabled'
            self.sb_y_pos['state'] = 'disabled'
            # Show the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getTotalSpectrum(processedData.hist)
                x = np.linspace(0, np.size(spect), np.size(spect))
                #TKG.__init__(ImageFrame)
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getTotalSpectrum(processedData.timeHist, processedData.timeStep)
                TKG.show_plot( t, spect)
            
        elif(selected=="Pixel"):
            # Enable the buttons
            self.sb_x_pos['state'] = 'normal'
            self.sb_y_pos['state'] = 'normal'
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getPixelSpectrum(processedData.hist, [self.x_pos, self.y_pos])
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getPixelSpectrum(processedData.timeHist, [self.x_pos, self.y_pos], processedData.timeStep)
                TKG.show_plot( t, spect)
        elif(selected=="Column"):
            # Disable the buttons
            self.sb_x_pos['state'] = 'disabled'
            self.sb_y_pos['state'] = 'normal'
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getRowSpectrum(processedData.hist, self.y_pos)
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getRowSpectrum(processedData.timeHist, self.y_pos, processedData.timeStep)
                TKG.show_plot( t, spect)
        elif(selected=="Row"):
            # Disable the buttons
            self.sb_x_pos['state'] = 'normal'
            self.sb_y_pos['state'] = 'disabled'
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getColumnSpectrum(processedData.hist, self.x_pos)
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getColumnSpectrum(processedData.timeHist, self.x_pos, processedData.timeStep)
                TKG.show_plot( t, spect)

    def coordinatesUpdated(self,b,c,d):
        selected = self.selectedSpectrum.get()
        global processedData
        if(selected=="Pixel"):
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getPixelSpectrum(processedData.hist, [self.x_pos, self.y_pos])
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getPixelSpectrum(processedData.timeHist, [self.x_pos, self.y_pos], processedData.timeStep)
                TKG.show_plot( t, spect)
        elif(selected=="Column"):
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getRowSpectrum(processedData.hist, self.y_pos)
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getRowSpectrum(processedData.timeHist, self.y_pos, processedData.timeStep)
                TKG.show_plot( t, spect)
        elif(selected=="Row"):
            #Draw the spectrum
            if(self.data_type == "energy"):
                spect = ImageSpectrumAnalysis.getColumnSpectrum(processedData.hist, self.x_pos)
                x = np.linspace(0, np.size(spect), np.size(spect))
                TKG.show_plot( x, spect)
            elif(self.data_type == "hitRate"):
                [t,spect] = ImageHitRateAnalysis.getColumnSpectrum(processedData.timeHist, self.x_pos, processedData.timeStep)
                TKG.show_plot( t, spect)


spectSel = spectrumSelectionUI(spect_left, "energy", "Select spectrum type to display:")

hitRate_left = customtkinter.CTkFrame(tab_hitRates, width=20)
hitRate_left.pack(side=LEFT, fill=BOTH)
hitRateSel = spectrumSelectionUI(hitRate_left, "hitRate", "Select hit-rate type to display:")

root.mainloop()