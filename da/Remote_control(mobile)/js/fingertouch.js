$(function() {
    [
        'body > main > section > header > select',
        'body > nav',
        '.keypad',
        '.knob-container',
        '.switch',
    ].forEach(function(selector) {
        $(selector).on('mousedown touchstart', function(e) {
            e.stopPropagation();
        });
    });

    var nowPage = 0;
    var pages = [];
    $('body > nav > div').each(function(idx, ele) {
        var pageId = $(ele).attr('for'); 
        pages.push({
            'dx': $('#' + pageId).offset().left,
            'enter': function() {
                $(ele).click();
            },
        });
    });

    var slider = $('body > main');
    $('body').on('mousedown touchstart', function(e) {
        e.preventDefault();
        e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;

        var ax = slider.offset().left;
        var ox = e.pageX;
        var dx = 0;
        var tx = ax + dx;
        var nowPage = 0;
        for(var i=0; i<pages.length; ++i)
            if( Math.abs(pages[i].dx + $('body > main').offset().left) < 
                    Math.abs(pages[nowPage].dx + $('body > main').offset().left) )
                nowPage = i;

        slider.removeClass('transition');

        $('body').on('mousemove.rem touchmove.rem', function(e) {
            e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
            dx = e.pageX - ox;
            tx = ax + dx;
            slider.css('transform', 'translate('+tx+'px,0)');
        });

        $('body').on('mouseup.rem  touchend.rem', function(e) {
            $('body').off('.rem');
            slider.addClass('transition');

            if( Math.abs(dx/slider.width()) > 0.3 ) {
                var nextPage = nowPage + (dx>0 ? -1 : 1);
                if( pages[nextPage] ) {
                    pages[nextPage].enter();
                    return;
                }
            }
            pages[nowPage].enter();
        });
    });
});
