// Keypad
$(function() {
    $('#keypad-page .keypad button').click(function() {
        var feature = 'Keypad' + $('#keypad-page header select').val();
        IoTtalk.update(mac, feature, Number($(this).text()));
    });
});
