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

### IMPORTS ###################################################################

import time
import numpy as np
from PIL import Image, ImageOps, ImageTk

### CLASSES ###################################################################

class KMeans :

    def __init__(self, **kwargs) :

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
        scale = np.sqrt(max_pixels/n_pixels)
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
        
        # Convert back to image and draw to canvas
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
        scale = np.sqrt(max_pixels*n_palettes/n_pixels)
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
        # tiles of 16x16. Then, perform the color quantization and assemble
        # the output image from the processed tiles
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
        
        # Convert back to image and draw to canvas
        output_image = Image.fromarray(out.astype(np.uint8))
        self.output_canvas.set_zoom_draw_image(output_image)

    def process(self, **kwargs) :

        mode = kwargs.get("mode", self.default_mode_name)
        if mode == self.default_mode_name :
            self.process_default(**kwargs)
        elif mode == self.tiled_mode_name or mode == self.GBC_mode_name:
            self.process_tiled(**kwargs)
