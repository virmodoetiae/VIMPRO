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
###############################################################################
### IMPORTS ###################################################################
###############################################################################

import os
import sys
import time
import math
import random
import logging
import numpy as np
import pandas as pd
import tkinter as tk
from enum import Enum
from tkinter import ttk
from PIL import Image, ImageOps, ImageTk
from tkinter.filedialog import askopenfile, asksaveasfile

###############################################################################
### DICTIONARIES ##############################################################
###############################################################################

interpolation_modes = {"Bilinear" : Image.BILINEAR, "Bicubic" : Image.BICUBIC,
    "Nearest" : Image.NEAREST, "Lanczos" : Image.LANCZOS}

anchor_points = {"Center" : "c", "Top" : "n", "Top-left" : "ne", "Left" : "e", 
    "Bottom-left" : "se", "Bottom" : "s", "Bottom-right" : "sw",
    "Right" : "w", "Top-right" : "nw"}

###############################################################################
### FUNCTIONS #################################################################
###############################################################################

# Add to dict under dict_key from kwargs[kwargs_key], if it exists
def add_from_kwargs(dict, dict_key, kwargs_key, kwargs) :

    if kwargs_key in kwargs :
        dict[dict_key] = kwargs[kwargs_key]

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

###############################################################################
### Classes ###################################################################
###############################################################################

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
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

class Padding :

    def __init__(self, pad_x, pad_y, ratio=2) :
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.ratio = ratio

    def get(self, dirc, padmode="xy", invert=False) :
        pads = {}
        r = self.ratio
        if padmode == "xx" :
            x = self.pad_x
            y = self.pad_x
        elif padmode == "xy" :
            x = self.pad_x
            y = self.pad_y
        elif padmode == "yx" :
            x = self.pad_y
            y = self.pad_x
        elif padmode == "yy" :
            x = self.pad_y
            y = self.pad_y

        # Mnemonic:
        #(W, E)
        #(N, S)
        if not invert :
            if dirc == "c" :
                pads["padx"] = (x/r, x/r)
                pads["pady"] = (y/r, y/r)
            elif dirc == "n" :
                pads["padx"] = (x/r, x/r)
                pads["pady"] = (y, y/r)
            elif dirc == "ne" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y, y/r)
            elif dirc == "e" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y/r, y/r)
            elif dirc == "se" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y/r, y)
            elif dirc == "s" :
                pads["padx"] = (x/r, x/r)
                pads["pady"] = (y/r, y)
            elif dirc == "sw" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y/r, y)
            elif dirc == "w" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y/r, y/r)
            elif dirc == "nw" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y, y/r)
            elif dirc == "ns" :
                pads["padx"] = (x/r, x/r)
                pads["pady"] = (y, y)
            elif dirc == "ew" :
                pads["padx"] = (x, x)
                pads["pady"] = (y/r, y/r)
        else :
            if dirc == "c" :
                pads["padx"] = (x, x)
                pads["pady"] = (y, y)
            elif dirc == "n" :
                pads["padx"] = (x, x)
                pads["pady"] = (y/r, y)
            elif dirc == "ne" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y/r, y)
            elif dirc == "e" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y, y)
            elif dirc == "se" :
                pads["padx"] = (x, x/r)
                pads["pady"] = (y, y/r)
            elif dirc == "s" :
                pads["padx"] = (x, x)
                pads["pady"] = (y, y/r)
            elif dirc == "sw" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y, y/r)
            elif dirc == "w" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y, y)
            elif dirc == "nw" :
                pads["padx"] = (x/r, x)
                pads["pady"] = (y/r, y)
            elif dirc == "ns" :
                pads["padx"] = (x, x)
                pads["pady"] = (y/r, y/r)
            elif dirc == "ew" :
                pads["padx"] = (x/r, x/r)
                pads["pady"] = (y, y)
        return pads

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

# k-means algorithm that takes advantage of numpy. Operates on np.arrays
class KMeans :

    def __init__(self, **kwargs) :
        
        #self.data = kwargs["data"]

        self.data, self.data_freq = np.unique(kwargs["data"], axis=0, 
            return_counts=True) 
        
        self.n = self.data.shape[0]
        self.d = self.data.shape[1]
        self.k = kwargs["k"]
        
        self.means = np.empty((0, self.d))
        self.clusters = []
        self.weights = []
        
        self.max_iters = kwargs.get("maxiters", 100)
        self.min_rel_epsilon = (1.0/3.0)**(kwargs.get("fidelity", 10)-1)
        
        self.print_info = kwargs.get("printinfo", False)
        
        self.run()
        
    def run(self) :
        # Do nothing if data smaller than k
        if self.n <= self.k :
            self.means = self.data
            self.correct_means()
            return

        if self.print_info :
            print("Running k-means with target residual:", 
                self.min_rel_epsilon)

        # Initialize means randomly
        while self.means.shape[0] < self.k :
            self.means = np.vstack([self.means, self.sample_from_data()])

        # Run the k-means iterations
        i = 0
        not_converged = True
        rel_epsilon = 1.0
        start_epsilon = 0.0
        while (i < self.max_iters and not_converged) :
            epsilon = self.run_one_iteration()
            if i == 0 :
                start_epsilon = epsilon
            else :
                rel_epsilon = epsilon/start_epsilon
            if rel_epsilon <= self.min_rel_epsilon :
                not_converged = False
            i+=1

        self.correct_means()

        if self.print_info :
            print("Final k-means performance (iters/res):", i,
                '{:.3E}'.format(rel_epsilon))

    def run_one_iteration(self) :
        # This bit of code produces an array dists of shape
        # (data.shape[0], means.shape[1]). Each row contains the
        # distances of the corresponding data point to each point
        # in means. So dists[i][j] is the average distance of data[i]
        # form means[j]
        dists = np.zeros((self.n, 0))
        for i, mean in enumerate(self.means) :
            dists = np.insert(
                dists, i, np.linalg.norm((mean-self.data), axis=1), axis=1)

        # Assign points in data to the closest cluster corresponding to 
        # each mean
        argmin_dists = np.argmin(dists, axis=1)
        self.clusters = [[] for i in range(self.k)]
        self.weights = [[] for i in range(self.k)]
        for i, mean in enumerate(self.means) :
            indices = np.where(argmin_dists == i)[0]
            self.clusters[i] = self.data[indices]
            self.weights[i] = self.data_freq[indices]
        
        # Update means
        epsilon = 0
        for i, cluster in enumerate(self.clusters) :
            if cluster.shape[0] > 0 :
                new_mean = np.average(cluster, 
                    axis=0, weights=np.asarray(self.weights[i]))
            else :
                new_mean = self.sample_from_data()
            epsilon += np.linalg.norm(new_mean-self.means[i])
            self.means[i] = new_mean

        return epsilon

    def correct_means(self) :
        # Force size of k (maybe unnecessary?)
        self.means = np.unique(np.rint(self.means), axis=0)
        while self.means.shape[0] < self.k :
            self.means = np.vstack([self.means, self.means[-1]])

    def sample_from_data(self) :
        while True :
            new_mean = self.data[np.random.randint(0, self.n-1)]
            if new_mean not in self.means :
                return new_mean

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

class ImageProcessor :

    def __init__(self, input_canvas, output_canvas) :
        self.input_canvas = input_canvas
        self.output_canvas = output_canvas
        self.max_pixels = 128*128
        self.default_mode_name = "Default"
        self.tiled_mode_name = "Tiled"
        self.GBC_mode_name = "Game Boy Color"
        self.modes = [self.default_mode_name, self.tiled_mode_name, 
            self.GBC_mode_name]
    
    def best_palette_avg_norm(self, data, palettes) :
        if palettes.shape[0] > 1 :
            palettes_reshaped = palettes.reshape(
                palettes.shape[0]*palettes.shape[1], palettes.shape[2])
            palettes_sum_norm = np.zeros(palettes.shape[0])
            for i, palette_color in enumerate(palettes_reshaped) :
                palettes_sum_norm[int(np.floor(i/palettes.shape[1]))] += \
                    np.sum(np.linalg.norm(data-palette_color, axis=1), axis=0)
            return palettes[np.argmin(palettes_sum_norm)]
        return palettes[0]

    def best_palette_min_norm(data, palettes) :
        if palettes.shape[0] > 1 :
            palettes_reshaped = palettes.reshape(
                palettes.shape[0]*palettes.shape[1], palettes.shape[2])
            palettes_sum_norm = np.ones(palettes.shape[0])*1e12
            for i, palette_color in enumerate(palettes_reshaped) :
                I = int(np.floor(i/palettes.shape[1]))
                palettes_sum_norm[I] = min(np.sum(np.linalg.norm(
                    data-palette_color, axis=1), axis=0), palettes_sum_norm[I])
            return palettes[np.argmin(palettes_sum_norm)]
        return palettes[0]

    def replace_from_palette(self, data, palette) :
        # First, construct argmin_dists which is a 1-D array of size 
        #data.shape[0] wherein each element consists of the index of the 
        # corresponding palette color that best approximates the corresponding
        # element in data
        dists = np.zeros((data.shape[0], 0))
        for i, palette_color in enumerate(palette) :
            d = np.linalg.norm((palette_color-data), axis=1)
            dists = np.insert(dists, i, d, axis=1)
        argmin_dists = np.argmin(dists, axis=1)
        # Now, do the actual substitution in data. Would be great if I could
        # rid of the second for, but oh, for now it's fine
        for i, palette_color in enumerate(palette) :
            indices = np.where(argmin_dists == i)[0]*palette_color.shape[0]
            for j in range(palette_color.shape[0]) :
                data.put((indices+j), palette_color[j])
        return data

    def convert_color_bits(self, array, rgb_bits, unique=False) :
        if rgb_bits == [16, 16, 16] :
            return array
        scale_8_bit = np.array([float(2**(rgb_bits[0]-1))/255.0, 
            float(2**(rgb_bits[1]-1))/255.0, float(2**(rgb_bits[2]-1))/255.0])
        if unique :
            return np.unique(np.rint(np.divide(np.rint(np.multiply(
                array, scale_8_bit)), scale_8_bit)), axis=0)
        return np.rint(np.divide(np.rint(np.multiply(
                array, scale_8_bit)), scale_8_bit))

    def crop(self, im, target_aspect_ratio) :
        width, height = im.size
        aspect_ratio = width/height
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
        return im

    def process_default(self, **kwargs) :
        palette_size = kwargs["palettesize"]
        rgb_bits = kwargs["rgbbits"]
        fidelity = kwargs["fidelity"]
        out_x = kwargs["outx"]
        out_y = kwargs["outy"]
        aspect_ratio = out_x/out_y
        
        # Get or default
        max_pixels = kwargs.get("maxpixels", self.max_pixels)

        # Load image as copy and resize to operate the k-means on at most
        # self.max_pixels pixels (because it's time consuming), shape them into
        # a 1D array and operate k-means on them to find clusters of size 
        # n_colors
        kmeans_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        n_pixels = out_x*out_y
        scale = math.sqrt(max_pixels/n_pixels)
        kmeans_image = self.crop(kmeans_image, aspect_ratio)
        kmeans_image = kmeans_image.resize((int(out_x*min(scale, 1.0)), 
            int(out_y*min(1.0, scale))), resample=Image.NEAREST)
        data = np.array(kmeans_image)
        data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
        k_means = KMeans(data=data, k=palette_size, fidelity=fidelity, 
            printinfo=True)

        # Prepare output image (cropping and such)
        output_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        output_image = self.crop(output_image, aspect_ratio)
        output_image = output_image.resize((out_x, out_y))

        # Convert color palette into 8 bit
        k_means.means = self.convert_color_bits(k_means.means, 
            rgb_bits)

        # Replace colors in output with colors in palette
        data = np.array(output_image)
        orig_shape = data.shape
        data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
        self.replace_from_palette(data, k_means.means)
        data = data.reshape(orig_shape)
        
        # Reassamble data into image, set and draw image to output canvas
        output_image = Image.fromarray(data)
        self.output_canvas.set_zoom_draw_image(output_image)

    def process_tiled(self, **kwargs) :
        n_palettes = kwargs["npalettes"]
        palette_size = kwargs["palettesize"]
        rgb_bits = kwargs["rgbbits"]
        fidelity = kwargs["fidelity"]
        t_x = kwargs["tilesize"][0]
        t_y = kwargs["tilesize"][1]
        out_t_x = kwargs["outx"]
        out_t_y = kwargs["outy"]
        out_x = int(out_t_x*t_x)
        out_y = int(out_t_y*t_y)
        aspect_ratio = out_x/out_y
        # Get or default
        max_pixels = kwargs.get("maxpixels", self.max_pixels)

        input_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        input_image = self.crop(input_image, aspect_ratio)
        output_image = input_image.copy()
        output_image = output_image.resize((out_x, out_y))
        output_data = np.array(output_image)
        n_pixels = out_x*out_y
        scale = math.sqrt(max_pixels*n_palettes/n_pixels)
        input_image = input_image.resize((int(out_x*min(scale, 1.0)), 
            int(out_y*min(1.0, scale))), resample=Image.LANCZOS)
        data = np.array(input_image)
        data = data.reshape(data.shape[0]*data.shape[1], 
            data.shape[2])

        # Determine palettes
        palettes = []
        start_time = time.time()
        delta = np.floor(data.shape[0]/n_palettes)
        for i in range(n_palettes) :
            cut_data = None
            s = int(i*delta)
            if i != n_palettes-1 :
                e = int((i+1)*delta)
                cut_data = data[s:e]
            else :
                e = int((i)*delta)
                cut_data = data[e:]
            k_means = KMeans(data=cut_data, k=palette_size, fidelity=fidelity)
            k_means.means = self.convert_color_bits(k_means.means,
                rgb_bits)
            palettes.append(k_means.means)
        palettes = np.asarray(palettes)
        print("Dt k-means =", (time.time()-start_time))
        
        # Determine best palette for each tile. This is done or downsampled
        # tiles of 8x8 to improve performance
        best_palettes = []
        max_tile_pixels = 16*16
        start_time = time.time()
        out = np.empty((0, out_x, 3))
        for j in range(out_t_y) :
            hout = np.empty((t_y, 0, 3))
            for i in range(out_t_x) :
                I = i*t_x
                J = j*t_y
                box = (i*t_x, j*t_y, (i+1)*t_x, (j+1)*t_y)
                tile = output_image.crop(box)
                proc_tile = tile.copy()
                n_pixels = tile.width*tile.height
                if (n_pixels > max_tile_pixels) :
                    scale = np.sqrt(max_tile_pixels/n_pixels)
                    proc_tile = proc_tile.resize((int(tile.width*scale), 
                        int(tile.height*scale)), resample=Image.LANCZOS)
                data = np.array(proc_tile)
                best_palette = self.best_palette_avg_norm(
                    data.reshape(data.shape[0]*data.shape[1], data.shape[2]),
                    palettes)
                data = np.array(tile)
                orig_shape = data.shape
                self.replace_from_palette(
                    data.reshape(data.shape[0]*data.shape[1], data.shape[2]),
                    best_palette)
                data = data.reshape(orig_shape)
                hout = np.hstack((hout, data))
            out = np.vstack((out, hout))
        print("Dt substitution =", (time.time()-start_time))
        
        output_image = Image.fromarray(out.astype(np.uint8))
        self.output_canvas.set_zoom_draw_image(output_image)

    def process(self, **kwargs) :

        mode = kwargs.get("mode", self.default_mode_name)
        if mode == self.default_mode_name :
            self.process_default(**kwargs)
        elif mode == self.tiled_mode_name or mode == self.GBC_mode_name:
            self.process_tiled(**kwargs)

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

# Class to handle the representation of a selection rectangle
class SelectionRectangle :

    def __init__(self, canvas, *args, **kwargs) :
        self.canvas = canvas # Top level canvas on which selection lives
        self.coords_abs = [] # Absolute (i.e. with respect to canvas NW point)
        self.coords_rel = [] # Relative (i.e. with respect to image NW point)
        self.coords_rel_scaled = []
        self.id = -1
        min_x = 0
        min_y = 0
        if "event" in kwargs :
            event = kwargs.pop("event")
            min_x = event.x
            min_y = event.y
        max_x = min_x
        max_y = min_y
        self.x0 = min_x
        self.y0 = min_y
        self.id = canvas.create_line(
            min_x, max_y, 
            max_x, max_y,
            max_x, min_y,
            min_x, min_y,
            min_x, max_y,
            **kwargs)
        self.coords_abs = [min_x, min_y, max_x, max_y]
        min_x = self.canvas.canvasx(min_x)
        min_y = self.canvas.canvasy(min_y)
        max_x = self.canvas.canvasx(max_x)
        max_y = self.canvas.canvasy(max_y)
        self.coords_rel = [min_x, min_y, max_x, max_y]

    def delete(self) :
        self.canvas.delete(self.id)

    def resize(self, event) :
        min_x = min(self.x0, event.x)
        min_y = min(self.y0, event.y)
        max_x = max(self.x0, event.x)
        max_y = max(self.y0, event.y)
        min_x = max(min_x, 0)
        min_y = max(min_y, 0)
        max_x = min(max_x, self.canvas.winfo_width())
        max_y = min(max_y, self.canvas.winfo_height())
        self.coords_abs = [min_x, min_y, max_x, max_y]
        min_x = self.canvas.canvasx(min_x)
        min_y = self.canvas.canvasy(min_y)
        max_x = self.canvas.canvasx(max_x)
        max_y = self.canvas.canvasy(max_y)
        self.coords_rel = [min_x, min_y, max_x, max_y]
        self.coords_rel_scaled = [int(min_x/self.canvas.image_scale), 
            int(min_y/self.canvas.image_scale), 
            int(max_x/self.canvas.image_scale), 
            int(max_y/self.canvas.image_scale)]
        self.canvas.coords(self.id,
            min_x, max_y, 
            max_x, max_y,
            max_x, min_y,
            min_x, min_y,
            min_x, max_y)

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

class MouseScrollableImageCanvas(tk.Canvas):
    
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.configure(scrollregion=(0,0,1000,1000))
        self.image = None
        self.image_no_zoom = None
        self.image_no_zoom_PIL = None
        self.image_no_zoom_PIL_RGB = None
        self.image_id = None
        self.undo_buffer = None
        self.filepath = None
        self.filename = None
        
        self.image_scale = 1.0
        self.image_zoom_factor = 1.25
        self.aspect_ratio = 0.0

        # Refs to last x,y mouse coordinate after dragging, needed to maintain
        # the output image in place after processing (i.e. avoiding re-setting
        # the output view everytime the input is reprocessed and the output
        # re-drawn)
        self.last_event_x = 0
        self.last_event_y = 0

        # Selection tool
        self.selection_tool_b = None
        self.selection_rectangle = None
        
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
        if self.selection_tool_b : # If button is linked
            if self.selection_tool_b.toggled : # If button is on
                if self.selection_rectangle : # If a selection exists
                    self.selection_rectangle.delete()
                self.selection_rectangle = SelectionRectangle(self, 
                    event=event)
                return
        self.scan_mark(event.x, event.y)

    def click_and_drag(self, event):
        if self.selection_tool_b :
            if self.selection_tool_b.toggled :
                self.selection_rectangle.resize(event)
                return
        self.last_event_x = event.x
        self.last_event_y = event.y
        self.scan_dragto(event.x, event.y, gain=1)

    def release_click(self, event) :
        if self.selection_tool_b :
            if self.selection_tool_b.toggled :
                self.selection_rectangle.resize(event)
                return

    def delete_selection_rectangle(self) :
        if self.selection_rectangle :
            self.selection_rectangle.delete()
            self.selection_rectangle = None
                
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
        if not self.image_no_zoom_PIL :
            return
        iw = int(self.image_no_zoom_PIL.width*self.image_scale)
        ih = int(self.image_no_zoom_PIL.height*self.image_scale)
        size = (iw, ih)
        i1 = self.image_no_zoom_PIL.resize(size, resample=Image.NEAREST)
        self.image = ImageTk.PhotoImage(i1)
        self.configure(scrollregion=(0, 0, self.image.width(), 
            self.image.height()))
        self.delete_selection_rectangle()
        self.draw_image()

    # Set image from provided PIL image but do not draw
    def set_image(self, im) :
        self.image_no_zoom_PIL = im
        self.image_no_zoom_PIL_RGB = self.image_no_zoom_PIL.convert("RGB")
        self.image_no_zoom = ImageTk.PhotoImage(self.image_no_zoom_PIL_RGB)
        self.image = self.image_no_zoom
        self.aspect_ratio = self.image.width()/self.image.height()
        self.configure(scrollregion=(0, 0, self.image.width(), 
            self.image.height()))

    # Load image from file but do not draw
    def load_image(self) :
        self.image_scale = 1.0 # Re-set zoom level
        file = askopenfile(mode="rb", title="Select an image to load")
        if file :
            path = ""
            splitpath = file.name.split("/")
            for i, p in enumerate(splitpath) :
                if i < len(splitpath)-1 :
                    path += p+"/"
            self.filepath = path
            self.filename = (file.name.split("/")[-1]).split(".")[0]
            self.set_image(Image.open(file.name))

    # (Re-)Draw image on canvas
    def draw_image(self):
        if not self.image_id :
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

    # Resize image
    def resize_image(self, x, y, mode) :
        self.undo_buffer = self.image_no_zoom_PIL.copy()
        self.set_zoom_draw_image(
            self.image_no_zoom_PIL.resize((x,y),
            resample=interpolation_modes[mode]))

    # Crop image
    def crop_image(self, **kwargs) :
        x0 = self.image_no_zoom_PIL.width
        y0 = self.image_no_zoom_PIL.height
        box = None
        # Crop from anchor and final resolution
        if "anchor" in kwargs and "size" in kwargs :
            anchor = anchor_points[kwargs["anchor"]]
            x = min(kwargs["size"][0], x0)
            y = min(kwargs["size"][1], y0)
            dx = int(x0-x)
            dy = int(y0-y)
            dx_2 = int(dx/2.0)
            dy_2 = int(dy/2.0) 
            if anchor == "c" :
                box = (dx_2, dy_2, x+dx_2, y+dy_2)
            elif anchor == "n" :
                box = (dx_2, 0, x+dx_2, y)
            elif anchor == "ne" :
                box = (dx, 0, x+dx, y)
            elif anchor == "e" :
                box = (dx, dy_2, x+dx, y+dy_2)
            elif anchor == "se" :
                box = (dx, dy, x+dx, y+dy)
            elif anchor == "s" :
                box = (dx_2, dy, x+dx_2, y+dy)
            elif anchor == "sw" :
                box = (0, dy, x, y+dy)
            elif anchor == "w" :
                box = (0, dy_2, x, y+dy_2)
            elif anchor == "nw" :
                box = (0, 0, x, y)
        # Crop from bounding box
        elif "box" in kwargs :
            box = kwargs["box"]
            box = (max(box[0], 0), max(box[1], 0), min(box[2], x0), 
                min(box[3], y0))
        self.undo_buffer = self.image_no_zoom_PIL.copy()
        self.set_zoom_draw_image(self.image_no_zoom_PIL.crop(box))

    # Undo (specifically meant for resize_image or crop_image)
    def undo(self) :
        if self.undo_buffer :
            self.set_zoom_draw_image(self.undo_buffer)
            self.undo_buffer = None

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

# Toggleable button with option image to be provided for its different states
class ToggleButton(tk.Button) :

    def __init__(self, *args, **kwargs) :
        
        # Pop before passing to tk.Button to avoid dict errors
        self.on_i = kwargs.pop("onimage", None)
        self.off_i = kwargs.pop("offimage", None)
        
        if "command" not in kwargs :
            kwargs["command"] = self.on_toggle_change
        tk.Button.__init__(self, *args, **kwargs, relief="raised")
        
        # Button starts off
        self.toggled = False
        if self.off_i and "image" not in kwargs:
            self.config(image=self.off_i)

    def on_toggle_change(self, *args) :
        self.toggled = not self.toggled
        self.update_appearance()
        
    def toggle_on(self) :
        self.toggled = True
        self.update_appearance()

    def toggle_off(self) :
        self.toggled = False
        self.update_appearance()

    def update_appearance(self) :
        if self.toggled :
            if self.on_i :
                self.config(image=self.on_i)
            self.config(relief="sunken")
        else :
            if self.off_i :
                self.config(image=self.off_i)
            self.config(relief="raised")

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

# Class to handle an entry of an integer in a way that is closer to what I 
# need compared to tk.IntVar
class IntEntry(tk.Entry) :

    def __init__(self, *args, **kwargs) :
        tk.Entry.__init__(self, *args, **kwargs)
        self.sv = tk.StringVar()
        self.config(textvariable=self.sv)
        self.value = None
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
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

# Compund object consisting of a label, two entries represnting and x and y
# resolution fields as well as a middle button that acts as an aspect ratio
# lock
class ResolutionLabelEntry :

    def __init__(self, *args, **kwargs) :
        self.top_level = args[0]
        self.row = kwargs.get("row", 0)
        self.column = kwargs.get("column", 0)
        self.min_value = kwargs.get("minvalue")
        self.max_value = kwargs.get("maxvalue")
        self.last_modified = None
        self.update_in_progress = False
        self.aspect_ratio = kwargs.get("aspectratio", 0.0)
        self.pads = kwargs.get("pads", kwargs)
        self.buffer = None

        self.label_dict = {}
        add_from_kwargs(self.label_dict, "text", "labeltext", kwargs)
        add_from_kwargs(self.label_dict, "width", "labelwidth", kwargs)
        self.l = tk.Label(self.top_level, anchor=tk.W, **self.label_dict)
        self.l.grid(row=self.row, column=self.column, sticky=tk.W, 
            **self.pads[0])
        
        self.entry_dict = {}
        add_from_kwargs(self.entry_dict, "width", "entrywidth", kwargs)

        self.x_e = IntEntry(self.top_level, **self.entry_dict)
        self.x_e.grid(row=self.row, column=self.column+1, sticky=tk.W+tk.E, 
            **self.pads[1])

        self.aspect_ratio_b = ToggleButton(self.top_level, bd=0,
            onimage=ImageTk.PhotoImage(file="lock.png"), 
            offimage=ImageTk.PhotoImage(file="ulock.png"), **self.entry_dict)
        self.aspect_ratio_b.config(command=self.on_toggle_aspect_ratio)
        self.aspect_ratio_b.grid(row=self.row, column=self.column+2, 
            sticky=tk.W+tk.E, **self.pads[2])

        self.y_e = IntEntry(self.top_level, **self.entry_dict)
        self.y_e.grid(row=self.row, column=self.column+3, sticky=tk.W+tk.E, 
            **self.pads[3])

        if self.min_value :
            self.x_e.set_min_value(self.min_value)
            self.y_e.set_min_value(self.min_value)
        if self.max_value :
            self.x_e.set_min_value(self.max_value)
            self.y_e.set_min_value(self.max_value)

        self.x_e.trace_add("write", self.on_write_x)
        self.y_e.trace_add("write", self.on_write_y)

    def disable(self) :
        self.x_e.config(state=tk.DISABLED)
        self.y_e.config(state=tk.DISABLED)
        self.aspect_ratio_b.config(state=tk.DISABLED)

    def enable(self) :
        self.x_e.config(state=tk.NORMAL)
        self.y_e.config(state=tk.NORMAL)
        self.aspect_ratio_b.config(state=tk.NORMAL)

    def on_toggle_aspect_ratio(self) :
        self.aspect_ratio_b.on_toggle_change()
        if self.aspect_ratio_b.toggled :

            # Update last modified variable
            if self.last_modified == "x" :
                self.update_complementary_x()
            elif self.last_modified == "y" :
                self.update_complementary_y()

    def on_write_x(self, *args) :
        if self.update_in_progress :
            return
        old_x = self.x_e.value
        self.x_e.on_write(args)
        if not self.x_e.valid :
            return
        if self.x_e.value != old_x :
            self.last_modified = "x"
        self.update_complementary_x()

    def on_write_y(self, *args) :
        if self.update_in_progress :
            return
        old_y = self.y_e.value
        self.y_e.on_write(args)
        if not self.y_e.valid :
            return
        if self.y_e.value != old_y :
            self.last_modified = "y"
        self.update_complementary_y()

    def set(self, x, y) :
        self.aspect_ratio = float(x)/float(y)
        self.x_e.set_value(x)
        self.y_e.set_value(y)

    def set_buffer(self) :
        self.buffer = (self.x_e.value, self.y_e.value)

    def reset_from_buffer(self) : 
        if self.buffer :
            self.set(self.buffer[0], self.buffer[1])
        self.buffer = None

    # Update out_res_y to be consistent with the current out_res_x if
    # the locked aspect ratio is toggled
    def update_complementary_x(self) :
        self.update_in_progress = True
        if (self.aspect_ratio != 0.0 and
            self.aspect_ratio_b.toggled) :
            new_y = int(self.x_e.value/self.aspect_ratio)
            self.y_e.set_value(new_y)
        self.update_in_progress = False

    # Update out_res_x to be consistent with the current out_res_y if
    # the locked aspect ratio is toggled
    def update_complementary_y(self) :
        self.update_in_progress = True
        if (self.aspect_ratio != 0.0 and 
            self.aspect_ratio_b.toggled) :
            new_x = int(self.y_e.value*self.aspect_ratio)
            self.x_e.set_value(new_x)
        self.update_in_progress = False  

    def valid(self) :
        return (self.x_e.valid and self.y_e.valid)

#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

class Application(tk.Tk) :

    def __init__(self, *args, **kwargs) :

        tk.Tk.__init__(self, *args, **kwargs)
        self.title("VIMPRO - Virmodoetiae Image Processor")
        self.iconphoto(False, ImageTk.PhotoImage(file='icon.png'))
        self.bind("<Configure>", self.on_main_window_resize)
        self.frames = []
        
        # UI Layout ----------------------------------------------------------#
        self.label_width = 20
        self.button_width = 10
        self.entry_width = 8
        self.default_pad = 20
        self.pad0 = Padding(self.default_pad, self.default_pad)
        self.pad1 = Padding(self.default_pad/4, self.default_pad/8)

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
        self.input_canvas = MouseScrollableImageCanvas(self.input_frame, 
            width=600, height=300)
        self.input_canvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        #---------------------------------------------------------------------#
        # Output frame and canvas (SW) ---------------------------------------#
        self.output_frame = tk.LabelFrame(self.left_frame, text="Output")
        self.output_frame.grid(row=1, column=0, sticky=tk.W+tk.E+tk.N+tk.S, 
            **self.pad0.get("sw"))
        self.frames.append(self.output_frame)
        self.output_canvas = MouseScrollableImageCanvas(self.output_frame, 
            width=600, height=300)
        self.output_canvas.grid(row=0, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        # Image processor object
        self.image_processor = ImageProcessor(self.input_canvas, 
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
            "Mode" : 5, "Number of palettes" : 6, "Palette size" : 7, 
            "Bits per channel (R,G,B)" : 8, "Fidelity" : 9, "Tile size" : 10,
            "Output resolution" : 11, "Process image" : 12, 
            "Save options" : 13, "Pixel size" : 14, "Final resolution" : 15,
            "Save image" : 16}

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
        self.open_resize_b = ToggleButton(self.ctrl_frame, text=row_name,
            width=self.button_width, command=self.on_open_resize)
        self.open_resize_b.grid(row=row_n, column=0, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("w", "xx"))

        # Resize frame
        self.resize_frame = tk.LabelFrame(self.ctrl_frame)
        self.frames.append(self.resize_frame)
        
        # Target resolution for resize
        self.resize_res_le = ResolutionLabelEntry(self.resize_frame,
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
        self.open_crop_b = ToggleButton(self.ctrl_frame, text=row_name,
            width=self.button_width, command=self.on_open_crop)
        self.open_crop_b.grid(row=row_n, column=0, sticky=tk.W+tk.E+tk.N,
            **self.pad1.get("sw", "xx"))

        # Crop frame
        self.crop_frame = tk.LabelFrame(self.ctrl_frame)
        self.frames.append(self.crop_frame)

        # Target resolution for crop
        self.crop_res_le = ResolutionLabelEntry(self.crop_frame, 
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

        self.selection_tool_b = ToggleButton(self.crop_sub_frame, 
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
        row_name = "Number of palettes"
        row_n = self.ctrl_rows[row_name]
        self.palettes_n_l = tk.Label(self.ctrl_frame, text=row_name, 
            anchor=tk.W)
        self.palettes_n_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.palettes_n_e.set_min_value(1)
        self.palettes_n_e.set_value(8)

        # Processor mode -------------#
        # This should come first, but the option menu needs to be tied to
        # the creation-destruction of additional entries/labels when a certain
        # proc_mode_om is selected. The show/hide functionality of these
        # fields needs to be passed as command, but this means that I cannot
        # create proc_mode_om until after I have created all the
        # entries/labels that are referenced by the command. Thus, proc_mode
        # is created at the end
        row_name = "Mode"
        row_n = self.ctrl_rows[row_name]
        proc_mode_l = tk.Label(self.ctrl_frame, text=row_name)
        proc_mode_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))

        self.proc_mode_sv = tk.StringVar()
        self.proc_mode_sv.set("Default")
        self.proc_mode_om = ttk.OptionMenu(self.ctrl_frame, self.proc_mode_sv,
            self.image_processor.modes[0], *self.image_processor.modes,
            command=self.on_proc_mode)
        self.proc_mode_om.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))

        # Palette size ---------------#
        row_name = "Palette size"
        row_n = self.ctrl_rows[row_name]
        palette_size_l = tk.Label(self.ctrl_frame, text=row_name, anchor=tk.W)
        palette_size_l.grid(row=row_n, column=0, sticky=tk.W,
            **self.pad1.get("w"))
        self.palette_size_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.palette_size_e.set_value(4)
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

        self.bits_R_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_R_e.set_value(16)
        self.bits_R_e.set_min_value(2)
        self.bits_R_e.set_max_value(16)
        self.bits_R_e.grid(row=row_n, column=1, sticky=tk.W+tk.E,
            **self.pad1.get("c"))
        
        self.bits_G_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_G_e.set_value(16)
        self.bits_G_e.set_min_value(2)
        self.bits_G_e.set_max_value(16)
        self.bits_G_e.grid(row=row_n, column=2, sticky=tk.W+tk.E,
            **self.pad1.get("c"))
        
        self.bits_B_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.bits_B_e.set_value(16)
        self.bits_B_e.set_min_value(2)
        self.bits_B_e.set_max_value(16)
        self.bits_B_e.grid(row=row_n, column=3, sticky=tk.W+tk.E,
            **self.pad1.get("e"))

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
        # Number of palettes -------------#
        row_name = "Tile size"
        row_n = self.ctrl_rows[row_name]
        self.tile_size_l = tk.Label(self.ctrl_frame, text=row_name, 
            anchor=tk.W)
        self.tile_size_e_x = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.tile_size_e_x.set_min_value(1)
        self.tile_size_e_x.set_value(8)
        self.tile_size_e_y = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.tile_size_e_y.set_min_value(1)
        self.tile_size_e_y.set_value(8)

        # Output resolution ----------#
        row_name = "Output resolution"
        row_n = self.ctrl_rows[row_name]
        self.out_res_le = ResolutionLabelEntry(self.ctrl_frame, row=row_n,
            col=0, minvalue=1, labeltext=row_name, labelwidth=self.label_width,
            entrywidth=self.entry_width, pads=[self.pad1.get("w"), 
            self.pad1.get("c"), self.pad1.get("c"), self.pad1.get("e")])

        # Process image --------------#
        row_name = "Process image"
        row_n = self.ctrl_rows[row_name]
        self.process_image_b = tk.Button(self.ctrl_frame, 
            width=self.button_width, text=row_name, command=self.process_image)
        self.process_image_b.grid(row=row_n, column=0, sticky=tk.W+tk.E, 
            **self.pad1.get("sw", "xx"))
        
        # Save options -------------------------------------------------------#
        row_name = "Save options"
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
        self.pixel_size_e = IntEntry(self.ctrl_frame, width=self.entry_width)
        self.pixel_size_e.set_value(1)
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

        # Add functionality at the end to avoid potential issues regarding
        # referencing missing variables
        self.pixel_size_e.trace_add("write", self.on_write_pixel_size)

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
        self.on_proc_mode() # Init out_res_le buffers

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
        new_x = self.input_canvas.image_no_zoom_PIL.width
        new_y = self.input_canvas.image_no_zoom_PIL.height

        # Update output image resolution fields to default to input image size
        if (self.input_canvas.filename != previous_filename or 
            (old_x != new_x or old_y != new_y)) :
            self.update_all_res_entries(new_x, new_y)
        
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

    def on_resize(self) :
        if not self.resize_res_le.valid() :
            print("Cannot resize image because of invalid target resolution")
            return
        x = self.resize_res_le.x_e.value
        y = self.resize_res_le.y_e.value
        self.input_canvas.resize_image(x, y, self.interp_mode_sv.get())
        self.update_all_res_entries(x, y)
        self.update_undo_b()

    def on_undo_resize(self) :
        if self.input_canvas.undo_buffer :
            x = self.input_canvas.undo_buffer.width
            y = self.input_canvas.undo_buffer.height
            self.update_all_res_entries(x, y)
        self.input_canvas.undo()
        self.update_undo_b()

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
                self.input_canvas.crop_image(anchor=self.crop_anchor_sv.get(),
                    size=(x,y))
                flag = True
        if flag :
            self.update_undo_b()
            x = self.input_canvas.image_no_zoom_PIL.width
            y = self.input_canvas.image_no_zoom_PIL.height
            self.update_all_res_entries(x, y)

    def on_undo_crop(self) :
        if self.input_canvas.undo_buffer :
            x = self.input_canvas.undo_buffer.width
            y = self.input_canvas.undo_buffer.height
            self.update_all_res_entries(x, y)
        self.input_canvas.undo()
        self.update_undo_b()

    def on_proc_mode(self, *args) :
        row_name = "Number of palettes"
        row_n = self.ctrl_rows[row_name]

        mode = self.proc_mode_sv.get()
        if mode == self.image_processor.default_mode_name :
            self.palettes_n_l.grid_forget()
            self.palettes_n_e.grid_forget()
            self.tile_size_l.grid_forget()
            self.tile_size_e_x.grid_forget()
            self.tile_size_e_y.grid_forget()
            self.out_res_le.l.config(text="Ouput resolution")
            self.out_res_le.reset_from_buffer()
        elif mode == self.image_processor.tiled_mode_name :
            row_name = "Number of palettes"
            row_n = self.ctrl_rows[row_name]
            self.palettes_n_l.grid(row=row_n, column=0,
                sticky=tk.W+tk.E, **self.pad1.get("w"))
            self.palettes_n_e.grid(row=row_n, column=1, columnspan=3,
            sticky=tk.W+tk.E, **self.pad1.get("e"))
            row_name = "Tile size"
            row_n = self.ctrl_rows[row_name]
            self.tile_size_l.grid(row=row_n, column=0,
                sticky=tk.W+tk.E, **self.pad1.get("w"))
            self.tile_size_e_x.grid(row=row_n, column=1,
                sticky=tk.W+tk.E, **self.pad1.get("c"))
            self.tile_size_e_y.grid(row=row_n, column=3,
                sticky=tk.W+tk.E, **self.pad1.get("e"))
            self.out_res_le.l.config(text= "Ouput resolution (tiles)")
            self.out_res_le.set_buffer()
            if (self.out_res_le.valid() and self.tile_size_e_x.valid and 
                self.tile_size_e_y.valid) :
                x = int(np.floor(
                    self.out_res_le.x_e.value/self.tile_size_e_x.value))
                y = int(np.floor(
                    self.out_res_le.y_e.value/self.tile_size_e_y.value))
                self.out_res_le.set(x, y)
    
    def on_write_pixel_size(self, *args) :
        self.pixel_size_e.on_write(args)
        self.update_save_resolution()

    def on_save_image(self) :
        if self.output_canvas.image_id :
            if not self.pixel_size_e.valid :
                print("Cannot save output because of invalid pixel size")
                return
            pixel_size = self.pixel_size_e.value
            file_exists = True
            filename = ""
            extension=".png"
            i = 0
            while file_exists :
                filename = self.input_canvas.filename+"_VIMPRO_"+str(
                    i)+extension
                file_exists = os.path.exists(
                    self.input_canvas.filepath+filename)
                i+=1
            file = asksaveasfile(mode='w', defaultextension=".png",
                initialfile=filename, filetypes=[("PNG image file", ".png")],)
            if not file :
                return
            output_image = self.output_canvas.image_no_zoom_PIL.copy()
            final_size = (int(output_image.width*pixel_size), 
                int(output_image.height*pixel_size))
            output_image = output_image.resize(final_size, 
                resample=Image.NEAREST) 
            output_image.save(file.name)

    def on_main_window_resize(self, *args) :
        pass

    # From here on, the ordering is alphabetical

    def process_image(self) :
        mode =self.proc_mode_sv.get()

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
        if mode != self.image_processor.default_mode_name :
            if not self.palettes_n_e.valid :
                print("Cannot run processor because of invalid number of \
                    palettes")
            if not (self.tile_size_e_x.valid or not self.tile_size_e_y.valid) :
                print("Cannot run processor because of invalid tile size")
        # Get input data. Note that everything here is an IntEntry object, 
        # which implements the value attribute. Fidelity isn't, so I use get
        palettes_n=self.palettes_n_e.value
        palette_size = self.palette_size_e.value
        rgb_bits = [self.bits_R_e.value, self.bits_G_e.value, 
            self.bits_B_e.value]
        fidelity = self.fidelity_e.get()
        tile_x = self.tile_size_e_x.value
        tile_y = self.tile_size_e_y.value
        out_x = self.out_res_le.x_e.value
        out_y = self.out_res_le.y_e.value

        # Run processor
        self.image_processor.process(mode=mode, npalettes=palettes_n,
            palettesize=palette_size, rgbbits=rgb_bits, fidelity=fidelity, 
            tilesize=(tile_x, tile_y), outx=out_x, outy=out_y)

        # Update output resolution of the possible save file
        self.update_save_resolution()

    def update_all_res_entries(self, x, y) :
        self.resize_res_le.set(x, y)
        self.crop_res_le.x_e.set_max_value(x)
        self.crop_res_le.y_e.set_max_value(y)
        self.crop_res_le.set(x, y)
        self.out_res_le.set(x, y)
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

###############################################################################
### MAIN ######################################################################
###############################################################################

if __name__ == "__main__":

    app = Application()
    app.mainloop()
