// Switch
$(function() {
    $('.toggle-button').each(function(idx, ele) {
        var on = false;
        $(ele).click(function() {
            if( on )
                $(ele).removeClass('toggle-button-selected');
            else
                $(ele).addClass('toggle-button-selected');
            on = !on;

            var feature = 'Switch' + $(this, 'button').text();
            IoTtalk.update(mac, feature, Number(on));
        })
    });
});
