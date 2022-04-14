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
import time
import random
import string
import subprocess

from sys import platform
from copy import deepcopy
from PIL import Image, ImageOps, ImageTk
from tkinter.filedialog import askopenfile, asksaveasfile

import numpy as np

import VIMPRO_Data as vd

### CLASSES ###################################################################

class KMeans :

    def __init__(self, **kwargs) :

        # Remove transparency from the k-means clustering and add it back
        # as a single color (0,0,0,0) to the means if any transparency was
        # present to begin with
        tmp = deepcopy(kwargs["data"])
        alpha_threshold = 127
        transparent = np.where(tmp[:,3] < alpha_threshold)
        non_transparent = np.where(tmp[:,3] > alpha_threshold)
        tmp[non_transparent, 3] = 255
        tmp[transparent] = np.array([0,0,0,0])
        tmp = np.delete(tmp, transparent, axis=0)
        self.has_transparency = False
        if transparent[0].shape[0] != 0 :
            self.has_transparency = True

        self.data, self.data_freq = np.unique(tmp, axis=0, 
            return_counts=True)
        
        self.n = self.data.shape[0]
        self.d = self.data.shape[1]
        self.k = kwargs["k"]
        
        self.means = np.empty((0, self.d))
        self.clusters = []
        self.weights = []
        
        self.max_iters = kwargs.get("maxiters", 200)
        self.min_rel_epsilon = (1.0/3.0)**(kwargs.get("fidelity", 10)-1)
        
        self.print_info = kwargs.get("printinfo", False)
        
        self.run()

    def force_means_size(self) :
        # Force size of k on self.means
        self.means = np.unique(np.rint(self.means), axis=0)
        while self.means.shape[0] < self.k :
            self.means = np.vstack([self.means, self.means[-1]])
        
    def run(self) :
        # Do nothing if data smaller than k
        if self.n <= self.k :
            self.means = self.data
            self.force_means_size()
            return

        if self.print_info :
            print("Running k-means with target residual:", 
                '{:.3E}'.format(self.min_rel_epsilon))

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

        self.force_means_size()

        if self.has_transparency :
            self.means = np.vstack([self.means, np.array([0,0,0,0])])

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

    def sample_from_data(self) :
        while True :
            new_mean = self.data[np.random.randint(0, self.n)]
            
            # I.e. "if new_mean not in self.means"
            if not np.any(np.all((new_mean == self.means), axis=1)) :
                return new_mean

#-----------------------------------------------------------------------------#

class ImageProcessor :

    def __init__(self, input_canvas, output_canvas) :
        # Input, output canvases need to be objects that are or inherit from
        # tkinter canvases
        self.input_canvas = input_canvas
        self.output_canvas = output_canvas
        self.max_pixels = 128*128
        self.default_proc_mode_name = "Default"
        self.tiled_proc_mode_name = "Tiled"
        self.proc_modes = [self.default_proc_mode_name, 
            self.tiled_proc_mode_name]
        self.default_comp_mode_name = "Default"
        self.GBC_comp_mode_name = "Game Boy Color"
        self.comp_modes = [self.default_comp_mode_name, 
            self.GBC_comp_mode_name]

        self.proc_mode_sv = None
        self.comp_mode_sv = None

        self.output_is_GBC_compatible = False
        self.GBC_palette_map = None
        self.tile_size = None
        self.asm_source = None
    
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

    def convert_color_bits(self, array, rgb_bits, unique=False) :
        if rgb_bits == [16, 16, 16] :
            return array
        bit_scale = np.array([
            float((2**(rgb_bits[0])-1))/255.0, 
            float((2**(rgb_bits[1])-1))/255.0, 
            float((2**(rgb_bits[2])-1))/255.0,
            1.0])
        if unique :
            return np.unique(np.rint(np.divide(np.rint(np.multiply(
                array, bit_scale)), bit_scale)), axis=0)
        return np.rint(np.divide(np.rint(np.multiply(
                array, bit_scale)), bit_scale))

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

    def data_to_palette_index_map(self, data, palette) :
        # Returns a 1-D array of size data.shape[0] wherein each element 
        # consists of the index of the corresponding palette color that best
        # approximates the corresponding element in data
        dists = np.zeros((data.shape[0], 0))
        for i, palette_color in enumerate(palette) :
            d = np.linalg.norm((palette_color-data), axis=1)
            dists = np.insert(dists, i, d, axis=1)
        return np.argmin(dists, axis=1)

    def replace_from_palette(self, data, palette) :
        palette_index_map = self.data_to_palette_index_map(data, palette)
        for i, palette_color in enumerate(palette) :
            indices = np.where(
                palette_index_map == i)[0]*palette_color.shape[0]
            for j in range(palette_color.shape[0]) :
                data.put((indices+j), palette_color[j])
        return data

    def process_default(self, **kwargs) :
        palette_size = kwargs["palettesize"]
        rgb_bits = kwargs["rgbbits"]
        fidelity = kwargs["fidelity"]
        out_x = kwargs["outsize"][0]
        out_y = kwargs["outsize"][1]
        aspect_ratio = out_x/out_y
        
        # Get or default
        max_pixels = kwargs.get("maxpixels", self.max_pixels)

        # Load image as copy and resize to operate the k-means on at most
        # self.max_pixels pixels (because it's time consuming), shape them into
        # a 1D array and operate k-means on them to find clusters of size 
        # n_colors
        kmeans_image = self.input_canvas.image_no_zoom_PIL_RGB.copy()
        n_pixels = out_x*out_y
        scale = np.sqrt(max_pixels/n_pixels)
        kmeans_image = self.crop(kmeans_image, aspect_ratio)
        kmeans_image = kmeans_image.resize((int(out_x*min(scale, 1.0)), 
            int(out_y*min(1.0, scale))), resample=Image.NEAREST)
        data = np.array(kmeans_image)
        data = data.reshape(data.shape[0]*data.shape[1], data.shape[2])
        k_means = KMeans(data=data, k=palette_size, fidelity=fidelity, 
            printinfo=False)

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
        
        # Convert back to image and draw to canvas
        output_image = Image.fromarray(data)
        self.output_canvas.set_zoom_draw_image(output_image)

        # Set self.GBC_palette_map if in GBC_comp_mode
        if self.comp_mode == self.GBC_comp_mode_name :
            self.GBC_palette_map = [
                [k_means.means for i in range(20)] for i in range(18)]
            self.palettes = np.array([k_means.means])
            self.tile_size = (8, 8) # Useless, I keep it for consistency
        else :
            self.GBC_palette_map = None
            self.palettes = None
            self.tile_size = None

    def process_tiled(self, **kwargs) :
        #n_palettes = kwargs["npalettes"]
        palettes_grid_x = kwargs["palettesgridsize"][0]
        palettes_grid_y = kwargs["palettesgridsize"][1]
        n_palettes = palettes_grid_x*palettes_grid_y
        palette_size = kwargs["palettesize"]
        rgb_bits = kwargs["rgbbits"]
        fidelity = kwargs["fidelity"]
        t_x = kwargs["tilesize"][0]
        t_y = kwargs["tilesize"][1]
        out_t_x = kwargs["outsize"][0]
        out_t_y = kwargs["outsize"][1]
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
        scale = np.sqrt(max_pixels*n_palettes/n_pixels)
        input_image = input_image.resize((int(out_x*min(scale, 1.0)), 
            int(out_y*min(1.0, scale))), resample=Image.LANCZOS)
        data = np.array(input_image)

        # Determine palettes
        palettes = []
        dy = np.floor(data.shape[0]/palettes_grid_y)
        dx = np.floor(data.shape[1]/palettes_grid_x)
        #start_time = time.perf_counter()
        for i in range(palettes_grid_y) :
            start_y = int(dy*i)
            end_y = int(dy*(i+1))
            if i == palettes_grid_y-1 :
                end_y = data.shape[0]
            data_cut_y = np.split(data, [start_y, end_y], axis=0)[1]
            for j in range(palettes_grid_x) :
                start_x = int(dx*j)
                end_x = int(dx*(j+1))
                if j == palettes_grid_x-1 :
                    end_x = data.shape[1]
                data_cut_xy = np.split(data_cut_y, [start_x, end_x], axis=1)[1]
                data_cut_xy = data_cut_xy.reshape(
                    data_cut_xy.shape[0]*data_cut_xy.shape[1], 
                    data_cut_xy.shape[2])
                k_means = KMeans(data=data_cut_xy, k=palette_size, 
                    fidelity=fidelity)
                k_means.means = self.convert_color_bits(k_means.means,
                    rgb_bits)
                palettes.append(k_means.means)
        palettes = np.asarray(palettes)
        #print("Dt k-means =", (time.perf_counter()-start_time))

        if self.comp_mode == self.GBC_comp_mode_name :
            self.GBC_palette_map = [
                [None for i in range(out_t_x)] for i in range(out_t_y)]
            self.palettes = palettes.copy()
            self.tile_size = (t_x, t_y)
        else :
            self.GBC_palette_map = None
            self.palettes = None
            self.tile_size = None

        # Determine best palette for each tile. This is done or downsampled
        # tiles of 16x16. Then, perform the color quantization and assemble
        # the output image from the processed tiles
        max_tile_pixels = 16*16
        #start_time = time.perf_counter()
        out = np.empty((0, out_x, 4))
        for j in range(out_t_y) :
            hout = np.empty((t_y, 0, 4))
            for i in range(out_t_x) :
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
                if self.comp_mode == self.GBC_comp_mode_name :
                    self.GBC_palette_map[j][i] = best_palette
                data = np.array(tile)
                orig_shape = data.shape
                self.replace_from_palette(
                    data.reshape(data.shape[0]*data.shape[1], data.shape[2]),
                    best_palette)
                data = data.reshape(orig_shape)
                hout = np.hstack((hout, data))
            out = np.vstack((out, hout))
        #print("Dt substitution =", (time.perf_counter()-start_time))

        # Convert back to image and draw to canvas
        output_image = Image.fromarray(out.astype(np.uint8))
        self.output_canvas.set_zoom_draw_image(output_image)

    def process(self, **kwargs) :
        self.proc_mode = self.proc_mode_sv.get()
        self.comp_mode = self.comp_mode_sv.get()

        if (self.comp_mode == self.GBC_comp_mode_name and 
            self.proc_mode == self.tiled_proc_mode_name) :
            if kwargs["palettesgridsize"][0]*kwargs["palettesgridsize"][1] > 8:
                print("Cannot run processor in Game Boy Color compatibility \
                        mode if the total palettes grid size (x*y) exceeds 8")
                return

        if self.proc_mode == self.default_proc_mode_name :
            self.process_default(**kwargs)
        elif self.proc_mode == self.tiled_proc_mode_name :
            self.process_tiled(**kwargs)

        # Missing check on whether the actual processing succeeded, the
        # self.output_is_GBC_compatible should only be true in that case
        if self.comp_mode == self.GBC_comp_mode_name :
            self.output_is_GBC_compatible = True
        else :
            self.output_is_GBC_compatible = False

        # Copy filename and path from input canvas to enable saving the image
        # from the output canvas
        self.output_canvas.filename = self.input_canvas.filename
        self.output_canvas.filepath = self.input_canvas.filepath

    '''
    This function converts the output_image and converts it to a Game Boy 
    Color format. By that, I mean that the script produces a complete Game Boy
    Color assembly source code file (i.e. .asm) that can that be compiled with
    the free RGBDS package https://github.com/rednex/rgbds. In particular, once
    the RGBDS package is installed, the .asm source file (assuming its is 
    called main.asm) can be compiled via issuing:
        rgbasm.exe -o main.o main.asm
        rgblink.exe -o main.gb main.o
        rgbfix -C -v -p 0 main.gb <= the C option denots a GBC ROM instead of a
                                     GB ROM, it will not compile properly 
                                     without it!
    To skip the manual compilation step, if you are on a 64-bit Windows system,
    you can use the 'Compile .gb file button'
    '''
    def create_asm(self) :
        if not(self.output_is_GBC_compatible) :
            return

        t_x = self.tile_size[0]
        t_y = self.tile_size[1]

        def GBC_hex_format(h) :
            if len(h) == 1 :
                return "$0"+h
            else :
                return "$"+h

        # Check palettes map dimensions, and if not equal to adequate GBC ones,
        # "stretch" it
        self.GBC_palette_map = np.array(self.GBC_palette_map)
        x_shape = self.GBC_palette_map.shape[1]
        y_shape = self.GBC_palette_map.shape[0]
        if x_shape != 20 : 
            hout = np.empty((y_shape, 0, 4, 4))
            n = int(t_x/8)
            for col in range(x_shape) :
                for i in range(n) :
                    hout = np.hstack((hout, 
                        self.GBC_palette_map[:,col].reshape(y_shape, 1, 4, 4)))
            self.GBC_palette_map = hout.copy()
            x_shape = self.GBC_palette_map.shape[1]
        if y_shape != 18 : 
            vout = np.empty((0, x_shape, 4, 4))
            n = int(t_y/8)
            for row in range(y_shape) :
                for i in range(n) :
                    vout = np.vstack((vout, 
                        self.GBC_palette_map[row,:].reshape(1, x_shape, 4, 4)))
            self.GBC_palette_map = vout.copy()
            y_shape = self.GBC_palette_map.shape[0]

        output_image = self.output_canvas.image_no_zoom_PIL_RGB.copy()

        class GBTile :
            def __init__(self, bits) :
                self.bits = bits.copy()
                self.id = ""
                for b in reversed(self.bits) :
                    self.id+=str(format(int(b, 2), "x"))
                for i in range(len(self.bits)) :
                    self.bits[i] = GBC_hex_format(
                        format(int(self.bits[i], 2), "x").upper())
            def __eq__(self, rhs) :
                return self.id == rhs.id
            def __ne__(self, rhs) :
                return not (self==rhs)

        palettes_indices = []
        tiles_indices = []
        tiles = []
        for j in range(18) :
            for i in range(20) :
                palette = self.GBC_palette_map[j][i]
                lpalette = palette.tolist()
                palette_index = self.palettes.tolist().index(palette.tolist())
                palettes_indices.append(palette_index)

                box = (i*8, j*8, (i+1)*8, (j+1)*8)
                tile = output_image.crop(box)
                tile = np.array(tile)
                # tile_palette_index is an 8x8 array just like tile. The tile
                # array is such that each [j,i] element contains an rgb color.
                # tile_palette_index instead is such that each [j,i] element
                # is an integer between 0 and 3 that represents one of the four
                # colors in palette. In particular, that number is the index
                # of the color in the palette list that corresponds to the 
                # color in position [j,i] of tile.
                tile_palette_index = self.data_to_palette_index_map(
                    tile.reshape(tile.shape[0]*tile.shape[1], tile.shape[2]), 
                    palette).reshape(tile.shape[0], tile.shape[1])

                '''
                Quick reminder on how Game Boy (Color or not) tiles work.
                All of the graphics is based on 8x8 pixel tiles. Each tile is a
                collection of numbers ranging from 0 to 3, representing one of
                the four possible colors a pixel can assume. The actual color
                value (in hex RGB 555 format) is stored elsewhere, in a map
                that indicats which tile uses which palette (i.e. which set of 
                four colors). The big difference between the Game Boy and the 
                Game Boy Color is that the former supports only one palette for
                all tiles (and you cannot really change it, it is white, black,
                and two shades of gray), while the latter supports a maximum of
                8 different color palettes. Regardless, the fundamental 
                representation is the same. Take the following tile:

                0 1 2 2 1 1 3 0
                0 2 2 2 2 3 3 1
                1 0 0 0 2 0 0 2
                2 1 1 1 3 3 3 2
                0 2 1 3 0 2 1 3
                0 0 0 1 1 0 0 0
                2 2 3 3 1 3 0 0
                3 2 1 0 3 2 1 0
                
                The way this is stored is the following. For each line,
                convert each number into a binary format and store the low and
                the high bits for each number (there is only 2 bits as the 
                numbers are in the 0-3 range) in separate arrays. Then convert
                each array into hex numbers and store them in a little endian
                way (the row of the low bits first, the row of the high bits
                second). If this sounds confusing, let us make an example, let
                us consider the first row:

                0 1 2 2 1 1 3 0

                After binary conversion, we have:

                00 01 10 10 01 01 11 00

                For each number, the first digit is the high bit, and the 
                second digit is the low bit (). Now, store the low bits and 
                high bits separately, so that:

                low_bits =  [0 1 0 0 1 1 1 0]
                high_bits = [0 0 1 1 0 0 1 0]

                the low and high bits are then both translated into hex numbers
                (the leading 0s are inconsequential but have been bracketed for
                clarity) :

                low_bits =  [0 1 0 0 1 1 1 0] = (0)1001110 = 0x4E
                high_bits = [0 0 1 1 0 0 1 0] = (00)110010 = 0x32

                Thus, the first row is converted into two hex numbers in the 
                0-255 range. These two numbers are stored in memory in a little
                endian way, so that the final representation of the first row
                in memory is 0x4E 0x32 in two adjecent memory locations wherein
                the address of the second is the adderss of the first + 1.
                This is repeated for all 8 rows, so that each tile is 
                represented as 16 numbers in hex format in the 0-255 range 
                stored in 16 adjacent memory addresses in a little endian 
                format.
                '''
                tile_bits = []
                for row in tile_palette_index :
                    # Get low and high bits in string binary format, then 
                    # convert to hex, and pad with leading 0s if necessary
                    low_bits = np.array2string(
                        np.remainder(row, 2).astype(int), 
                        separator="").lstrip("[").rstrip("]")
                    high_bits = np.array2string(
                        np.remainder(np.floor(row/2), 2).astype(int), 
                        separator="").lstrip("[").rstrip("]")
                    tile_bits.append(low_bits)
                    tile_bits.append(high_bits)
                
                # Add tile to tiles (i.e. pattern table) only if id did not
                # already appear, and set the correct tile_index for this tile
                # accordingly
                tile = GBTile(tile_bits)
                tile_index = None
                for k, tilek in enumerate(tiles) :
                    if tilek == tile :
                        tile_index = k
                        break
                if tile_index == None :
                    tiles.append(tile)
                    tile_index = len(tiles)-1
                tiles_indices.append(tile_index)

        # Write the source header, the only info it requires is the number of
        # palettes that are present and info on whether the second memory bank
        # for the tile table is necessary (only if I have more than 256 tiles)
        self.asm_source = vd.fill_from_source_header_to_palettes_start(
            len(self.palettes), len(tiles) > 256)

        # Write palettes to source
        for i, palette in enumerate(self.palettes) :
            self.asm_source += ("               ; Palette "+str(i)+"\n")
            for j, color in enumerate(palette) :
                color_hex_rgb555 = format(
                    np.floor(color[0]/8).astype(int)+
                    np.floor(color[1]/8).astype(int)*32+
                    np.floor(color[2]/8).astype(int)*1024, "x").upper()
                while len(color_hex_rgb555) < 4 :
                    color_hex_rgb555 = "0"+color_hex_rgb555
                hi_nibble = color_hex_rgb555[0]+color_hex_rgb555[1]
                lo_nibble = color_hex_rgb555[2]+color_hex_rgb555[3]
                color_line = ("    DB $"+lo_nibble+",$"+hi_nibble)
                color_line += (" ; $ 16-bit RGB = "+
                    np.array2string(np.array(color).astype(int))+"\n")
                self.asm_source += color_line

        # 
        self.asm_source += vd.fill_from_palettes_end_to_bank0_tile_start()

        # Write tiles to bank0
        for i, tile in enumerate(tiles) :
            if i < 256 :
                self.asm_source += ("    DB ")
                for j, line in enumerate(tile.bits) :
                    if j != 8 :
                        self.asm_source += (line)
                    else :
                        lineNum = GBC_hex_format(format(i, "x").upper())
                        self.asm_source += (" ; tile "+str(i)+" / "+
                            lineNum+"\n"+"    DB "+line)
                    if j < 15 and j != 7:
                        self.asm_source += (",")
                self.asm_source += ("\n")

        #
        self.asm_source += vd.fill_from_bank0_tile_end_to_bank1_tile_start()

        # Write tiles that go to bank 1 of the tile map
        for i, tile in enumerate(tiles) :
            if i >= 256 :
                self.asm_source += ("    DB ")
                for j, line in enumerate(tile.bits) :
                    if j != 8 :
                        self.asm_source += (line)
                    else :
                        lineNum = GBC_hex_format(format(i, "x").upper())
                        self.asm_source += (" ; tile "+str(i)+" / "+
                            lineNum+"\n"+"    DB "+line)
                    if j < 15 and j != 7:
                        self.asm_source += (",")
                self.asm_source += ("\n")

        #
        self.asm_source += vd.fill_from_bank1_tile_end_to_bank0_map_start()

        # Write actual map
        for i in range(18) :
            self.asm_source += ("    DB ")
            for j in range(20) :
                I = tiles_indices[20*i+j]
                if I >= 256 :
                    I -= 256
                n = GBC_hex_format(format(I, "x").upper())
                if j != 10 :
                    self.asm_source += (n)
                else :
                    self.asm_source += (" ; line "+str(i)+"\n"+"    DB "+n)
                if j < 19 and j != 9 :
                    self.asm_source += (",")
            self.asm_source += ("\n")

        #
        self.asm_source += vd.fill_from_bank0_map_end_to_bank1_map_start()

        # Write palette map
        for i, palettes_index in enumerate(palettes_indices) :
            if i%10 == 0 :
                self.asm_source += ("    DB ")
            # Bit 3 of pi set to 1 tells to use bg characters in bank1
            # So, bin 00001000 == dec 8, and we need to add it to the palette 
            # number
            if tiles_indices[i] >= 256 :
                pi = GBC_hex_format(format((palettes_index+8), "x").upper())
            else :
                pi = GBC_hex_format(format((palettes_index), "x").upper())
            self.asm_source += (pi)
            if (i+1)%10 != 0 :
                self.asm_source += (",")
            elif (i+1)%20 != 0:
                self.asm_source += (" ; line "+str(np.floor(i/20).astype(int))+
                    "\n")
            else :
                self.asm_source += ("\n")

        #
        self.asm_source += vd.fill_from_bank1_map_end_to_source_end()

    def export_asm(self) :

        if not(self.output_is_GBC_compatible) :
            return
        if self.asm_source == "" :
            return
        file = asksaveasfile(mode='w', defaultextension=".asm",
            initialfile="main", filetypes=[("Assembly source file", ".asm")])
        if file :
            file.write(self.asm_source)

        # Clear source after saving file
        self.asm_source = ""

    def compile_gb(self) :
        
        # Currently only for Windows
        if platform != "win32":
            return

        # Create asm source code
        self.create_asm()

        if not(self.output_is_GBC_compatible) :
            return
        if self.asm_source == "" :
            return

        # Create dummy file which will be overwritten
        file = asksaveasfile(mode='w', defaultextension=".gb",
            initialfile="main", filetypes=[("GBC file", ".gb")])
        if not file :
            self.asm_source = ""
            return
        
        # Define names
        filename_with_ext = file.name.split("/")[-1]
        filename_without_ext = filename_with_ext.split(".")[0]
        folder_path = str(file.name).replace(filename_with_ext, "")

        # Name root for temporary files written to disk
        tmp = ''.join(
                random.choice(
                    string.ascii_uppercase+string.digits+string.ascii_lowercase
                    ) for _ in range(29))

        # Write asm source
        with open(tmp+".asm", "w") as o :
            o.write(self.asm_source)

        # Write dlls
        with open("libpng16.dll", "wb") as o:
            o.write(vd.libpng16_dll_x64)
        with open("zlib1.dll", "wb") as o:
            o.write(vd.zlib1_dll_x64)

        # Write and run exes to actually write the compiled .gb to the initial
        # dummy file
        with open(tmp+".exe", "wb") as o:
            o.write(vd.rgbasm_exe_x64)
        subprocess.call([tmp+".exe", "-o", tmp+".o", tmp+".asm"])
        with open(tmp+".exe", "wb") as o:
            o.write(vd.rgblink_exe_x64)
        subprocess.call([tmp+".exe", "-o", file.name, tmp+".o"])
        with open(tmp+".exe", "wb") as o:
            o.write(vd.rgbfix_exe_x64)
        subprocess.call([tmp+".exe", "-C", "-v", "-p", "0", file.name])

        # Remove all leftovers
        os.remove(tmp+".asm")
        os.remove(tmp+".o")
        os.remove(tmp+".exe")
        os.remove("libpng16.dll")
        os.remove("zlib1.dll")

        # Reset source
        self.asm_source = ""
        