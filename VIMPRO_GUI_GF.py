###############################################################################
##                                                                           ##
##             ________________________________     _________   _________    ##
##            // ____  ____  _________________/    // ____  /  // ____  /    ##
##           // /  // /  // /                     // /  // /  // /  // /     ##
##          // /  // /  // /_____  _________     // /__// /__//_/__// /      ##
##         // /  // /  // ______/ // ______/    // __________________/       ##
##        // /  // /  // /_______//_/_____     // /        // /_____         ##
##       // /  // /  // _______________  /    // /        //_____  /         ##
##      // /  // /  // /_____  // /__// /    // /        ___   // /          ##
##     // /__// /  // ______/ //_______/    // /        // /__// /           ##
##    //_______/  //_/                     //_/        //_______/            ##
##                                                                           ##
##                                                             Stefan Radman ##
###############################################################################

### IMPORTS ###################################################################

import os
import ntpath
import logging
import numpy as np

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk

import VIMPRO_Processor as vp
import VIMPRO_Tkinter as vk
import VIMPRO_Data as vd

from tkinter.filedialog import askdirectory

### FUNCTIONS #################################################################

### CLASSES ###################################################################

class GUI_GF(tk.Toplevel) :

    def __init__(self, root, **kwargs) :

        tk.Toplevel.__init__(self, root, **kwargs)
        self.root = root
        self.title("Generative features options")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # UI Constants ---------------#
        self.label_width = 20
        self.button_width = 10
        self.entry_width = 8
        self.default_pad = 20
        self.pad0 = vk.Padding(self.default_pad, self.default_pad)
        self.pad1 = vk.Padding(self.default_pad/4, self.default_pad/8)
        
        self.frame = tk.Frame(self)
        self.frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S,
            **self.pad0.get("c"))

        row_names = ["Number of runs", "Palette size range", 
        "R channel bit range", "G channel bit range", "B channel bit range",
        "Set output folder", "Run"]
        self.rows = {}
        for i, name in enumerate(row_names) :
            self.rows[name] = i

        # Number of runs -------------#
        row_name = "Number of runs"
        row_n = self.rows[row_name]
        self.n_runs_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.n_runs_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.n_runs = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.n_runs.set(10)
        self.n_runs.grid(row=row_n, column=1, columnspan=2,
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # Palettes size range --------#
        row_name = "Palette size range"
        row_n = self.rows[row_name]
        self.palettes_sr_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.palettes_sr_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.palettes_sr_min = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.palettes_sr_min.set(3)
        self.palettes_sr_min.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.palettes_sr_max = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.palettes_sr_max.set(6)
        self.palettes_sr_max.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # R channel bit range --------#
        row_name = "R channel bit range"
        row_n = self.rows[row_name]
        self.r_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.r_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.r_channel_br_min = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.r_channel_br_min.set(2)
        self.r_channel_br_min.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.r_channel_br_max = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.r_channel_br_max.set(8)
        self.r_channel_br_max.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # G channel bit range --------#
        row_name = "G channel bit range"
        row_n = self.rows[row_name]
        self.g_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.g_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.g_channel_br_min = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.g_channel_br_min.set(2)
        self.g_channel_br_min.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.g_channel_br_max = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.g_channel_br_max.set(8)
        self.g_channel_br_max.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # B channel bit range --------#
        row_name = "B channel bit range"
        row_n = self.rows[row_name]
        self.b_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.b_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.b_channel_br_min = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.b_channel_br_min.set(2)
        self.b_channel_br_min.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.b_channel_br_max = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.b_channel_br_max.set(8)
        self.b_channel_br_max.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # Output folder --------------#
        row_name = "Set output folder"
        row_n = self.rows[row_name]
        self.output_folder_b = tk.Button(self.frame, text=row_name,
            command=self.on_set_output_folder)
        self.output_folder_b.grid(row=row_n, column=0, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("w"))
        self.output_folder = None

        # Run ------------------------#
        row_name = "Run"
        row_n = self.rows[row_name]
        self.run_b = tk.Button(self.frame, text=row_name,
            command=self.on_run)
        self.run_b.config(state=tk.DISABLED)
        self.run_b.grid(row=row_n, column=0, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("sw"))

        # Adjust
        vk.stretch_grid(self.frame)

    def on_set_output_folder(self) :
        f = askdirectory()
        print(f)
        if f != None and f != '':
            self.output_folder = f
            self.run_b.config(state=tk.NORMAL)

    def on_run(self) :
        pass

    def on_close(self) :
        self.root.on_open_gf_view()
        self.withdraw()