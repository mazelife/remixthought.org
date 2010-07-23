import colorsys
import math
from os import path
try:
   import cPickle as pickle
except:
   import pickle
import random

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.db import models

# Provide a ``product`` function for pre-2.6 users.
try:
    from itertools import product
except ImportError:
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

import app_settings

"""

This module handles the creation and assignment of tag colors and defines a 
Django widget and field for a GUI javascript-based colorpicker.

"""

class ColorPicker(object):
    """
    A class which provides an object that manages the creation and assignment 
    of new colors for tags. On init, the color picker will create a list of
    450,000 colors. These will be stored in a python pickle file (the location
    of this can be set in your settings file:   
    ``STATEMENTS_COLOR_DATA_FILE_PATH``). Requests for new tags will draw down 
    from this pool. Should the initial set be exhausted, new random colors will 
    begin to be generated. 
    """
    
    available_colors = None
    
    pickle_file = path.join(app_settings.COLOR_DATA_FILE_PATH, 'colors.data')
    
    def __init__(self, reset=False):
        if not reset and path.exists(self.pickle_file):
            fh = open(self.pickle_file)
            self.available_colors = pickle.loads(fh.read())
            fh.close()
        else:
            colors = self._create_colors()
            fh = open(self.pickle_file, 'w')
            fh.write(pickle.dumps(colors))
            fh.close()
            self.available_colors = colors
            
    
    def _create_colors(self):
        available_colors = []
        hues = xrange(0, 360, 2)
        saturations = xrange(80, 100, 2)
        values = xrange(75, 93, 2)
        for h, s, v in product(hues, saturations, values):
            h = round(h/360.0, 2)
            s = round(s/100.0, 2)
            v = round(v/100.0, 2)
            rgb = colorsys.hsv_to_rgb(h,s,v)
            hex_code = "%02X%02X%02X" % tuple([int(i * 255) for i in rgb])
            available_colors.insert(0, hex_code)
        return available_colors
    
    def _save_colors(self):
        fh = open(self.pickle_file, 'w')
        fh.write(pickle.dumps(self.available_colors))
        fh.close()
        
    def _get_colors(self):
        while len(self.available_colors) > 0:
            index = random.randrange(0, (len(self.available_colors)))
            color = self.available_colors[index]
            del self.available_colors[index]
            self._save_colors()
            yield color
    
    def get_color(self):
        """
        Get one color at a time. Once the intial set of 450,000 is 
        exhausted, start returning random colors (still within the 
        colorspace).
        """
        if not hasattr(self, 'colorset'):
            self.colorset = self._get_colors()
        if not self.colorset:
            return self.get_random_color()
        try:
            return self.colorset.next()
        except StopIteration:
            self.colorset = False
            return self.get_random_color()

    def get_random_color(self):
        h = round(random.randint(0, 360)/360.0, 2)
        s = round(random.randint(80, 100)/100.0, 2)
        v = round(random.randint(75, 93)/100.0, 2)
        rgb = colorsys.hsv_to_rgb(h,s,v)
        return "%02X%02X%02X" % tuple([int(i * 255) for i in rgb])

color_picker = ColorPicker()

class ColorPickerWidget(forms.TextInput):
    class Media:
        css = {
            'all': (
                settings.MEDIA_URL + 'styles/colorpicker.css',
            )
        }
        js = (
            settings.MEDIA_URL + 'scripts/jquery.min.js',
            settings.MEDIA_URL + 'scripts/colorpicker.js',
            settings.MEDIA_URL + 'scripts/colorpicker_support.js',            
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        super(ColorPickerWidget, self).__init__(attrs=attrs)

    def render(self, name, value, attrs=None):
        rendered = super(ColorPickerWidget, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            $('#id_%s').ColorPicker(admin_options).bind('keyup', function(){
            	$(this).ColorPickerSetColor(this.value);
            });
            ColorPickerAdmin.fields.push($('#id_%s')[0])
            </script>''' % (name, name))

class ColorField(models.CharField):
    """Field for a GUI HTML/Javascript-based color picker."""
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorPickerWidget
        return super(ColorField, self).formfield(**kwargs)
