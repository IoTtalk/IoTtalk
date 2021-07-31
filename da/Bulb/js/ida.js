$(function () {
    csmapi.set_endpoint (window.location.origin);   //csmapi.set_endpoint ("http://IP:9999");
    var profile = {
        'dm_name': 'Bulb',
        'idf_list': [],
        'odf_list': [Luminance, Color_O],
    }
    
    var r = 255 ;
    var g = 255;
    var b = 0;
    var lum = 100;

    function draw () {
        var rr = Math.floor((r * lum) / 100);
        var gg = Math.floor((g * lum) / 100);
        var bb = Math.floor((b * lum) / 100);
        $('.bulb-top, .bulb-middle-1, .bulb-middle-2, .bulb-middle-3, .bulb-bottom, .night').css(
            {'background': 'rgb('+ rr +', '+ gg +', '+ bb +')'}
        );
    }

    function Luminance (data) {
        lum = data[0]
        draw();
    }

    function Color_O (data) {
        r = data[0];
        g = data[1];
        b = data[2];
        draw();
    }

    function ida_init () {
        $('font')[0].innerText = profile.d_name;
        draw();
    }

    var ida = {
        'ida_init': ida_init,
    };

    dai(profile, ida);
});
