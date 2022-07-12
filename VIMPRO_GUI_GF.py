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

from tkinter.filedialog import askdirectory, askopenfile

import colorsys

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

        row_names = ["Palette size range", 
        "R channel bit range", "G channel bit range", "B channel bit range",
        "Outline", "Background", "Load alpha mask", "Alpha mask", 
        "Alpha mask value", "Step", "Set output folder", "Number of runs", 
        "Run"]
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
        self.n_runs_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.n_runs_e.set(10)
        self.n_runs_e.grid(row=row_n, column=1, columnspan=2,
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # Palettes size range --------#
        row_name = "Palette size range"
        row_n = self.rows[row_name]
        self.palettes_sr_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.palettes_sr_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.palettes_sr_min_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.palettes_sr_min_e.set(3)
        self.palettes_sr_min_e.set_min_value(1)
        self.palettes_sr_min_e.set_max_value(32)
        self.palettes_sr_min_e.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.palettes_sr_max_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.palettes_sr_max_e.set(6)
        self.palettes_sr_max_e.set_max_value(32)
        self.palettes_sr_max_e.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.palettes_sr_min_e.set_max_value_e(self.palettes_sr_max_e)
        self.palettes_sr_max_e.set_min_value_e(self.palettes_sr_min_e)

        # R channel bit range --------#
        row_name = "R channel bit range"
        row_n = self.rows[row_name]
        self.r_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.r_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.r_channel_br_min_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.r_channel_br_min_e.set(2)
        self.r_channel_br_min_e.set_min_value(1)
        self.r_channel_br_min_e.set_max_value(8)
        self.r_channel_br_min_e.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.r_channel_br_max_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.r_channel_br_max_e.set(8)
        self.r_channel_br_max_e.set_min_value(1)
        self.r_channel_br_max_e.set_max_value(8)
        self.r_channel_br_max_e.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.r_channel_br_min_e.set_max_value_e(self.r_channel_br_max_e)
        self.r_channel_br_max_e.set_min_value_e(self.r_channel_br_min_e)

        # G channel bit range --------#
        row_name = "G channel bit range"
        row_n = self.rows[row_name]
        self.g_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.g_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.g_channel_br_min_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.g_channel_br_min_e.set(2)
        self.g_channel_br_min_e.set_min_value(1)
        self.g_channel_br_min_e.set_max_value(8)
        self.g_channel_br_min_e.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.g_channel_br_max_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.g_channel_br_max_e.set(8)
        self.g_channel_br_max_e.set_min_value(1)
        self.g_channel_br_max_e.set_max_value(8)
        self.g_channel_br_max_e.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.g_channel_br_min_e.set_max_value_e(self.g_channel_br_max_e)
        self.g_channel_br_max_e.set_min_value_e(self.g_channel_br_min_e)

        # B channel bit range --------#
        row_name = "B channel bit range"
        row_n = self.rows[row_name]
        self.b_channel_br_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.b_channel_br_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.b_channel_br_min_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.b_channel_br_min_e.set(2)
        self.b_channel_br_min_e.set_min_value(1)
        self.b_channel_br_min_e.set_max_value(8)
        self.b_channel_br_min_e.grid(row=row_n, column=1, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.b_channel_br_max_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.b_channel_br_max_e.set(8)
        self.b_channel_br_max_e.set_min_value(1)
        self.b_channel_br_max_e.set_max_value(8)
        self.b_channel_br_max_e.grid(row=row_n, column=2, 
            sticky=tk.W+tk.E, **self.pad1.get("c"))
        self.b_channel_br_min_e.set_max_value_e(self.b_channel_br_max_e)
        self.b_channel_br_max_e.set_min_value_e(self.b_channel_br_min_e)

        # Outline --------------------#
        row_name = "Outline"
        row_n = self.rows[row_name]
        self.outline = False
        self.outline_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.outline_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.outline_iv = tk.IntVar()
        self.outline_cb = tk.Checkbutton(self.frame, variable=self.outline_iv, 
            onvalue=1, offvalue=0, command=self.on_outline_check)
        self.outline_cb.grid(row=row_n, column=1, sticky=tk.W, 
            **self.pad1.get("w"))

        # Background -----------------#
        row_name = "Background"
        row_n = self.rows[row_name]
        self.background = False
        self.background_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.background_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.background_iv = tk.IntVar()
        self.background_cb = tk.Checkbutton(self.frame, 
            variable=self.background_iv, onvalue=1, offvalue=0, 
            command=self.on_background_check)
        self.background_cb.grid(row=row_n, column=1, sticky=tk.W, 
            **self.pad1.get("w"))

        # Load alpha mask ------------#
        row_name = "Load alpha mask"
        row_n = self.rows[row_name]
        self.load_alpha_mask_b = tk.Button(self.frame, text=row_name,
            command=self.on_load_alpha_mask)
        self.load_alpha_mask_b.grid(row=row_n, column=0, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("w"))
        self.alpha_mask_data = None
        self.alpha_mask_image = None

        # Alpha mask -----------------#
        row_name = "Alpha mask"
        row_n = self.rows[row_name]
        self.alpha_mask = False
        self.alpha_mask_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.alpha_mask_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.alpha_mask_iv = tk.IntVar()
        self.alpha_mask_cb = tk.Checkbutton(self.frame, 
            variable=self.alpha_mask_iv, onvalue=1, offvalue=0, 
            command=self.on_alpha_mask_check)
        self.alpha_mask_cb.grid(row=row_n, column=1, sticky=tk.W, 
            **self.pad1.get("w"))
        self.alpha_mask_cb.config(state=tk.DISABLED)

        # Alpha mask value -----------#
        row_name = "Alpha mask value"
        row_n = self.rows[row_name]
        self.alpha_mask_value_l = tk.Label(self.frame, text=row_name, 
            anchor=tk.W)
        self.alpha_mask_value_l.grid(row=row_n, column=0, sticky=tk.W, 
            **self.pad1.get("w"))
        self.alpha_mask_value_e = vk.IntEntry(self.frame, 
            width=self.entry_width)
        self.alpha_mask_value_e.set(127)
        self.alpha_mask_value_e.set_min_value(0)
        self.alpha_mask_value_e.set_max_value(255)
        self.alpha_mask_value_e.grid(row=row_n, column=1, columnspan=2,
            sticky=tk.W+tk.E, **self.pad1.get("c"))

        # Output folder --------------#
        row_name = "Set output folder"
        row_n = self.rows[row_name]
        self.output_folder_b = tk.Button(self.frame, text=row_name,
            command=self.on_set_output_folder)
        self.output_folder_b.grid(row=row_n, column=0, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("w"))
        self.output_folder = None

        # Step -----------------------#
        row_name = "Step"
        row_n = self.rows[row_name]
        self.step_b = tk.Button(self.frame, text=row_name,
            command=self.on_step)
        self.step_b.grid(row=row_n, column=0, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("w"))

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

    # Functions --------------------------------------------------------------#

    def on_set_output_folder(self) :
        f = askdirectory()
        if f != None and f != '':
            self.output_folder = f
            self.run_b.config(state=tk.NORMAL)

    def on_outline_check(self) :
        self.outline = bool(self.outline_iv.get())

    def on_background_check(self) :
        self.background = bool(self.background_iv.get())

    def on_load_alpha_mask(self) :
        f = askopenfile(mode="rb", title="Select a mask file to load")
        if f :
            self.alpha_mask_image = Image.open(f.name).convert("RGBA")
            self.alpha_mask_data = None
            self.alpha_mask_cb.config(state=tk.NORMAL)
        else :
            self.alpha_mask_image = None
            self.alpha_mask_data = None
            self.alpha_mask_iv.set(0)
            self.alpha_mask_cb.config(state=tk.DISABLED)

    def on_alpha_mask_check(self) :
        self.alpha_mask = bool(self.alpha_mask_iv.get())

    def on_step(self) :
        self.on_run(step=True)

    def on_run(self, step=False) :

        def randomize(m, M) :
            if m == M :
                return m
            return np.random.randint(m, M)

        if  (not self.n_runs_e.valid and step) or \
            (not self.palettes_sr_min_e.valid) or \
            (not self.palettes_sr_max_e.valid) or \
            (not self.r_channel_br_min_e.valid) or \
            (not self.r_channel_br_max_e.valid) or \
            (not self.g_channel_br_min_e.valid) or \
            (not self.g_channel_br_max_e.valid) or \
            (not self.b_channel_br_min_e.valid) or \
            (not self.b_channel_br_max_e.valid) :
            print("Parameters not set correctly")
            return

        if (not step and not self.root.pixel_size_e.valid) :
            print("Pixel size not set correctly")
            return
       
        nr = 1
        if (not step) :
            nr = self.n_runs_e.value
        for i in range(nr) : 
            # Values from master
            fidelity = self.root.fidelity_e.get()
            out_size = (self.root.out_res_le.x_e.value, 
                self.root.out_res_le.y_e.value)
            # Values from here
            ps = randomize(self.palettes_sr_min_e.value,
                self.palettes_sr_max_e.value)
            rb = randomize(self.r_channel_br_min_e.value, 
                self.r_channel_br_max_e.value)
            gb = randomize(self.g_channel_br_min_e.value, 
                self.g_channel_br_max_e.value)
            bb = randomize(self.b_channel_br_min_e.value, 
                self.b_channel_br_max_e.value)
            # Run
            self.root.image_processor.process(
                palettesgridsize=(None, None), 
                palettesize=ps, 
                rgbbits=(rb,gb,bb), 
                fidelity=fidelity, 
                tilesize=(None, None), 
                outsize=out_size)

            palette = self.root.image_processor.palettes[0]
            if palette[-1][3] == 0 :
                palette = np.delete(palette, palette.shape[0]-1, axis=0)
            avg_color = (np.average(palette, axis=0)).astype(np.uint8)
            avg_color[3] = 255 # Just to be sure
            
            # Apply outline
            if self.outline :
                out_color = (avg_color/2).astype(np.uint8)
                out_color[3] = 255
                #print(out_color)
                self.root.image_processor.apply_shader_outline(
                    alphathreshold=127, 
                    outlinecolor=out_color)

            # Apply background
            if self.background :
                bkg_color = colorsys.rgb_to_hsv(avg_color[0], avg_color[1], 
                    avg_color[2])
                h = np.random.rand()
                bkg_color = colorsys.hsv_to_rgb(h, bkg_color[1], bkg_color[2])
                r, g, b = bkg_color
                self.root.image_processor.set_background_color(
                        np.array([r, g, b, 255]))

            # Apply alpha mask
            if self.alpha_mask and self.alpha_mask_value_e.valid :
                if self.alpha_mask_data is None :
                    o = self.root.image_processor.output_canvas.image_no_zoom_PIL_RGB
                    size = (o.width, o.height)
                    self.alpha_mask_data = np.array(
                        self.alpha_mask_image.resize(size, 
                        resample=Image.LANCZOS))
                alpha = self.alpha_mask_value_e.value
                self.root.image_processor.apply_alpha_mask(
                    self.alpha_mask_data, alpha)

            # Save
            if (not step) :
                if not self.root.pixel_size_e.valid :
                    return
                self.root.output_canvas.dialogless_save_image(
                    pixelsize = self.root.pixel_size_e.value,
                    outfolder = self.output_folder,
                    appendstr = f"_{i}"
                )

    def on_close(self) :
        self.root.on_open_gf_view()
        self.withdraw()