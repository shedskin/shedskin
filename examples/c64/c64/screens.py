#!/usr/bin/env python


from . import sprite as sprites
from . import palette
from . import pixbufs

"""
depending on row:
mode 0
mode 4
mode 5
fill pixbuf data depending on current row (i.e. on increase_raster_position).
TODO: row count, bit 3 0x11; column count
TODO: remember mode
sprites and collision detection by the ORIGINAL data.
"""
WIDTH = 366 # 320
HEIGHT = 300 # 240
cell_column_count = 40 # FIXME configurable.
class Screen(object):
    def __init__(self, VIC, CIA2):
        #self.GDK_pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, WIDTH, HEIGHT)
        #self.GDK_pixbuf.fill(0x000000FF)
        self.pixbuf_obj = pixbufs.Pixbuf()
        self.VIC = VIC
        self.MMU = VIC.MMU
        self.CIA2 = CIA2
        #self.pixbuf = (HEIGHT * WIDTH) * [0]
        self.props = VIC.props
        self.current_scanline = (WIDTH + sprites.WIDTH * 2) * [0]
        self.C64_scanline = WIDTH * [0] # for collision detection
        self.sprite_scanline = sprites.WIDTH * [0]
        self.raster_position = 0
        self.client_raster_position = 0
        self.breakpoint_raster_position = 0
        self.B_enable_raster_interrupt = False
        self.B_enable_sprite_background_collision_interrupt = False
        self.B_enable_sprite_sprite_collision_interrupt = False
        self.raw_interrupt_status = 0
    def get_rendered_pixbuf(self):
        return(self.pixbuf_obj.native_pixbuf)
    def render_sprites(self, B_foreground):
        props = self.props
        sprite_scanline = self.sprite_scanline
        row_index = self.raster_position
        if row_index < props.first_row or row_index > props.last_row:
            return
        client_index = row_index
        for i in range(7, -1, -1):
            sprite_selector = 1 << i
            if ((props.sprite_priority & sprite_selector) == 0) != B_foreground or (props.sprite_enabled & sprite_selector) == 0:
                continue
            sprite_size_Y = sprites.HEIGHT << (1 if props.sprite_expand_vertically & sprite_selector else 0)
            sprite_Y = props.sprite_Y[i]
            page64_index = self.VIC.VIC_read_memory(props.video_offset + 1024 - 8 + i, 1) & 0xFF
            base = page64_index * 64 # default: 0
            sprite_data = [self.VIC.VIC_read_memory(base + iii) for iii in range(64)] # actually 63, but :P
            if client_index >= sprite_Y and client_index < sprite_Y + sprite_size_Y:
                expand_vertically = (2 if props.sprite_expand_vertically & sprite_selector else 1)
                expand_horizontally = (2 if props.sprite_expand_horizontally & sprite_selector else 1)
                client_Y = (client_index - sprite_Y) >> (expand_vertically - 1)
                cell_inner_Y = client_Y & 7
                for k in range(sprites.WIDTH):
                    sprite_scanline[k] = 0
                sprite_size_X = sprites.WIDTH << (expand_horizontally - 1)
                sprite_X = props.sprite_X[i]
                data_offset = client_Y * 3
                #print i, client_index, base, data_offset, client_Y
                primary_color = palette.get_RGBA32_pixel(props.sprite_primary_color[i] & 0xF)
                B_multicolor_enabled = (props.sprite_multicolor_enabled & sprite_selector) != 0
                if B_multicolor_enabled:
                    sprite_multicolor_0 = palette.get_RGBA32_pixel(props.sprite_multicolor_0 & 0xF)
                    sprite_multicolor_1 = palette.get_RGBA32_pixel(props.sprite_multicolor_1 & 0xF)
                    colors = [0, sprite_multicolor_0, primary_color, sprite_multicolor_1] # FIXME check that
                    v = sprite_data[data_offset]
                    mask = 0xC0 # first two bits
                    shift = 6
                    for x in range(0, sprites.WIDTH, 2):
                        pixel = colors[(v & mask) >> shift]
                        sprite_scanline[x] = pixel
                        sprite_scanline[x+1] = pixel
                        mask >>= 2
                        shift -= 2
                        if mask == 0:
                            mask = 0xC0
                            shift = 6
                            data_offset += 1
                            v = sprite_data[data_offset]
                else:
                    v = sprite_data[data_offset]
                    mask = 0x80
                    for x in range(sprites.WIDTH):
                        if v & mask:
                            sprite_scanline[x] = primary_color
                        mask >>= 1
                        if mask == 0:
                            mask = 0x80
                            data_offset += 1
                            v = sprite_data[data_offset]
                # sprite_scanline now contains the UNSCALED scanline, with 0 for the transparent bits.
                x = sprite_X
                if x >= 0 and x < WIDTH:
                    if expand_horizontally > 1:
                        for j in range(sprites.WIDTH):
                            v = sprite_scanline[j]
                            if v:
                                self.current_scanline[x] = v
                            x += 1
                            if v:
                                self.current_scanline[x] = v
                            x += 1
                    else:
                        for j in range(sprites.WIDTH):
                            if sprite_scanline[j]:
                                self.current_scanline[x] = sprite_scanline[j]
                            x += 1
    def render_background(self):
        for i in range(WIDTH):
            self.C64_scanline[i] = 0
        props = self.props
        background_color_0 = palette.get_RGBA32_pixel(props.background_color_0)
        for x in range(props.first_column, props.last_column + 1):
            self.current_scanline[x] = background_color_0
    def render_border(self):
        index = self.raster_position
        props = self.props
        border_color = palette.get_RGBA32_pixel(self.props.border_color)
        if index < props.first_row or index > props.last_row:
            for x in range(WIDTH):
                self.current_scanline[x] = border_color
        else:
            for x in range(props.first_column): # left border
                self.current_scanline[x] = border_color
            for x in range(props.last_column + 1, WIDTH): # right border
                self.current_scanline[x] = border_color
    def render_scanline(self):
        index = self.raster_position
        # FIXME viewport_row, viewport_column
        self.render_background()
        self.render_sprites(False)
        props = self.props
        if index >= props.first_row and index <= props.last_row:
            client_index = index - props.first_row
            mode = self.props.mode
            # mode = <multicolor><extended_background><bitmap>
            # mode = <MCM><ECM><BMM>
            cell_origin = self.props.video_offset
            bitmap_origin = self.props.character_bitmaps_offset # + (self.CIA2.VIC_bank * 4096) # bank offset
            cell_index = cell_column_count * (client_index >> 3)
            cell_inner_Y = client_index & 7
            cell_beginning = cell_origin + cell_index
            cell_count = cell_column_count
            ox = 0
            MMU = self.MMU
            VIC = self.VIC
            cell_values = VIC.load_12_chunk(cell_beginning, cell_count)
            cell_values_i = -1
            color = 0
            mask = 0x80
            if mode == 0 or mode == 4: # text mode, multicolor text mode
                for x in range(props.first_column, props.last_column + 1):
                    if (ox & 7) == 0: # next cell
                        cell_values_i += 1
                        cell_value = cell_values[cell_values_i]
                        color_index = (cell_value >> 8)
                        color = palette.get_RGBA32_pixel(color_index & 0xF)
                        bitmap_beginning = bitmap_origin + (cell_value & 0xFF) * 8 + cell_inner_Y
                        bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                        if mode != 0 and color_index >= 8: # were already done earlier
                            bitmap_value = 0
                    if bitmap_value & mask:
                        self.current_scanline[x] = color
                    mask = mask >> 1
                    if mask == 0:
                        mask = 0x80
                    ox += 1
            cell_values_i = -1
            ox = 0
            mask = 0x80
            if mode == 1: # bitmap mode
                bitmap_beginning = bitmap_origin + (cell_index << 3) + cell_inner_Y
                for x in range(props.first_column, props.last_column + 1):
                    if (ox & 7) == 0: # next cell
                        cell_values_i += 1
                        cell_value = cell_values[cell_values_i]
                        foreground_color = palette.get_RGBA32_pixel((cell_value >> 4) & 0xF)
                        background_color = palette.get_RGBA32_pixel((cell_value >> 0) & 0xF)
                        bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                    self.current_scanline[x] = foreground_color if bitmap_value & mask else background_color
                    mask = mask >> 1
                    if mask == 0:
                        mask = 0x80
                        bitmap_beginning += 8
                        bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                    ox += 1
            elif mode == 2: # extended background (text)
                background_colors = [palette.get_RGBA32_pixel(props.background_color_0), 
                                     palette.get_RGBA32_pixel(props.background_color_1), 
                                     palette.get_RGBA32_pixel(props.background_color_2), 
                                     palette.get_RGBA32_pixel(props.background_color_3)]
                for x in range(props.first_column, props.last_column + 1):
                    if (ox & 7) == 0: # next cell
                        cell_values_i += 1
                        cell_value = cell_values[cell_values_i]
                        color_index = (cell_value >> 8) & 0xF
                        color = palette.get_RGBA32_pixel(color_index & 0xF)
                        background_color = background_colors[(cell_value & 0xFF) >> 6]
                        bitmap_beginning = bitmap_origin + (cell_value & 0x3F) * 8 + cell_inner_Y
                        bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                    self.current_scanline[x] = color if bitmap_value & mask else background_color
                    mask = mask >> 1
                    if mask == 0:
                        mask = 0x80
                    ox += 1
            elif mode == 3: # invalid
                pass
            elif mode == 4: # multicolor text
                B_skip = False
                multi_colors = [palette.get_RGBA32_pixel(props.background_color_0), 
                                palette.get_RGBA32_pixel(props.background_color_1), 
                                palette.get_RGBA32_pixel(props.background_color_2), 
                                palette.get_RGBA32_pixel(props.background_color_3)]
                shift = 6
                mask = 3
                for x in range(props.first_column, props.last_column + 1, 2):
                    if (ox & 7) == 0: # next cell
                        cell_values_i += 1
                        cell_value = cell_values[cell_values_i] # IndexError here
                        color_index = (cell_value >> 8)
                        # ?? color = palette.get_RGBA32_pixel(color_index & 0xF)
                        if (color_index & 8) == 0: # not multicolor: already done
                            B_skip = True
                        else:
                            multi_colors[3] = palette.get_RGBA32_pixel(color_index & 7)
                            B_skip = False
                            bitmap_beginning = bitmap_origin + (cell_value & 0xFF) * 8 + cell_inner_Y
                            bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                    if not B_skip:
                        self.current_scanline[x] = self.current_scanline[x+1] = multi_colors[(bitmap_value >> shift) & mask]
                    shift -= 2
                    if shift < 0:
                        shift = 6
                    ox += 2
            elif mode == 5: # multicolor bitmap mode
                # bits 01 is treated as "background".
                bitmap_origin = bitmap_origin & 0x2000 # take only bit 13 just in case.
                bitmap_beginning = bitmap_origin + (cell_index << 3) + cell_inner_Y
                bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                shift = 6
                mask = 3
                for x in range(props.first_column, props.last_column + 1, 2):
                    if (ox & 7) == 0: # next cell
                        cell_values_i += 1
                        cell_value = cell_values[cell_values_i]
                        color_indices = [props.background_color_0 & 0xF, (cell_value >> 4) & 0xF, cell_value & 0xF, cell_value >> 8]
                    vv = (bitmap_value >> shift) & mask
                    if vv > 0:
                        self.current_scanline[x + 1] = self.current_scanline[x] = palette.get_RGBA32_pixel(color_indices[vv])
                    shift -= 2
                    if shift < 0:
                        shift = 6
                        bitmap_beginning += 8
                        bitmap_value = VIC.VIC_read_memory(bitmap_beginning, 1)
                    # TODO: #b01 is background as far as collision detection is concerned.
                    ox += 2
        self.render_border()
        self.render_sprites(True)
        self.flip()
    def flip(self):
        # actually put the finished line into the pixbuf.
        beginning_offset = WIDTH * self.raster_position
        self.pixbuf_obj.merge(beginning_offset, self.current_scanline)
        #for x in range(WIDTH):
        #   self.pixbuf[beginning_offset] = self.current_scanline[x]
        #   beginning_offset += 1
    def increase_raster_position(self):
        self.render_scanline()
        self.client_raster_position = self.raster_position # FIXME (HEIGHT + self.raster_position - 3) % HEIGHT
        self.raster_position += 1
        if self.raster_position >= HEIGHT:
            self.raster_position = 0
            # TODO self.repaint()
        if self.B_enable_raster_interrupt and self.client_raster_position == self.breakpoint_raster_position:
            self.raw_interrupt_status |= 1
