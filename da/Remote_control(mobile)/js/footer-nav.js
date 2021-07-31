// Handler page change
$(function() {
    var main = $('body > main');

    $('body > nav > div').each(function(idx, ele) {
        var targetId = $(ele).attr('for');
        var offset = idx*100;
        if( $('#'+targetId).length === 0 )
            return;
        $('#'+targetId).css('left', offset + '%');
        $(ele).click(function() {
            main.css('transform', 'translate(-'+offset+'%, 0)');
            $('body > nav > div').removeClass('active');
            $(this).addClass('active');
        });
    });

    $('body > nav > div').first().click();
});
