// Knob
$(function() {
    // Init knob
    $('.knob-container').knobKnob({
        startDeg: -45,
        degRange: 270,
        initVal: 0.6,
        numColorbar: 31,
    });

    var lastVal = -1;
    function knobChecker() {
        // Check update
        var val = parseFloat($('.knob-container').val());
        if( val.toString() !== lastVal.toString() ) {
            lastVal = val;
            var feature = 'Knob' + $('#knob-page header select').val();
            if( window.d_name !== null )
                IoTtalk.update(mac, feature, val);
        }
        setTimeout(knobChecker, 250);
    }
    knobChecker();
});
