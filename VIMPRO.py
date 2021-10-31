'''
###############################################################################
##                                                                           ##
##             _________________________________    _________   _________    ##
##            // ____  _____  _________________/   // ____  /  // ____  /    ##
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
'''

### IMPORTS ###################################################################

import sys
import time
import math
import random
import logging
import numpy as np
import tkinter as tk
from PIL import Image, ImageOps, ImageTk
from tkinter.filedialog import askopenfile, asksaveasfile

### FUNCTIONS #################################################################

# Setting weights to 1 for a col and/or row makes it stretchable
def config_rows_cols(obj) :
    col_count, row_count = obj.grid_size()
    for col in range(col_count):
        root.grid_columnconfigure(col, weight=1)
    for row in range(row_count):
        obj.grid_rowconfigure(row, weight=1)

### Classes ###################################################################

# k-means algorithm that takes advantage of numpy. Operates on np.arrays
class KMeans :

    # Items is 2D np array
    def __init__(self, Items, k, fidelity, print_=False) :
        self.Items = Items
        self.n = Items.shape[0]
        self.d = Items.shape[1]
        self.k = k
        self.meanItems = np.empty((0, self.d))
        self.clusters = []

        # Set iteration parameters from fidelity (this is all harcoded based
        # on what I saw works best, on average, according to my expectations)
        self.max_outer_iter = int(fidelity*2)
        self.min_rel_cluster_size = (fidelity*1.5)*0.02
        self.inner_iter_abs_tol = (1.0/5.0)**(fidelity-1)
        
        self.print_ = print_
        self.findClusters()
        
    def findClusters(self) :
        if self.n <= self.k :
            self.meanItems = self.Items
        outer_flag = True
        outer_iter = 0
        while (outer_flag and outer_iter < self.max_outer_iter) :

            # Init random clusters
            meanItems = np.empty_like(self.meanItems)
            clusters = []
            while meanItems.shape[0] < self.k :
                item = self.Items[random.randint(0, self.n-1)]
                if item not in meanItems :
                    meanItems = np.append(meanItems,
                        item.reshape((1, self.d)), axis=0)
                    clusters.append([item])
            for item in self.Items :
                dists = np.sum(np.square(item-meanItems), axis=1)
                mini = np.argmin(dists, axis=0)
                minDist = dists[mini]
                if minDist > 1e-69 :
                    clusters[mini].append(item)

            # Iteratively refine clusters
            inner_flag = True
            inner_iter = 0
            rms_0 = 0
            residual = 1
            while inner_flag :
                rms = 0
                for i, cluster in enumerate(clusters) :
                    meanItem = np.sum(cluster, axis=0)/max(
                            len(cluster),1)
                    rms += np.sum(np.square(meanItem - meanItems[i]), axis=0)
                    meanItems[i] = meanItem
                clusters = []
                for i in range(self.k) :
                    clusters.append([])
                for item in self.Items :
                    dists = np.sum(np.square(item-meanItems), axis=1)
                    mini = np.argmin(dists, axis=0)
                    minDist = dists[mini]
                    if minDist > 1e-69 :
                        clusters[mini].append(item)
                if (inner_iter > 0) :
                    residual = rms/rms_0
                else :
                    rms_0 = rms
                if self.print_ :
                    print("Processor status:", 
                        (outer_iter+1), "/", (inner_iter+1), "/", 
                        '{:.3E}'.format(residual), "/", 
                        self.min_rel_cluster_size)
                inner_flag = (residual > self.inner_iter_abs_tol)
                inner_iter += 1

            # Compute cluster sizes, if there are clusters that are too 
            # small (i.e. less a certain fraction of the expected average 
            # cluster size), start over
            sizes = []
            for cluster in clusters :
                sizes.append(len(cluster))
            minSize = self.min_rel_cluster_size*self.Items.shape[0]/self.k
            if min(sizes) <= minSize :
                outer_flag = True
            else :
                outer_flag = False
            
            #
            outer_iter += 1
        
        self.clusters = clusters
        self.meanItems = np.rint(meanItems)

#-----------------------------------------------------------------------------#

class ImageProcessor :

    def __init__(self, input_canvas, output_canvas) :
        self.input_canvas = input_canvas
        self.output_canvas = output_canvas
        self.palette = []
        self.max_pixels = 48*48
        self.n_colors = 0
        self.bits_R = 0
        self.bits_G = 0
        self.bits_B = 0
        self.fidelity = 0
        self.out_res_x = 0
        self.out_res_y = 0

    def crop(self, im) :
        width, height = im.size
        aspect_ratio = width/height
        target_aspect_ratio = self.out_res_x/self.out_res_y
        if abs((target_aspect_ratio-aspect_ratio)/target_aspect_ratio) > 0.01 :
            if aspect_ratio > target_aspect_ratio :
                target_width = height*target_aspect_ratio
                delta_width = int((width-target_width)/2)
                border = (delta_width, 0, width-delta_width, height)
            else :
                target_height = width/target_aspect_ratio
                delta_height = int((height-target_height)/2)
                border = (0, delta_height, width, height-delta_height)
            im = im.crop(border)
        return im.convert("RGB")

    def process_image(self) :
        # Load image as copy and resize to operate the kMeans on at most
        # self.max_pixels pixels (because it's time consuming), shape them into
        # a 1D array and operate k-means on them to find clusters of size 
        # n_colors
        input_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        width, height = input_image.size
        n_pixels = width*height
        scale = math.sqrt(self.max_pixels/n_pixels)
        input_image = self.crop(input_image) # Crop according to out asp. ratio
        if scale < 1.0 :
            input_image = input_image.resize((int(width*scale), 
                int(height*scale)))
        data = np.array(input_image)
        data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
        abs_tol = (1.0/5.0)**(self.fidelity)
        k_means = KMeans(data, self.n_colors, self.fidelity, True)

        # Prepare output image (cropping and such)
        start_time = time.time()
        output_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        output_image = self.crop(output_image)
        output_image = output_image.resize((self.out_res_x, self.out_res_y))

        # Convert color palette into 8 bit
        scale_8_bit = np.array([float(2**(self.bits_R-1))/255.0, 
            float(2**(self.bits_G-1))/255.0, float(2**(self.bits_B-1))/255.0])
        k_means.meanItems = np.rint(
            np.divide(
                np.rint(np.multiply(k_means.meanItems, scale_8_bit)), 
                scale_8_bit))

        # Replace colors in output with colors in palette
        data = np.array(output_image)
        orig_shape = data.shape
        data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
        for i, item in enumerate(data) :
            dists = np.sum(np.square(item-k_means.meanItems), axis=1)
            mini = np.argmin(dists, axis=0)
            minDist = dists[mini]
            if minDist > 1e-69 :
                data[i] = k_means.meanItems[mini]
        data = data.reshape(orig_shape)

        # Reassamble data into image, set and draw image to output canvas
        output_image = Image.fromarray(data)
        self.output_canvas.set_zoom_draw_image(output_image)

#-----------------------------------------------------------------------------#

# Class to handle the representation of a selection rectangle
class SelectionRectangle :

    def __init__(self, canvas, *args, **kwargs) :
        self.canvas = canvas
        self.coords_abs = [] # Absolute (i.e. with respect to canvas NW point)
        self.coords_rel = [] # Relative (i.e. with respect to image NW point)
        self.id = -1
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0
        self.id = canvas.create_line(
            min_x, max_y, 
            max_x, max_y,
            max_x, min_y,
            min_x, min_y,
            min_x, max_y,
            **kwargs)

    def resize(self, coords) :
        self.coords_abs = coords
        min_x = self.canvas.canvasx(coords[0])
        min_y = self.canvas.canvasy(coords[1])
        max_x = self.canvas.canvasx(coords[2])
        max_y = self.canvas.canvasy(coords[3])
        self.coords_rel = [min_x, min_y, max_x, max_y]
        self.canvas.coords(self.id,
            min_x, max_y, 
            max_x, max_y,
            max_x, min_y,
            min_x, min_y,
            min_x, max_y)

    def delete(self) :
        self.canvas.delete(self.id)

#-----------------------------------------------------------------------------#

class MouseScrollableImageCanvas(tk.Canvas):
    
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.configure(scrollregion=(0,0,1000,1000))
        self.image = ""
        self.image_no_zoom = ""
        self.image_no_zoom_PIL = ""
        self.image_no_zoom_PIL_RGB = ""
        self.image_id = -1
        self.image_scale = 1.0
        self.image_zoom_factor = 1.25
        self.image_aspect_ratio = 0.0
        self.filename = ""

        # Refs to last x,y mouse coordinate after dragging, needed to maintain
        # the output image in place after processing (i.e. avoiding re-setting
        # the output view everytime the input is reprocessed and the output
        # re-drawn)
        self.last_event_x = 0
        self.last_event_y = 0

        # Selection tool
        self.selection_tool_b = ""
        self.selection_coords = [0,0,0,0] # x, y min, x, y max
        self.selection_rectangle = ""
        
        # Mouse scrolling
        self.bind("<ButtonPress-1>", self.click)
        self.bind("<B1-Motion>", self.click_and_drag)
        self.bind("<ButtonRelease-1>", self.release_click)
        # Linux scroll
        self.bind("<Button-4>", self.zoomerP)
        self.bind("<Button-5>", self.zoomerM)
        # Windows scroll
        self.bind("<MouseWheel>",self.zoomer)

    # Scrolling
    def click(self, event):
        if self.selection_tool_b != "" : # If button is linked
            if self.selection_tool_b.toggled : # If button is on
                if self.selection_rectangle != "" : # If a selection exists
                    self.delete_selection()
                    self.selection_coords = [0,0,0,0]
                self.selection_coords[0] = event.x
                self.selection_coords[1] = event.y
                self.selection_rectangle = SelectionRectangle(self)
                return
            else :
                self.selection_coords = [0,0,0,0]
        self.scan_mark(event.x, event.y)

    def click_and_drag(self, event):
        if self.selection_tool_b != "" :
            if self.selection_tool_b.toggled :
                min_x = min(self.selection_coords[0], event.x)
                min_y = min(self.selection_coords[1], event.y)
                max_x = max(self.selection_coords[0], event.x)
                max_y = max(self.selection_coords[1], event.y)
                self.selection_rectangle.resize([min_x, min_y, max_x, max_y])
                self.selection_coords[2] = event.x
                self.selection_coords[3] = event.y
                return
            else :
                self.selection_coords = [0,0,0,0]
        self.last_event_x = event.x
        self.last_event_y = event.y
        self.scan_dragto(event.x, event.y, gain=1)

    def release_click(self, event) :
        if self.selection_tool_b != "" :
            if self.selection_tool_b.toggled :
                if (self.selection_coords[2] < self.selection_coords[0]) :
                    tmp = self.selection_coords[2]
                    self.selection_coords[2] = self.selection_coords[0]
                    self.selection_coords[0] = tmp
                if (self.selection_coords[3] < self.selection_coords[1]) :
                    tmp = self.selection_coords[3]
                    self.selection_coords[3] = self.selection_coords[1]
                    self.selection_coords[1] = tmp
                print(self.selection_coords)

    def delete_selection(self) :
        if self.selection_rectangle != "" :
            self.selection_rectangle.delete()
            self.selection_rectangle = ""
        self.selection_coords = [0,0,0,0]
                
    # Windows zoom
    def zoomer(self, event):
        if (event.delta > 0):
            self.image_scale *= self.image_zoom_factor
            #self.scale("all", event.x, event.y, 1.1, 1.1)
        elif (event.delta < 0):
            self.image_scale /= self.image_zoom_factor
            #self.scale("all", event.x, event.y, 0.9, 0.9)
        self.zoom_image(event.x, event.y)

    # Linux zoom
    def zoomerP(self, event):
        self.image_scale *= self.image_zoom_factor
        self.zoom_image(event.x, event.y)
        #self.scale("all", event.x, event.y, 1.1, 1.1)
    def zoomerM(self, event):
        self.image_scale /= self.image_zoom_factor
        self.zoom_image(event.x, event.y)
        #self.scale("all", event.x, event.y, 0.9, 0.9)

    # Actually zoom the picture
    def zoom_image(self, x, y) :
        if self.image_no_zoom_PIL == "" :
            return
        iw = int(self.image_no_zoom_PIL.width*self.image_scale)
        ih = int(self.image_no_zoom_PIL.height*self.image_scale)
        size = (iw, ih)
        i1 = self.image_no_zoom_PIL.resize(size, resample=Image.NEAREST)
        self.image = ImageTk.PhotoImage(i1)
        self.configure(scrollregion=(0, 0, self.image.width(), 
            self.image.height()))
        self.delete_selection()
        self.draw_image()
        '''
        ids = [i for i in self.find_all() if i != self.image_id]
        print(ids, self.image_scale)
        self.scale(ids, x, y, 
            self.image_scale, self.image_scale)
        '''

    # Set image from provided PIL image but do not draw
    def set_image(self, im) :
        self.image_no_zoom_PIL = im
        self.image_no_zoom_PIL_RGB = self.image_no_zoom_PIL.convert("RGB")
        self.image_no_zoom = ImageTk.PhotoImage(self.image_no_zoom_PIL_RGB)
        self.image = self.image_no_zoom
        self.image_aspect_ratio = self.image.width()/self.image.height()
        self.configure(scrollregion=(0, 0, self.image.width(), 
            self.image.height()))

    # Load image from file but do not draw
    def load_image(self) :
        self.image_scale = 1.0 # Re-set zoom level
        file = askopenfile(mode="rb", title="Select an image to load")
        if file :
            self.filename = (file.name.split("/")[-1]).split(".")[0]
            self.set_image(Image.open(file.name))

    # (Re-)Draw image on canvas
    def draw_image(self):
        if (self.image_id == -1) :
            self.image_id = self.create_image(0, 0, anchor='nw', 
                image=self.image)
        else :
            self.itemconfig(self.image_id, image=self.image)
        self.scan_dragto(self.last_event_x, self.last_event_y, gain=1)

    # Set passed image but zoom it to the level of the pre-existing image
    def set_zoom_draw_image(self, im):
        self.set_image(im)
        self.zoom_image(self.last_event_x, self.last_event_y)
        self.draw_image()

    # Set and draw passed image
    def set_draw_image(self, im):
        self.set_image(im)
        self.draw_image()

    # -Load and draw new image
    def load_draw_image(self):
        self.load_image()
        self.draw_image()

#-----------------------------------------------------------------------------#

#
class IntEntry(tk.Entry) :

    def __init__(self, *args, **kwargs) :
        tk.Entry.__init__(self, *args, **kwargs)
        self.sv = tk.StringVar()
        self.config(textvariable=self.sv)
        self.value = ""
        self.min_value = 0
        self.max_value = 1e69
        self.valid = False
        self.sv.trace_add("write", self.on_write)

    def on_write(self, *args) :
        try :
            self.value = max(min(int(self.sv.get()), self.max_value), 
                self.min_value)
            self.sv.set(self.value)
            self.valid = True
            self.config({"background": "White"})
        except :
            self.valid = False
            self.config({"background": "Red"})

    def set_value(self, value) :
        self.sv.set(value)
        self.on_write()

    def set_min_value(self, value) :
        self.min_value = value
        if not self.valid :
            self.sv.set(value)
        self.on_write()

    def set_max_value(self, value) :
        self.max_value = value
        if not self.valid :
            self.sv.set(value)
        self.on_write()

    # Method to overwrite trace_add if needed
    def trace_add(self, *args) :
        self.sv.trace_add(*args)

#-----------------------------------------------------------------------------#

class ToggleButton(tk.Button) :

    def __init__(self, *args, **kwargs) :
        tk.Button.__init__(self, *args, **kwargs, relief="raised", 
            command=self.on_toggle_change)
        self.toggled = False

    def on_toggle_change(self, *args) :
        self.toggled = not self.toggled
        if self.toggled :
            self.config(relief="sunken")
        else :
            self.config(relief="raised")

#-----------------------------------------------------------------------------#

# Classes for handling the log redirection
class IODirector(object):

    def __init__(self, log_t):
        self.log_t = log_t

class StdoutDirector(IODirector):

    def write(self, msg):
        self.log_t.update_idletasks()
        self.log_t.insert(tk.END, msg)
        self.log_t.yview(tk.END)
    def flush(self):
        pass

#-----------------------------------------------------------------------------#

class Application(tk.Tk) :

    def __init__(self, *args, **kwargs) :

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("VIMPRO - Virmodoetiae Image Processor")
        self.iconphoto(False, ImageTk.PhotoImage(file='icon.png'))
        self.bind("<Configure>", self.on_resize)
        self.frames = []
        
        # UI Layout ----------------------------------------------------------#
        pad0 = 20
        pad1 = pad0/4
        entry_size = 7
        label_size = 18

        #---------------------------------------------------------------------#
        # Input frame and canvas (NW) ----------------------------------------#
        self.frame0 = tk.LabelFrame(self, text="Input")
        self.frame0.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=(pad0, pad0/2), pady=(pad0, pad0/2))
        self.frames.append(self.frame0)
        self.input_canvas = MouseScrollableImageCanvas(self.frame0, width=600, 
            height=400)
        self.input_canvas.pack(fill=tk.BOTH)

        #---------------------------------------------------------------------#
        # Output frame and canvas (SW) ---------------------------------------#
        self.frame1 = tk.LabelFrame(self, text="Output")
        self.frame1.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=(pad0, pad0/2), pady=(pad0/2, pad0))
        self.frames.append(self.frame1)
        self.output_canvas = MouseScrollableImageCanvas(self.frame1, width=600, 
            height=400)
        self.output_canvas.pack(fill=tk.BOTH)

        # Image processor object
        self.image_processor = ImageProcessor(self.input_canvas, 
            self.output_canvas)

        #---------------------------------------------------------------------#
        # Control frame (NE) -------------------------------------------------#
        self.frame2 = tk.LabelFrame(self, text="Controls")
        self.frame2.grid(row=0, column=1, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=(pad0/2, pad0), pady=(pad0, pad0/2))
        self.frames.append(self.frame2)

        # Input options ------------------------------------------------------#
        self.in_opt = tk.LabelFrame(self.frame2, text="Input options")
        self.in_opt.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=pad1, pady=(pad1, pad1/2))

        # Image loading
        self.load_image_b = tk.Button(self.in_opt, 
            text="Load image", command=self.load_image)
        self.load_image_b.grid(row=0, column=0, sticky=tk.W+tk.E, 
            padx=(pad1, pad1/2), pady=(pad1, pad1/2))

        # Selection tool
        self.selection_tool_b = ToggleButton(self.in_opt,
            text="Selection tool")
        self.selection_tool_b.config(command=self.toggle_selection_tool)
        self.selection_tool_b.grid(row=0, column=1, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1), pady=(pad1, pad1/2))
        self.input_canvas.selection_tool_b = self.selection_tool_b
        
        # Processor options --------------------------------------------------#
        self.proc_opt = tk.LabelFrame(self.frame2, text="Processor options")
        self.proc_opt.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=pad1, pady=(pad1/2, pad1/2))
        
        # Number of colors
        colors_l = tk.Label(self.proc_opt, text="Number of colors", 
            anchor=tk.W, width=label_size)
        colors_l.grid(row=0, column=0, sticky=tk.W, 
            padx=(pad1, pad1/2), pady=(pad1, pad1/2))
        self.colors_e = IntEntry(self.proc_opt, width=entry_size)
        self.colors_e.set_value(4)
        self.colors_e.set_min_value(1)
        self.colors_e.grid(row=0, column=1, columnspan=2, sticky=tk.W, 
            padx=(pad1/2, pad1), pady=(pad1, pad1/2))

        # Bits per color channel
        bits_per_channel_l = tk.Label(self.proc_opt, 
            text= "Bits per channel (R,G,B)")
        bits_per_channel_l.grid(row=1, column=0, sticky=tk.W,
            padx=(pad1, pad1/2), pady=(pad1/2, pad1/2))
        
        self.bits_R_e = IntEntry(self.proc_opt, width=entry_size)
        self.bits_R_e.set_value(16)
        self.bits_R_e.set_min_value(2)
        self.bits_R_e.set_max_value(16)
        self.bits_R_e.grid(row=1, column=1, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1/2), pady=(pad1/2, pad1/2))
        
        self.bits_G_e = IntEntry(self.proc_opt, width=entry_size)
        self.bits_G_e.set_value(16)
        self.bits_G_e.set_min_value(2)
        self.bits_G_e.set_max_value(16)
        self.bits_G_e.grid(row=1, column=2, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1/2), pady=(pad1/2, pad1/2))
        
        self.bits_B_e = IntEntry(self.proc_opt, width=entry_size)
        self.bits_B_e.set_value(16)
        self.bits_B_e.set_min_value(2)
        self.bits_B_e.set_max_value(16)
        self.bits_B_e.grid(row=1, column=3, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1), pady=(pad1/2, pad1/2))

        # Color fidelity
        fidelity_l = tk.Label(self.proc_opt, text="Color fidelity", 
            anchor=tk.W, width=label_size)
        fidelity_l.grid(row=2, column=0, sticky=tk.W, 
            padx=(pad1, pad1/2), pady=(pad1/2, pad1/2))

        self.fidelity_e = tk.Scale(self.proc_opt, from_=1, to=10, 
            orient=tk.HORIZONTAL, showvalue=False)
        self.fidelity_e.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1), pady=(pad1/2, pad1/2))

        # Output resolution
        out_res_l = tk.Label(self.proc_opt, text="Output resolution", 
            anchor=tk.W, width=label_size)
        out_res_l.grid(row=3, column=0, sticky=tk.W, 
            padx=(pad1, pad1/2), pady=(pad1/2, pad1/2))
        
        self.out_res_x_e = IntEntry(self.proc_opt, width=entry_size)
        self.out_res_x_e.set_min_value(1)
        self.out_res_x_e.grid(row=3, column=1, sticky=tk.W, 
            padx=(pad1/2, pad1/2), pady=(pad1/2, pad1/2))
        
        self.out_res_y_e = IntEntry(self.proc_opt, width=entry_size)
        self.out_res_y_e.set_min_value(1)
        self.out_res_y_e.grid(row=3, column=3, sticky=tk.W, 
            padx=(pad1/2, pad1), pady=(pad1/2, pad1/2))
        
        self.aspect_ratio_i_lock = ImageTk.PhotoImage(file="lock.png")
        self.aspect_ratio_i_ulock =ImageTk.PhotoImage(file="ulock.png")
        self.aspect_ratio_b_status = 0
        self.aspect_ratio_b = tk.Button(self.proc_opt, bd=0,
            image=self.aspect_ratio_i_ulock, command=self.toggle_aspect_ratio)
        self.aspect_ratio_b.grid(row=3, column=2,
            padx=(pad1/2, pad1/2), pady=(pad1/2, pad1/2))

        # Process image
        process_image_b = tk.Button(self.proc_opt, 
            text="Process image", command=self.process_image)
        process_image_b.grid(row=10, column=0, sticky=tk.W, 
            padx=pad1, pady=(pad1/2, pad1))

        # Set entry functionality
        self.last_modified_out_res = "x"
        self.update_in_progress = False
        self.out_res_x_e.trace_add("write", self.update_out_res_x)
        self.out_res_y_e.trace_add("write", self.update_out_res_y)

        # Save options -------------------------------------------------------#
        self.save_opt = tk.LabelFrame(self.frame2, text="Save options")
        self.save_opt.grid(row=2, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            padx=pad1, pady=(pad1/2, pad1))

        # Pixel size
        pixel_size_l = tk.Label(self.save_opt, text="Pixel size", 
            anchor=tk.W, width=label_size)
        pixel_size_l.grid(row=0, column=0, sticky=tk.W, 
            padx=(pad1, pad1/2), pady=(pad1/2, pad1/2))
        self.pixel_size_e = IntEntry(self.save_opt, width=entry_size)
        self.pixel_size_e.set_value(1)
        self.pixel_size_e.set_min_value(1)
        self.pixel_size_e.grid(row=0, column=1, sticky=tk.W, 
            padx=(pad1/2, pad1), pady=(pad1, pad1/2))

        # Final output resolution
        final_out_res_l = tk.Label(self.save_opt, text="Final resolution", 
            anchor=tk.W, width=label_size)
        final_out_res_l.grid(row=1, column=0, sticky=tk.W, 
            padx=(pad1, pad1/2), pady=(pad1/2, pad1/2))
        self.final_out_res_sv = tk.StringVar(value="0 x 0")
        final_out_res_val_l = tk.Label(self.save_opt,
            textvariable=self.final_out_res_sv, anchor=tk.W)
        final_out_res_val_l.grid(row=1, column=1, sticky=tk.W+tk.E,
            padx=(pad1/2, pad1), pady=(pad1/2, pad1/2))
        self.update_final_resolution()

        # Save output image
        save_image_b = tk.Button(self.save_opt, text="Save image", 
            command=self.save_image)
        save_image_b.grid(row=2, column=0, sticky=tk.W, padx=pad1, 
            pady=(pad1/2, pad1))
        
        # Set entry functionality
        self.pixel_size_e.trace_add("write", self.update_pixel_size)

        #---------------------------------------------------------------------#
        # Logging frame (SE) -------------------------------------------------#
        self.frame3 = tk.LabelFrame(self, text="Log", width=400)
        self.frame3.grid(row=1, column=1, sticky=tk.W+tk.E+tk.N+tk.S,
            padx=(pad0/2, pad0), pady=(pad0/2, pad0))
        self.frame3.grid_propagate(False)
        self.frames.append(self.frame3)
        
        # Create logging text box and divert sys.stdout to it
        self.log_t = tk.Text(self.frame3, bg='black', fg="white")
        self.log_t.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S,
            padx=(pad1, pad1), pady=(pad1, pad1))
        sys.stdout = StdoutDirector(self.log_t)

        #-End of UI layout ---------------------------------------------------#

        # Formatting ---------------------------------------------------------#
        self.stretch_grid(self)
        for frame in self.frames :
            self.stretch_grid(frame)

    #-Start of class methods -------------------------------------------------#

    def load_image(self) :
        # Load image
        previous_filename = self.input_canvas.filename
        self.input_canvas.load_draw_image()

        # Update output image resolution fields to default to input image size
        # The update_in_progress flag is needed to avoid triggering 
        # update_out_res_x and update_out_res_y when I load the image
        if (self.input_canvas.filename != previous_filename) :
            self.out_res_x_e.set_value(self.input_canvas.image_no_zoom_PIL.width)
            self.out_res_y_e.set_value(self.input_canvas.image_no_zoom_PIL.height)
        
        # Start with locked aspect ratio after loading
        self.aspect_ratio_b_status = 1
        self.aspect_ratio_b.config(image=self.aspect_ratio_i_lock)

    def toggle_selection_tool(self) :
        self.selection_tool_b.on_toggle_change()
        if not self.selection_tool_b.toggled :
            self.input_canvas.delete_selection()

    def save_image(self) :
        # If an output exists
        if self.output_canvas.image_id != -1 :
            if not self.pixel_size_e.valid :
                print("Cannot save output because of invalid pixel size")
                return
            pixel_size = self.pixel_size_e.value
            file = asksaveasfile(mode='w', defaultextension=".png",
                initialfile=self.input_canvas.filename+"_out",
                filetypes=[("PNG image file", ".png")],)
            if not file :
                return
            output_image = self.output_canvas.image_no_zoom_PIL.copy()
            final_size = (int(output_image.width*pixel_size), 
                int(output_image.height*pixel_size))
            output_image = output_image.resize(final_size, 
                resample=Image.NEAREST) 
            output_image.save(file.name)

    # Update out_res_y to be consistent with the current out_res_x if
    # the locked aspect ratio is toggled
    def update_complementary_out_res_x(self) :
        self.update_in_progress = True
        if (self.input_canvas.image_aspect_ratio != 0.0 and
            self.aspect_ratio_b_status == 1) :
            new_y = int(self.out_res_x_e.value/
                self.input_canvas.image_aspect_ratio)
            self.out_res_y_e.set_value(new_y)
        self.update_final_resolution()
        self.update_in_progress = False

    # Update out_res_x to be consistent with the current out_res_y if
    # the locked aspect ratio is toggled
    def update_complementary_out_res_y(self) :
        self.update_in_progress = True
        if (self.input_canvas.image_aspect_ratio != 0.0 and 
            self.aspect_ratio_b_status == 1) :
            new_x = int(self.out_res_y_e.value*
                self.input_canvas.image_aspect_ratio)
            self.out_res_x_e.set_value(new_x)
        self.update_final_resolution()
        self.update_in_progress = False  

    def update_out_res_x(self, *args) :
        if self.update_in_progress :
            return
        old_x = self.out_res_x_e.value
        self.out_res_x_e.on_write(args)
        if not self.out_res_x_e.valid :
            return
        if self.out_res_x_e.value != old_x :
            self.last_modified_out_res = "x"
        self.update_complementary_out_res_x()

    def update_out_res_y(self, *args) :
        if self.update_in_progress :
            return
        old_y = self.out_res_y_e.value
        self.out_res_y_e.on_write(args)
        if not self.out_res_y_e.valid :
            return
        if self.out_res_y_e.value != old_y :
            self.last_modified_out_res = "y"
        self.update_complementary_out_res_y()

    def toggle_aspect_ratio(self):
        if self.aspect_ratio_b_status == 0:
            self.aspect_ratio_b_status = 1
            self.aspect_ratio_b.config(image=self.aspect_ratio_i_lock)
            
            # Update resolution after enabling aspect ratio lock
            if self.last_modified_out_res == "x" :
                self.update_complementary_out_res_x()
            elif self.last_modified_out_res == "y" :
                self.update_complementary_out_res_y()
        else:
            self.aspect_ratio_b_status = 0
            self.aspect_ratio_b.config(image=self.aspect_ratio_i_ulock)
        self.update_final_resolution()

    def update_pixel_size(self, *args) :
        self.pixel_size_e.on_write(args)
        self.update_final_resolution()

    def update_final_resolution(self) :
        if not self.pixel_size_e.valid :
            return
        pixel_size = self.pixel_size_e.value
        self.final_out_res_sv.set(str(int(pixel_size*self.out_res_x_e.value))+
            " x "+str(int(pixel_size*self.out_res_y_e.value)))

    def process_image(self) :
        if self.input_canvas.image_id == -1 :
            print("Cannot run processor because no input image loaded")
            return
        self.image_processor.n_colors = self.colors_e.value
        if not self.colors_e.valid :
            print("Cannot run processor because of invalid number of colors")
            return
        self.image_processor.out_res_x = self.out_res_x_e.value
        self.image_processor.out_res_y = self.out_res_y_e.value
        if (not self.out_res_x_e.valid or not self.out_res_y_e.valid) :
            print("Cannot run processor because of invalid resolution")
            return
        self.image_processor.bits_R = self.bits_R_e.value
        self.image_processor.bits_G = self.bits_G_e.value
        self.image_processor.bits_B = self.bits_B_e.value
        if (not self.bits_R_e.valid or not self.bits_G_e.valid or not 
            self.bits_B_e.valid) :
            print("Cannot run processor because of invalid RGB channel bits")
            return
        self.image_processor.fidelity = self.fidelity_e.get()
        self.image_processor.process_image()

    def stretch_grid(self, obj) :
        col_count, row_count = obj.grid_size()
        for col in range(col_count):
            obj.grid_columnconfigure(col, weight=1, minsize=0)
        for row in range(row_count):
            obj.grid_rowconfigure(row, weight=1, minsize=0)

    def on_resize(self, event) :
        pass
        
### MAIN ######################################################################

if __name__ == "__main__":

    app = Application()
    app.mainloop()
