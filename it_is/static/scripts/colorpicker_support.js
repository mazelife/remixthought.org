/* Supporting Scripts for using the colorpicker in the django admin */

var admin_options = {
    onSubmit: function(hsb, hex, rgb, el) {
        $(el).val(hex);
        $(el).css('background-color', '#' + hex);
        if (hsb.b < 60) {
            $(el).css('color', '#ffffff');
        }
        $(el).ColorPickerHide();
    },
    onBeforeShow: function () {
        $(this).ColorPickerSetColor(this.value);
    }
}

var ColorPickerAdmin = {
    init: function () {
        for (var i = 0; i < this.fields.length; i++) {
            var field, hex, hex_code, brightness;
            field = $(this.fields[i]);
            hex = field.attr('value');
            hex_code = "#" + hex;
            hex = parseInt(hex, 16);
            brightness = Math.max(hex >> 16, (hex & 0x00FF00) >> 8, (hex & 0x0000FF)) * 100/255;
            if (brightness < 60) {
                field.css('color', '#ffffff');
            }
            field.css('background-color', hex_code)
        }
    },
    fields: []
}

$(document).ready(function () { ColorPickerAdmin.init(); });