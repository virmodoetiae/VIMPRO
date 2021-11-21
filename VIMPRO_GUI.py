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
import sys
import logging
import numpy as np

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk

import VIMPRO_Processor as vp
import VIMPRO_Tkinter as vk
import VIMPRO_Data as vd

### DICTIONARIES ##############################################################

interpolation_modes = {"Bilinear" : Image.BILINEAR, "Bicubic" : Image.BICUBIC,
    "Nearest" : Image.NEAREST, "Lanczos" : Image.LANCZOS}

anchor_points = {"Center" : "c", "Top" : "n", "Top-right" : "ne", "Right" : "e", 
    "Bottom-right" : "se", "Bottom" : "s", "Bottom-left" : "sw",
    "Left" : "w", "Top-left" : "nw"}

### FUNCTIONS #################################################################

# Make grid stretchable
def stretch_grid(obj, **kwargs) :
        except_rows = kwargs.get("exceptrows", [])
        except_columns = kwargs.get("exceptcolumns", [])
        min_row_size = kwargs.get("minrowsize", 0)
        min_column_size = kwargs.get("mincolumnsize", 0)
        col_count, row_count = obj.grid_size()
        for col in range(col_count):
            w = 1
            if col in except_columns :
                w = 0
            obj.grid_columnconfigure(col, weight=w, minsize=min_column_size)
        for row in range(row_count):
            w = 1
            if row in except_rows :
                w = 0
            obj.grid_rowconfigure(row, weight=w, minsize=min_row_size)

### Classes ###################################################################

class GUI(tk.Tk) :

    def __init__(self, *args, **kwargs) :

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("VIMPRO - Virmodoetiae Image Processor")
        self.iconphoto(False, ImageTk.PhotoImage(vd.icon_image))
        self.bind("<Configure>", self.on_main_window_resize)
        self.frames = []
        
        # UI Layout ----------------------------------------------------------#
        self.label_width = 20
        self.button_width = 10
        self.entry_width = 8
        self.default_pad = 20
        self.pad0 = vk.Padding(self.default_pad, self.default_pad)
        self.pad1 = vk.Padding(self.default_pad/4, self.default_pad/8)

        self.left_frame = tk.Frame(self)
        self.left_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)
        self.right_frame = tk.Frame(self)
        self.right_frame.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S)
        self.frames.append(self.left_frame)
        self.frames.append(self.right_frame)
        
        #---------------------------------------------------------------------#
        # Input frame and canvas (NW) ----------------------------------------#
        self.input_frame = tk.LabelFrame(self.left_frame, text="Input")
        self.input_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            **self.pad0.get("nw"))
        self.frames.append(self.input_frame)
        self.input_canvas = vk.MouseScrollableImageCanvas(self.input_frame, 
            width=600, height=300)
        self.input_canvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        #---------------------------------------------------------------------#
        # Output frame and canvas (SW) ---------------------------------------#
        self.output_frame = tk.LabelFrame(self.left_frame, text="Output")
        self.output_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            **self.pad0.get("sw"))
        self.frames.append(self.output_frame)
        self.output_canvas = vk.MouseScrollableImageCanvas(self.output_frame, 
            width=600, height=300)
        self.output_canvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        # Image processor object
        self.image_processor = vp.ImageProcessor(self.input_canvas, 
            self.output_canvas)

        #---------------------------------------------------------------------#
        # Control frame (NE) -------------------------------------------------#
        self.ctrl_frame = tk.LabelFrame(self.right_frame, text="Controls", 
            height=12)
        self.ctrl_frame.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N, 
            **self.pad0.get("ne"))
        self.frames.append(self.ctrl_frame)
        n_cols = 5
        self.ctrl_rows = {"Input options" : 0, "Load image" : 1, 
            "Resize tool" : 2, "Crop tool" : 3, "Processing options" : 4, 
            "Processor mode" : 5,  "Compatibility mode" : 6, 
            "Palettes search grid size" : 7, "Palette size" : 8, 
            "Bits per channel (R,G,B)" : 9, "Fidelity" : 10, "Tile size" : 11, 
            "Tiles grid size" : 12, "Output resolution" : 12+1, 
            "Process image" : 13+1, "Save & export options" : 14+1, 
            "Pixel size" : 15+1, "Final resolution" : 16+1,
            "Save image" : 17+1, "Export .asm source" : 18+1}

        # Input options ------------------------------------------------------#
        row_name = "Input options"
        row_n = self.ctrl_rows[row_name]
        ttk.Separator(self.ctrl_frame, orient=tk.HORIZONTAL).grid(row=row_n, 
            column=0, columnspan=n_cols, sticky=tk.W+tk.E, 
            **self.pad1.get("c", "xy", True))
        tk.Label(self.ctrl_frame, text=row_name).grid(row=row_n, column=0, 
            padx=self.label_width, sticky=tk.W)

        # Load image
        row_name = "Load image"
        row_n = self.ctrl_rows[row_name]
        self.load_image_b = tk.Button(self.ctrl_frame, text=row_name,
            width=self.button_width, command=self.on_load_image)
        self.load_image_b.grid(row=row_n, column=0, sticky=tk.W+tk.E+tk.N, 
            **self.pad1.get("nw", "xx"))

        # Resize tool ----------------#
        row_name = "Resize tool"
        row_n = self.ctrl_rows[row_name]
        self.open_resize_b = vk.ToggleButton(self.ctrl_frame, text=row_name,
            width=self.button_width, command=self.on_open_resize)
        self.open_resize_b.grid(row=row_n, column=0, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("w", "xx"))

        # Resize frame
        self.resize_frame = tk.LabelFrame(self.ctrl_frame)
        self.frames.append(self.resize_frame)
        
        # Target resolution for resize
        self.resize_res_le = vk.ResolutionLabelEntry(self.resize_frame,
            row=0, col=0, minvalue=1, labeltext="Resolution",
            entrywidth=int(self.entry_width/2), pads=[self.pad1.get("nw"),
            self.pad1.get("n"), self.pad1.get("n"), self.pad1.get("ne")])

        # Interpolation mode
        interp_mode_l = tk.Label(self.resize_frame, text= "Interpolation")
        interp_mode_l.grid(row=1, column=0, sticky=tk.W, **self.pad1.get("w"))

        self.interp_mode_sv = tk.StringVar()
        self.interp_mode_om = ttk.OptionMenu(self.resize_frame, 
            self.interp_mode_sv, list(interpolation_modes.keys())[0],
            *list(interpolation_modes.keys()))
        self.interp_mode_om.grid(row=1, column=1, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("e"))

        # Actual resize and undo resize buttons
        self.resize_sub_frame = tk.Frame(self.resize_frame)
        self.resize_sub_frame.grid(row=2, column=0, columnspan=4,
            sticky=tk.W+tk.E+tk.N)
        self.frames.append(self.resize_sub_frame)

        self.resize_b = tk.Button(self.resize_sub_frame, text="Resize",
            command=self.on_resize)
        self.resize_b.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("sw"))

        # Undo resize button
        self.undo_resize_b = tk.Button(self.resize_sub_frame, text="Undo",
            command=self.on_undo_resize)
        self.undo_resize_b.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("se"))

        # Crop tool ------------------#
        row_name = "Crop tool"
        row_n = self.ctrl_rows[row_name]
        self.open_crop_b = vk.ToggleButton(self.ctrl_frame, text=row_name,
            width=self.button_width, command=self.on_open_crop)
        self.open_crop_b.grid(row=row_n, column=0, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("sw", "xx"))

        # Crop frame
        self.crop_frame = tk.LabelFrame(self.ctrl_frame)
        self.frames.append(self.crop_frame)

        # Target resolution for crop
        self.crop_res_le = vk.ResolutionLabelEntry(self.crop_frame, 
            row=0, col=0, minvalue=1, labeltext="Resolution",
            entrywidth=int(self.entry_width/2), pads=[self.pad1.get("nw"), 
            self.pad1.get("n"), self.pad1.get("n"), self.pad1.get("ne")])

        # Cropping anchor
        crop_anchor_l = tk.Label(self.crop_frame, text= "Crop anchor")
        crop_anchor_l.grid(row=1, column=0, sticky=tk.W, **self.pad1.get("w"))

        self.crop_anchor_sv = tk.StringVar()
        self.crop_anchor_om = ttk.OptionMenu(self.crop_frame, 
            self.crop_anchor_sv, list(anchor_points.keys())[0], 
            *list(anchor_points.keys()))
        self.crop_anchor_om.grid(row=1, column=1, columnspan=3,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("e"))

        # Selection tool, do crop and undo crop
        self.crop_sub_frame = tk.Frame(self.crop_frame)
        self.crop_sub_frame.grid(row=2, column=0, columnspan=4, 
            sticky=tk.W+tk.E+tk.N)
        self.frames.append(self.crop_sub_frame)

        self.selection_tool_b = vk.ToggleButton(self.crop_sub_frame, 
            text="Selection", command=self.on_selection_tool)
        self.selection_tool_b.grid(row=0, column=0, 
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("sw"))

        self.crop_b = tk.Button(self.crop_sub_frame, text="Crop", 
            command=self.on_crop)
        self.crop_b.grid(row=0, column=1, 
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("sw"))

        self.undo_crop_b = tk.Button(self.crop_sub_frame, text="Undo",
            command=self.on_undo_crop)
        self.undo_crop_b.grid(row=0, column=2,
            sticky=tk.W+tk.E+tk.N, **self.pad1.get("se"))

        # Initial status for all undo buttons is off
        self.update_undo_b()

        # Link selection tool to input canvas
        self.input_canvas.selection_tool_b = self.selection_tool_b
        
        # Processing options -------------------------------------------------#
        row_name = "Processing options"
        row_n = self.ctrl_rows[row_name]
        ttk.Separator(self.ctrl_frame, orient=tk.HORIZONTAL).grid(row=row_n,
            column=0, columnspan=n_cols, sticky=tk.W+tk.E, 
            **self.pad1.get("c", "xy", True))
        tk.Label(self.ctrl_frame, text=row_name).grid(row=row_n, column=0,
            padx=self.label_width, sticky=tk.W)

        # Number of palettes -------------#
        row_name = "Palettes search grid size"
        row_n = self.ctrl_rows[row_name]
        self.palettes_grid_l = tk.Label(self.ctrl_frame, text=row_name, 
            anchor=tk.W)
        self.palettes_grid_x_e = vk.IntEntry(self.ctrl_frame, 
            width=self.entry_width)
        self.palettes_grid_x_e.set_min_value(1)
        self.palettes_grid_x_e.set(4)
        self.palettes_grid_y_e = vk.IntEntry(self.ctrl_frame, 
            width=self.entry_width)
        self.palettes_grid_y_e.set_min_value(1)
        self.palettes_grid_y_e.set(2)

        # Processor mode -------------#
        # This should come first, but the option menu needs to be tied to
        # the creation-destruction of additional entries/labels when a certain
        # proc_mode_om is selected. The show/hide functionality of these
        # fields needs to be passed as command, but this means that I cannot
        # create proc_mode_om until after I have created all the
        # entries/labels that are referenced by the command. Thus, proc_mode
        # is created at the end
        row_name = "Processor mode"
        row_n = self.ctrl_rows[row_name]
        proc_mode_l = tk.Label(self.ctrl_frame, text=row_name)
        proc_mode_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))

        self.prev_proc_mode = None
        self.proc_mode_sv = tk.StringVar()
        self.proc_mode_sv.set(self.image_processor.proc_modes[0])
        self.proc_mode_om = ttk.OptionMenu(self.ctrl_frame, self.proc_mode_sv,
            self.image_processor.proc_modes[0], 
            *self.image_processor.proc_modes, command=self.on_proc_mode)
        self.proc_mode_om.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))

        # Compatibility mode
        row_name = "Compatibility mode"
        row_n = self.ctrl_rows[row_name]
        comp_mode_l = tk.Label(self.ctrl_frame, text=row_name)
        comp_mode_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))

        self.prev_comp_mode = None
        self.comp_mode_sv = tk.StringVar()
        self.comp_mode_sv.set(self.image_processor.comp_modes[0])
        self.comp_mode_om = ttk.OptionMenu(self.ctrl_frame, self.comp_mode_sv,
            self.image_processor.comp_modes[0], 
            *self.image_processor.comp_modes, command=self.on_comp_mode)
        self.comp_mode_om.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))

        # Palette size ---------------#
        row_name = "Palette size"
        row_n = self.ctrl_rows[row_name]
        palette_size_l = tk.Label(self.ctrl_frame, text=row_name, anchor=tk.W)
        palette_size_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))
        self.palette_size_e = vk.IntEntry(self.ctrl_frame, 
            width=self.entry_width)
        self.palette_size_e.set(4)
        self.palette_size_e.set_min_value(1)
        self.palette_size_e.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))

        # Number of palettes (only if self.proc_mode_om == Tiled or GameBoy)
        # Left empty row at proc_start_row + 3
        
        # RGB channel bits ------------#
        row_name = "Bits per channel (R,G,B)"
        row_n = self.ctrl_rows[row_name]
        bits_per_channel_l = tk.Label(self.ctrl_frame, text= row_name,
            anchor=tk.W, width=self.label_width)
        bits_per_channel_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))

        self.bits_R_e = vk.IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_R_e.set(16)
        self.bits_R_e.set_min_value(2)
        self.bits_R_e.set_max_value(16)
        self.bits_R_e.grid(row=row_n, column=1, sticky=tk.W+tk.E,
            **self.pad1.get("c"))
        
        self.bits_G_e = vk.IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_G_e.set(16)
        self.bits_G_e.set_min_value(2)
        self.bits_G_e.set_max_value(16)
        self.bits_G_e.grid(row=row_n, column=2, sticky=tk.W+tk.E,
            **self.pad1.get("c"))
        
        self.bits_B_e = vk.IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_B_e.set(16)
        self.bits_B_e.set_min_value(2)
        self.bits_B_e.set_max_value(16)
        self.bits_B_e.grid(row=row_n, column=3, sticky=tk.W+tk.E,
            **self.pad1.get("e"))

        self.bits_buffer = (self.bits_R_e.value, self.bits_G_e.value, 
            self.bits_B_e.value)

        # Color fidelity -------------#
        row_name = "Fidelity"
        row_n = self.ctrl_rows[row_name]
        fidelity_l = tk.Label(self.ctrl_frame, text=row_name, anchor=tk.W,
            width=self.label_width)
        fidelity_l.grid(row=row_n, column=0, sticky=tk.W, **self.pad1.get("w"))

        self.fidelity_e = tk.Scale(self.ctrl_frame, from_=1, to=10,
            orient=tk.HORIZONTAL, showvalue=False)
        self.fidelity_e.set(4) # Default value
        self.fidelity_e.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))

        # Tile size ------------------#
        row_name = "Tile size"
        row_n = self.ctrl_rows[row_name]
        self.tile_size_l = tk.Label(self.ctrl_frame, text=row_name, 
            anchor=tk.W)
        self.tile_size_e_x = vk.IntEntry(self.ctrl_frame, 
            width=self.entry_width)
        self.tile_size_e_x.set_min_value(1)
        self.tile_size_e_x.set(8)
        self.tile_size_e_y = vk.IntEntry(self.ctrl_frame, 
            width=self.entry_width)
        self.tile_size_e_y.set_min_value(1)
        self.tile_size_e_y.set(8)

        # Tiles grid size ------------#
        row_name = "Tiles grid size"
        row_n = self.ctrl_rows[row_name]
        self.tiles_grid_le = vk.ResolutionLabelEntry(self.ctrl_frame, row=row_n,
            col=0, minvalue=1, labeltext=row_name, labelwidth=self.label_width,
            entrywidth=self.entry_width, pads=[self.pad1.get("w"), 
            self.pad1.get("c"), self.pad1.get("c"), self.pad1.get("e")], 
            starthidden=True)
        self.tiles_grid_le.enable_auto_write_buffer("ref")

        # Output resolution ----------#
        row_name = "Output resolution"
        row_n = self.ctrl_rows[row_name]
        self.out_res_le = vk.ResolutionLabelEntry(self.ctrl_frame, row=row_n,
            col=0, minvalue=1, labeltext=row_name, labelwidth=self.label_width,
            entrywidth=self.entry_width, pads=[self.pad1.get("w"), 
            self.pad1.get("c"), self.pad1.get("c"), self.pad1.get("e")])
        self.out_res_le.enable_auto_write_buffer("ref")

        # Process image --------------#
        row_name = "Process image"
        row_n = self.ctrl_rows[row_name]
        self.process_image_b = tk.Button(self.ctrl_frame, 
            width=self.button_width, text=row_name, command=self.process_image)
        self.process_image_b.grid(row=row_n, column=0, sticky=tk.W+tk.E, 
            **self.pad1.get("sw", "xx"))
        
        # Save & export optionss ---------------------------------------------#
        row_name = "Save & export options"
        row_n = self.ctrl_rows[row_name]
        ttk.Separator(self.ctrl_frame, orient=tk.HORIZONTAL).grid(row=row_n,
            column=0, columnspan=n_cols, sticky=tk.W+tk.E, 
            **self.pad1.get("c", "xy", True))
        tk.Label(self.ctrl_frame, text=row_name).grid(row=row_n, column=0,
            padx=self.label_width, sticky=tk.W)

        # Pixel size -----------------#
        row_name = "Pixel size"
        row_n = self.ctrl_rows[row_name]
        pixel_size_l = tk.Label(self.ctrl_frame, text=row_name, anchor=tk.W,
            width=self.label_width)
        pixel_size_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("nw"))
        self.pixel_size_e = vk.IntEntry(self.ctrl_frame, width=self.entry_width)
        self.pixel_size_e.set(1)
        self.pixel_size_e.set_min_value(1)
        self.pixel_size_e.grid(row=row_n, column=1, sticky=tk.W,
            **self.pad1.get("ne"))

        # Final output resolution of the save file
        row_name = "Final resolution"
        row_n = self.ctrl_rows[row_name]
        save_res_l = tk.Label(self.ctrl_frame, text=row_name, anchor=tk.W)
        save_res_l.grid(row=row_n, column=0, sticky=tk.W, **self.pad1.get("w"))
        self.save_res_sv = tk.StringVar(value="0 x 0")
        save_res_val_l = tk.Label(self.ctrl_frame, anchor=tk.W,
            textvariable=self.save_res_sv)
        save_res_val_l.grid(row=row_n, column=1, columnspan=3, sticky=tk.W,
            **self.pad1.get("e"))
        
        # Save output image ----------#
        row_name = "Save image"
        row_n = self.ctrl_rows[row_name] 
        self.save_image_b = tk.Button(self.ctrl_frame, width=self.button_width,
            text=row_name, command=self.on_save_image)
        self.save_image_b.grid(row=row_n, column=0, sticky=tk.W+tk.E,
            **self.pad1.get("sw", "xx"))

        # Export .asm code -----------#
        row_name = "Export .asm source"
        row_n = self.ctrl_rows[row_name] 
        self.export_asm_b = tk.Button(self.ctrl_frame, width=self.button_width,
            text=row_name, command=self.on_export_asm)
        self.export_asm_b.grid(row=row_n, column=0, sticky=tk.W+tk.E,
            **self.pad1.get("sw", "xx"))

        # Add functionality at the end to avoid potential issues regarding
        # referencing missing variables
        self.tile_size_e_x.trace("w", self.on_write_tile_size_x)
        self.tile_size_e_y.trace("w", self.on_write_tile_size_y)
        self.pixel_size_e.trace("w", self.on_write_pixel_size)

        #---------------------------------------------------------------------#
        # Logging frame (SE) -------------------------------------------------#
        #self.log_frame = tk.LabelFrame(self.right_frame, text="Log")
        #self.log_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S,
        #    **self.pad0.get("se")
        #self.frames.append(self.log_frame)
        
        # Create logging text box and divert sys.stdout to it
        #self.log_t = tk.Text(self.log_frame, bg='black', fg="white", width=4, 
        #    height=10)
        #self.log_t.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S,
        #    **self.pad1.get("n", "xx", True))
        #sys.stdout = StdoutDirector(self.log_t)

        #-End of UI layout ---------------------------------------------------#

        # Additional initialization
        self.update_proc_mode() # Init out_res_le buffers

        # Formatting 
        stretch_grid(self)
        for frame in self.frames :
            stretch_grid(frame, minrowsize=25, mincolumnsize=25)

    #-Start of class methods -------------------------------------------------#

    # Methods are in order of appearance in the UI (top-bottom, left-right)
    # rather than alphabetical

    def on_load_image(self) :
        # Load image
        previous_filename = self.input_canvas.filename
        try :
            old_x = self.input_canvas.image_no_zoom_PIL.width
        except :
            old_x = 0
        try :
            old_y = self.input_canvas.image_no_zoom_PIL.height
        except :
            old_y = 0
        self.input_canvas.load_draw_image()
        # If an image was actually loaded (it might be that the user just
        # closed the window without loading anything)
        if self.input_canvas.image :
            new_x = self.input_canvas.image_no_zoom_PIL.width
            new_y = self.input_canvas.image_no_zoom_PIL.height

            # Update output image resolution fields to default to input image
            # size
            if (self.input_canvas.filename != previous_filename or 
                (old_x != new_x or old_y != new_y)) :
                self.out_res_le.set_buffer("orig", (new_x, new_y))
                self.update_all_res_entries(new_x, new_y)
                self.update_proc_mode()
            
            # Toggle aspect ratio locks on after loading
            self.resize_res_le.aspect_ratio_b.toggle_on()
            self.crop_res_le.aspect_ratio_b.toggle_on()
            self.out_res_le.aspect_ratio_b.toggle_on()

    def on_open_resize(self) :
        # First, close the cropping tool if open
        if self.open_crop_b.toggled :
            self.on_open_crop() 

        self.open_resize_b.on_toggle_change()
        if self.open_resize_b.toggled :
            self.resize_frame.grid(row=1, column=1, rowspan=3, columnspan=4,
                sticky=tk.W+tk.E+tk.N+tk.S, **self.pad1.get("w", "xx", True))
        else :
            self.resize_frame.grid_forget()
            self.resize_res_le.set((self.input_canvas.image_no_zoom_PIL.width,
                self.input_canvas.image_no_zoom_PIL.height))

    def on_resize(self) :
        if not self.resize_res_le.valid() :
            print("Cannot resize image because of invalid target resolution")
            return
        x = self.resize_res_le.x_e.value
        y = self.resize_res_le.y_e.value
        if (x != self.input_canvas.image_no_zoom_PIL.width and
            y != self.input_canvas.image_no_zoom_PIL.height) :
            self.input_canvas.resize_image(x, y, 
                interpolation_modes[self.interp_mode_sv.get()])
            self.out_res_le.set_buffer("orig", (x, y))
            self.update_all_res_entries(x, y)
            self.update_undo_b()
            self.update_proc_mode()

    def on_undo_resize(self) :
        if self.input_canvas.undo_buffer :
            x = self.input_canvas.undo_buffer.width
            y = self.input_canvas.undo_buffer.height
            self.out_res_le.set_buffer("orig", (x, y))
            self.update_all_res_entries(x, y)
        self.input_canvas.undo()
        self.update_undo_b()
        self.update_proc_mode()

    def on_open_crop(self) :
        # First, close the resize tool if open
        if self.open_resize_b.toggled :
            self.on_open_resize()

        self.open_crop_b.on_toggle_change()
        if self.open_crop_b.toggled :
            self.crop_frame.grid(row=1, column=1, rowspan=3, columnspan=4,
                sticky=tk.W+tk.E+tk.N+tk.S, **self.pad1.get("w", "xx", True))
        else :
            # When closing the crop window, make sure to delete any selections
            if self.selection_tool_b.toggled :
                self.on_selection_tool()
            self.input_canvas.delete_selection_rectangle()
            self.crop_frame.grid_forget()
            self.crop_res_le.set((self.input_canvas.image_no_zoom_PIL.width,
                self.input_canvas.image_no_zoom_PIL.height))

    def on_selection_tool(self) :
        self.selection_tool_b.on_toggle_change()
        if self.selection_tool_b.toggled :
            self.crop_res_le.disable()
        else :
            self.crop_res_le.enable()
            self.input_canvas.delete_selection_rectangle()

    def on_crop(self) :
        selection_box = None
        flag = False
        if self.selection_tool_b.toggled :
            selection_box = tuple(
                self.input_canvas.selection_rectangle.coords_rel_scaled)
            self.on_selection_tool()
        if selection_box :
            self.input_canvas.crop_image(box=selection_box)
            flag = True
        else :
            if not self.crop_res_le.valid() :
                print("Cannot crop because of invalid resolution")
                return
            x = self.crop_res_le.x_e.value
            y = self.crop_res_le.y_e.value
            if (x < self.input_canvas.image_no_zoom_PIL.width or 
                y < self.input_canvas.image_no_zoom_PIL.height) :
                self.input_canvas.crop_image(anchor=anchor_points[
                    self.crop_anchor_sv.get()], size=(x,y))
                flag = True
        if flag :
            self.update_undo_b()
            x = self.input_canvas.image_no_zoom_PIL.width
            y = self.input_canvas.image_no_zoom_PIL.height
            self.out_res_le.set_buffer("orig", (x, y))
            self.update_all_res_entries(x, y)
            self.update_proc_mode()

    def on_undo_crop(self) :
        if self.input_canvas.undo_buffer :
            x = self.input_canvas.undo_buffer.width
            y = self.input_canvas.undo_buffer.height
            self.out_res_le.set_buffer("orig", (x, y))
            self.update_all_res_entries(x, y)
        self.input_canvas.undo()
        self.update_undo_b()
        self.update_proc_mode()

    def on_proc_mode(self, *args, **kwargs) :
        proc_mode = self.proc_mode_sv.get()
        if (self.prev_proc_mode != proc_mode) :
            self.update_proc_mode(**kwargs)
        self.prev_proc_mode = proc_mode  

    def update_proc_mode(self, **kwargs) :
        proc_mode = self.proc_mode_sv.get()
        comp_mode = self.comp_mode_sv.get()
        row_name = "Palettes search grid size"
        row_n = self.ctrl_rows[row_name]

        if proc_mode == self.image_processor.default_proc_mode_name :
            self.palettes_grid_l.grid_forget()
            self.palettes_grid_x_e.grid_forget()
            self.palettes_grid_y_e.grid_forget()
            self.tile_size_l.grid_forget()
            self.tile_size_e_x.grid_forget()
            self.tile_size_e_y.grid_forget()
            
            self.tiles_grid_le.hide()
            self.tiles_grid_le.free_slave()
            self.out_res_le.enable()
            self.out_res_le.show_aspect_ratio_b()
            self.out_res_le.set_slave(self.tiles_grid_le)

            if (self.prev_proc_mode == 
                self.image_processor.tiled_proc_mode_name) :
                self.out_res_le.reset_from_buffer("orig")

            if comp_mode == self.image_processor.GBC_comp_mode_name :
                self.out_res_le.set_buffer("GBC")
                self.out_res_le.set((160, 148))
                self.out_res_le.disable()
            else : 
                self.out_res_le.enable()
        
        elif proc_mode == self.image_processor.tiled_proc_mode_name :
            row_name = "Palettes search grid size"
            row_n = self.ctrl_rows[row_name]
            self.palettes_grid_l.grid(row=row_n, column=0,
                sticky=tk.W+tk.E, **self.pad1.get("w"))
            self.palettes_grid_x_e.grid(row=row_n, column=1,
                sticky=tk.W+tk.E, **self.pad1.get("e"))
            self.palettes_grid_y_e.grid(row=row_n, column=2,
                sticky=tk.W+tk.E, **self.pad1.get("e"))
            row_name = "Tile size"
            row_n = self.ctrl_rows[row_name]
            self.tile_size_l.grid(row=row_n, column=0,
                sticky=tk.W+tk.E, **self.pad1.get("w"))
            self.tile_size_e_x.grid(row=row_n, column=1,
                sticky=tk.W+tk.E, **self.pad1.get("c"))
            self.tile_size_e_y.grid(row=row_n, column=2,
                sticky=tk.W+tk.E, **self.pad1.get("e"))

            if (self.prev_proc_mode == 
                self.image_processor.default_proc_mode_name) :
                self.out_res_le.set_buffer("orig")

            self.out_res_le.disable()
            self.out_res_le.hide_aspect_ratio_b()
            self.out_res_le.free_slave()
            self.tiles_grid_le.show()
            self.tiles_grid_le.set_slave(self.out_res_le, 
                xyscales=(self.tile_size_e_x, self.tile_size_e_y))
            
            if self.input_canvas.image :
                if (self.out_res_le.valid() and self.tile_size_e_x.valid
                    and self.tile_size_e_y.valid) :
                    x = int(np.floor(self.out_res_le.buffers["ref"][0]/
                        self.tile_size_e_x.value))
                    y = int(np.floor(self.out_res_le.buffers["ref"][1]/
                        self.tile_size_e_y.value))
                    self.tiles_grid_le.set((x, y))

            if comp_mode == self.image_processor.GBC_comp_mode_name :
                self.tiles_grid_le.set_buffer("GBC")
                self.out_res_le.set_buffer("GBC")
                self.out_res_le.set((160, 148))
                self.out_res_le.disable()

    def on_comp_mode(self, *args, **kwargs) :
        comp_mode = self.comp_mode_sv.get()
        if (self.prev_comp_mode != comp_mode) :
            self.update_comp_mode(**kwargs)
        self.prev_comp_mode = comp_mode  

    def update_comp_mode(self, *args) :
        comp_mode = self.comp_mode_sv.get()
        proc_mode = self.proc_mode_sv.get()
        if (comp_mode == self.image_processor.GBC_comp_mode_name) :
            self.palette_size_e.set_max_value(4)
            self.bits_buffer = (self.bits_R_e.value, self.bits_G_e.value, 
                self.bits_B_e.value)
            self.bits_R_e.set(5)
            self.bits_G_e.set(5)
            self.bits_B_e.set(5)
            self.bits_R_e.disable()
            self.bits_G_e.disable()
            self.bits_B_e.disable()
            self.tile_size_e_x.set(8)
            self.tile_size_e_x.disable()
            self.tile_size_e_y.set(8)
            self.tile_size_e_y.disable()
            self.tiles_grid_le.set_buffer("GBC")
            self.out_res_le.set_buffer("GBC")
            self.tiles_grid_le.set((20, 18))
            self.tiles_grid_le.disable()
            self.out_res_le.set((160, 148))
            self.out_res_le.disable()

        elif (comp_mode == self.image_processor.default_comp_mode_name) :
            self.palette_size_e.unset_max_value()
            self.bits_R_e.set(self.bits_buffer[0])
            self.bits_G_e.set(self.bits_buffer[1])
            self.bits_B_e.set(self.bits_buffer[2])
            self.bits_R_e.enable()
            self.bits_G_e.enable()
            self.bits_B_e.enable()
            self.tile_size_e_x.enable()
            self.tile_size_e_y.enable()
            self.tiles_grid_le.enable()
            if  (proc_mode == self.image_processor.default_proc_mode_name) :
                self.out_res_le.enable()
            self.tiles_grid_le.reset_from_buffer("GBC")
            self.out_res_le.reset_from_buffer("GBC")

    def on_write_tile_size_x(self, *args) :
        self.tile_size_e_x.on_write()
        x0, y0 = self.out_res_le.buffers["ref"]
        x = int(x0/self.tile_size_e_x.value)
        
        prev_state = self.tiles_grid_le.aspect_ratio_b.toggled
        if prev_state == True :
            self.tiles_grid_le.on_toggle_aspect_ratio()
        self.tiles_grid_le.disable_auto_write_buffer()
        self.out_res_le.disable_auto_write_buffer()
        self.tiles_grid_le.set_x(x)
        self.tiles_grid_le.enable_auto_write_buffer("ref")
        self.out_res_le.enable_auto_write_buffer("ref")
        if prev_state == True :
            self.tiles_grid_le.on_toggle_aspect_ratio()

    def on_write_tile_size_y(self, *args) :
        self.tile_size_e_y.on_write()
        x0, y0 = self.out_res_le.buffers["ref"]
        y = int(y0/self.tile_size_e_y.value)
        
        prev_state = self.tiles_grid_le.aspect_ratio_b.toggled
        if prev_state == True :
            self.tiles_grid_le.on_toggle_aspect_ratio()
        self.tiles_grid_le.disable_auto_write_buffer()
        self.out_res_le.disable_auto_write_buffer()
        self.tiles_grid_le.set_y(y)
        self.tiles_grid_le.enable_auto_write_buffer("ref")
        self.out_res_le.enable_auto_write_buffer("ref")
        if prev_state == True :
            self.tiles_grid_le.on_toggle_aspect_ratio()
    
    def on_write_pixel_size(self, *args) :
        self.pixel_size_e.on_write(args)
        self.update_save_resolution()

    def on_save_image(self) :
        if not self.pixel_size_e.valid :
            print("Cannot save output because of invalid pixel size")
            return
        pixel_size = self.pixel_size_e.value
        self.output_canvas.save_image(pixelsize=pixel_size, 
            appendstr="_VIMPRO_")

    def on_export_asm(self) :
        pass

    def on_main_window_resize(self, *args) :
        pass

    # From here on, the ordering is alphabetical

    def process_image(self) :
        proc_mode =self.proc_mode_sv.get()

        # Check input data validity
        if not self.input_canvas.image_id :
            print("Cannot run processor because no input image loaded")
            return
        if not self.palette_size_e.valid :
            print("Cannot run processor because of invalid color palette size")
            return
        if not self.out_res_le.valid() :
            print("Cannot run processor because of invalid resolution")
            return
        if (not self.bits_R_e.valid or not self.bits_G_e.valid or not 
            self.bits_B_e.valid) :
            print("Cannot run processor because of invalid RGB channel bits")
            return
        if proc_mode == self.image_processor.tiled_proc_mode_name :
            if not (self.palettes_grid_x_e.valid and 
                self.palettes_grid_y_e.valid):
                print("Cannot run processor because of invalid number of \
                    palettes")
                return
            if not (self.tile_size_e_x.valid or not self.tile_size_e_y.valid) :
                print("Cannot run processor because of invalid tile size")
                return
            if not self.tiles_grid_le.valid() :
                print("Cannot run processor because of invalid number tiles \
                 grid size")
                return
        # Get input data. Note that everything here is an IntEntry object, 
        # which implements the value attribute. Fidelity isn't, so I use get
        palettes_grid_size = (self.palettes_grid_x_e.value, 
            self.palettes_grid_y_e.value)
        palette_size = self.palette_size_e.value
        rgb_bits = [self.bits_R_e.value, self.bits_G_e.value, 
            self.bits_B_e.value]
        fidelity = self.fidelity_e.get()
        tile_size = (self.tile_size_e_x.value, self.tile_size_e_y.value)
        out_size = (self.out_res_le.x_e.value, self.out_res_le.y_e.value)
        if proc_mode == self.image_processor.tiled_proc_mode_name :
            out_size = (self.tiles_grid_le.x_e.value, 
                self.tiles_grid_le.y_e.value)

        # Run processor
        self.image_processor.process(procmode=proc_mode, palettesgridsize=
            palettes_grid_size, palettesize=palette_size, rgbbits=rgb_bits, 
            fidelity=fidelity, tilesize=tile_size, outsize=out_size)

        # Update output resolution of the possible save file
        self.update_save_resolution()

    def update_all_res_entries(self, x, y) :
        self.resize_res_le.set((x, y))
        self.crop_res_le.x_e.set_max_value(x)
        self.crop_res_le.y_e.set_max_value(y)
        self.crop_res_le.set((x, y))
        self.out_res_le.set((x, y))
        # Set max values on the cropping field to prevent useless cropping when
        # the target crop resolution is larger than the current image
        # resolution
        
    def update_save_resolution(self) :
        if not self.pixel_size_e.valid :
            return
        pixel_size = self.pixel_size_e.value
        x = 0
        y = 0
        try :
            x = self.output_canvas.image_no_zoom_PIL.width
            y = self.output_canvas.image_no_zoom_PIL.height
        except :
            pass # Not good practice, I know, but I really an info-less except
        self.save_res_sv.set(str(int(pixel_size*x))+
            " x "+str(int(pixel_size*y)))

    def update_undo_b(self) :
        if not self.input_canvas.undo_buffer :
            self.undo_resize_b.config(state=tk.DISABLED)
            self.undo_crop_b.config(state=tk.DISABLED)
        else :
            self.undo_resize_b.config(state=tk.NORMAL)
            self.undo_crop_b.config(state=tk.NORMAL)
