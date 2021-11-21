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
import tkinter as tk
from PIL import Image, ImageOps, ImageTk
from tkinter.filedialog import askopenfile, asksaveasfile

import VIMPRO_Data as vd

### FUNCTIONS #################################################################

# Add to dict under dict_key from kwargs[kwargs_key], if it exists
def add_from_kwargs(dict, dict_key, kwargs_key, kwargs) :
    if kwargs_key in kwargs :
        dict[dict_key] = kwargs[kwargs_key]

def void(*args, **kwargs) :
    pass

### CLASSES ###################################################################

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
        if self.selection_tool_b : # If button is slave
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

    def save_image(self, **kwargs) :
        if self.image_id :
            pixel_size = kwargs["pixelsize"]
            append_str = kwargs["appendstr"]
            file_exists = True
            filename = ""
            extension=".png"
            i = 0
            while file_exists :
                filename = self.filename+append_str+str(
                    i)+extension
                file_exists = os.path.exists(
                    self.filepath+filename)
                i+=1
            file = asksaveasfile(mode='w', defaultextension=".png",
                initialfile=filename, filetypes=[("PNG image file", ".png")],)
            if not file :
                return
            output_image = self.image_no_zoom_PIL.copy()
            final_size = (int(output_image.width*pixel_size), 
                int(output_image.height*pixel_size))
            output_image = output_image.resize(final_size, 
                resample=Image.NEAREST) 
            output_image.save(file.name)

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
            resample=mode))

    # Crop image
    def crop_image(self, **kwargs) :
        x0 = self.image_no_zoom_PIL.width
        y0 = self.image_no_zoom_PIL.height
        box = None
        # Crop from anchor and final resolution
        if "anchor" in kwargs and "size" in kwargs :
            anchor = kwargs["anchor"]
            x, y = kwargs["size"]
            x = min(x, x0)
            y = min(y, y0)
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
        self.sv.trace("w", self.on_write)

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

    def disable(self) :
        self.config(state=tk.DISABLED)

    def enable(self) :
        self.config(state=tk.NORMAL)

    def set(self, value) :
        self.sv.set(value)

    def set_min_value(self, value) :
        self.min_value = value
        if not self.valid :
            self.sv.set(value)

    def set_max_value(self, value) :
        self.max_value = value
        if not self.valid :
            self.sv.set(value)

    def unset_min_value(self) :
        self.min_value = 0

    def unset_max_value(self) :
        self.max_value = 1e69

    # Method to overwrite trace_add if needed
    def trace(self, *args) :
        self.sv.trace(*args)

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
        self.pads = kwargs.get("pads", kwargs)
        self.min_value = kwargs.get("minvalue")
        self.max_value = kwargs.get("maxvalue")
        self.aspect_ratio = kwargs.get("aspectratio", 0.0)

        self.slave = None
        self.master= None
        self.x_scale = None
        self.y_scale = None
        self.update_buffer_after_write = True

        self.buffers = {}
        self.auto_write_buffer = None
        self.last_modified = None
        self.update_in_progress = False

        self.label_dict = {}
        add_from_kwargs(self.label_dict, "text", "labeltext", kwargs)
        add_from_kwargs(self.label_dict, "width", "labelwidth", kwargs)
        self.l = tk.Label(self.top_level, anchor=tk.W, **self.label_dict)
        
        self.entry_dict = {}
        add_from_kwargs(self.entry_dict, "width", "entrywidth", kwargs)

        self.x_e = IntEntry(self.top_level, **self.entry_dict)

        self.aspect_ratio_b = ToggleButton(self.top_level, bd=0,
            onimage=ImageTk.PhotoImage(vd.lock_image), 
            offimage=ImageTk.PhotoImage(vd.ulock_image), **self.entry_dict)
        self.aspect_ratio_b.config(command=self.on_toggle_aspect_ratio)        

        self.y_e = IntEntry(self.top_level, **self.entry_dict)
        
        if not kwargs.get("starthidden", False) :
            self.show()

        if self.min_value :
            self.x_e.set_min_value(self.min_value)
            self.y_e.set_min_value(self.min_value)
        if self.max_value :
            self.x_e.set_max_value(self.max_value)
            self.y_e.set_max_value(self.max_value)

        self.x_e.trace("w", self.on_write_x)
        self.y_e.trace("w", self.on_write_y)

    def disable(self) :
        self.x_e.config(state=tk.DISABLED)
        self.y_e.config(state=tk.DISABLED)
        self.aspect_ratio_b.config(state=tk.DISABLED)

    def enable(self) :
        self.x_e.config(state=tk.NORMAL)
        self.y_e.config(state=tk.NORMAL)
        self.aspect_ratio_b.config(state=tk.NORMAL)

    def hide(self) :
        self.l.grid_forget()
        self.x_e.grid_forget()
        self.hide_aspect_ratio_b()
        self.y_e.grid_forget()

    def hide_aspect_ratio_b(self) :
        self.aspect_ratio_b.grid_forget()

    def show(self) :
        self.l.grid(row=self.row, column=self.column, sticky=tk.W, 
            **self.pads[0])
        self.x_e.grid(row=self.row, column=self.column+1, sticky=tk.W+tk.E, 
            **self.pads[1])
        self.show_aspect_ratio_b()
        self.y_e.grid(row=self.row, column=self.column+3, sticky=tk.W+tk.E, 
            **self.pads[3])

    def show_aspect_ratio_b(self) :
        self.aspect_ratio_b.grid(row=self.row, column=self.column+2, 
            sticky=tk.W+tk.E, **self.pads[2])

    def set_max_value(self, t) :
        x, y = t
        self.x_e.set_max_value(x)
        self.y_e.set_max_value(y)

    def set_min_value(self, t) :
        x, y = t
        self.x_e.set_min_value(x)
        self.y_e.set_min_value(y)

    def unset_max_value(self, t) :
        x, y = t
        self.x_e.unset_max_value()
        self.y_e.unset_max_value()

    def unset_min_value(self, t) :
        x, y = t
        self.x_e.unset_min_value()
        self.y_e.unset_min_value()

    def set_slave(self, slave, **kwargs) :
        x, y = kwargs.get("xyscales", (None, None))
        self.x_scale = x
        self.y_scale = y
        self.slave = slave
        self.slave.master = self
        self.slave.last_modified = self.last_modified
        self.slave.aspect_ratio_b.toggled = not self.aspect_ratio_b.toggled
        self.slave.on_toggle_aspect_ratio()

    def free_slave(self) :
        try :
            self.slave.master = None
        except : # I know...
            pass
        self.slave = None
        self.x_scale = None
        self.y_scale = None

    def on_toggle_aspect_ratio(self) :
        self.aspect_ratio_b.on_toggle_change()
        self.aspect_ratio = self.x_e.value/self.y_e.value
        '''
        if self.aspect_ratio_b.toggled :
            if self.last_modified == "x" :
                self.update_complementary_x()
            elif self.last_modified == "y" :
                self.update_complementary_y()
        '''
        if self.slave :
            self.slave.last_modified = self.last_modified
            self.slave.aspect_ratio_b.toggled = \
                not self.aspect_ratio_b.toggled
            self.slave.on_toggle_aspect_ratio()

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
        if self.slave and self.x_scale and self.y_scale:
            self.slave.last_modified = self.last_modified
            self.slave.set_x(self.x_e.value*self.x_scale.value, False)
            self.slave.update_complementary_x()
        if self.auto_write_buffer :
            self.buffers[self.auto_write_buffer] = (self.x_e.value, 
                self.y_e.value)

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
        if self.slave and self.y_scale and self.x_scale:
            self.slave.last_modified = self.last_modified
            self.slave.set_y(self.y_e.value*self.y_scale.value, False)
            self.slave.update_complementary_y()
        if self.auto_write_buffer :
            self.buffers[self.auto_write_buffer] = (self.x_e.value, 
                self.y_e.value)

    def set_x(self, x, setaspectratio=True) :
        if setaspectratio :
            self.aspect_ratio = float(x)/float(self.y_e.value)
        self.x_e.set(x)

    def set_y(self, y, setaspectratio=True) :
        if setaspectratio :
            self.aspect_ratio = float(self.x_e.value)/float(y)
        self.y_e.set(y)

    def set(self, t) :
        x, y = t
        # This master reset/set is force the setting of the resolution entries
        # without triggering the "if self.master ..." condition in 
        # update_complementary_*
        master_buffer = self.master
        self.master = None
        self.aspect_ratio = float(x)/float(y)
        self.x_e.set(x)
        self.y_e.set(y)
        self.master = master_buffer

    def enable_auto_write_buffer(self, buffer_name) :
        self.auto_write_buffer = buffer_name
        #self.buffers[self.auto_write_buffer] = (self.x_e.value, self.y_e.value)

    def disable_auto_write_buffer(self) :
        #self.buffers[self.auto_write_buffer] = None
        self.auto_write_buffer = None

    def set_buffer(self, i, t=None) :
        x = self.x_e.value
        y = self.y_e.value
        if t :
            x, y = t
        self.buffers[i] = (x, y)
    
    def reset_from_buffer(self, i) : 
        if i in self.buffers :
            self.set(self.buffers[i])

    # Update out_res_y to be consistent with the current out_res_x if
    # the locked aspect ratio is toggled
    def update_complementary_x(self) :
        self.update_in_progress = True
        if self.aspect_ratio_b.toggled :
            if self.master and self.master.y_scale :
                new_y = int(self.master.y_e.value*self.master.y_scale.value)
            elif self.aspect_ratio != 0.0 :
                new_y = int(self.x_e.value/self.aspect_ratio)
            self.y_e.set(new_y)
        self.update_in_progress = False

    # Update out_res_x to be consistent with the current out_res_y if
    # the locked aspect ratio is toggled
    def update_complementary_y(self) :
        self.update_in_progress = True
        if self.aspect_ratio_b.toggled :
            if self.master and self.master.x_scale :
                new_x = int(self.master.x_e.value*self.master.x_scale.value)
            elif self.aspect_ratio != 0.0 :
                new_x = int(self.y_e.value*self.aspect_ratio)
            self.x_e.set(new_x)
        self.update_in_progress = False  

    def valid(self) :
        return (self.x_e.valid and self.y_e.valid)

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

# Classes for handling the log redirection
class StdoutDirector(object):

    def __init__(self, log_t) :
        self.log_t = log_t

    def write(self, msg):
        self.log_t.update_idletasks()
        self.log_t.insert(tk.END, msg)
        self.log_t.yview(tk.END)

    def flush(self):
        pass

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