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

from operator import is_
import numpy as np
import taichi as ti
from taichi_glsl import vec2
from PIL import Image

### CONSTANTS AND INITIALIZATION ##############################################

'''
# Init taichi parallel computing architecture (CUDA if available)
try :
    ti.init(arch=ti.gpu)
    NP_TYPE = np.uint8
    TI_TYPE = ti.uint8
except :
    ti.init(arch=ti.opengl)
    NP_TYPE = np.int32
    TI_TYPE = ti.i32
'''

# CUDA is cool and works, but for these sorts of applications OpenGL is just
# faster to load/start. Uncomment the previous bit if cuda desired (and 
# available)
ti.init(arch=ti.opengl)
NP_TYPE = np.int32
TI_TYPE = ti.i32

### FUNCTIONS #################################################################

def get_from_kwargs_or_default(key, kwargs, default) :
    if key in kwargs :
        return kwargs[key]
    return default

### CLASSES ###################################################################

@ti.data_oriented
class OutlineShader :
    def __init__(self, image:Image, **kwargs) :
        
        #
        self.data = np.array(image.convert("RGBA"))
        self.resolution = vec2(self.data.shape[0], self.data.shape[1])
        
        # CPU array of all pixels in data
        self.screen_array = np.full((self.resolution.x, self.resolution.y, 4),
            [0,0,0,0], NP_TYPE)
        # GPU array of all pixels in data
        self.screen_field = ti.Vector.field(4, TI_TYPE, self.resolution)
        self.screen_field_0 = ti.Vector.field(4, TI_TYPE, self.resolution)
        
        # Options
        self.outline_width = get_from_kwargs_or_default("outlinewidth", kwargs,
            1)
        self.outline_color = np.array(get_from_kwargs_or_default(
            "outlinecolor", kwargs, [0,0,0,255]))
        self.alpha_threshold = get_from_kwargs_or_default("alphathreshold", 
            kwargs, 255)
        
        # Set outline color in GPU
        self.outline_color_field = ti.Vector.field(4, TI_TYPE, 1)
        for i in range(4) :
            self.outline_color_field[0][i] = self.outline_color[i]

    def apply(self) :
        # Run ------------------------#
        # Move CPU data to GPU
        self.screen_field.from_numpy(self.data.astype(NP_TYPE))
        # Find and mark outline
        for q in range(self.outline_width) :
            self.kernel_apply()
        # Move GPU data back to CPU
        self.screen_array = self.screen_field.to_numpy().astype(np.uint8)
        return (Image.fromarray(self.screen_array))

    @ti.kernel
    def kernel_apply(self)  :
        r = self.resolution
        outline_color = self.outline_color_field[0]

        # fg is fragment coord, a tuple of x, y (goes from 0 to res in each
        # dir). 
        # Copy to buffer on which shader is actually applied
        for fg in ti.grouped(self.screen_field) :
            self.screen_field_0[fg.x, fg.y] = \
                self.screen_field[fg.x, fg.y]
        
        # Apply shader
        for fg in ti.grouped(self.screen_field) :
            col = self.screen_field_0[fg.x, fg.y]
            if col[3] != 0 :
                continue
            is_boundary = False
            i = -1
            while (not is_boundary and i <= 1) :
                j = -1
                x = min(max(fg.x+i, 0), r.x-1)
                while (not is_boundary and j <= 1) :
                    y = min(max(fg.y+j, 0), r.y-1)
                    if self.screen_field_0[x, y][3] >= \
                        self.alpha_threshold :
                        self.screen_field[fg.x, fg.y] = \
                            outline_color
                        is_boundary = True
                    j+=1
                i+=1
