/**
 * @name        jQuery KnobKnob plugin
 * @author      Martin Angelov
 * @version     1.0
 * @url         http://tutorialzine.com/2011/11/pretty-switches-css3-jquery/
 * @license     MIT License
 *
 * @patch       for IoTtalk by sunset1995
 *              the spec and implementation is totaly different from origin source
 */

(function($){

    // Mobile detector reference from http://stackoverflow.com/questions/3514784/what-is-the-best-way-to-detect-a-mobile-device-in-jquery
    window.isMobile = false;
    if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|ipad|iris|kindle|Android|Silk|lge |maemo|midp|mmp|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino/i.test(navigator.userAgent) 
        || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(navigator.userAgent.substr(0,4)))
        window.isMobile = true;

    // Inner knob logic
    $.fn.__knobKnob = function(props) {
        var options = $.extend({
            startDeg: -45,
            degRange: 270,
            initVal: 0.6,
            onUpdate: function(){}
        }, props || {});
    
        var tpl = '<div class="knob">\
                <div class="top"></div>\
                <div class="base"></div>\
            </div>';

        function norm(deg) {
            return (deg + (parseInt(Math.abs(-deg/360), 10)+1) * 360) % 360;
        }

        function rad2deg(rad) {
            return rad*180/Math.PI;
        }

        function getAngleDegree(v1, v2) {
            var dot = v1[0]*v2[0] + v1[1]*v2[1];
            var l1 = Math.sqrt(v1[0]*v1[0] + v1[1]*v1[1]);
            var l2 = Math.sqrt(v2[0]*v2[0] + v2[1]*v2[1]);
            var rad = Math.acos(dot/(l1*l2));
            if( isNaN(rad) )
                return 0;
            return rad2deg(rad);
        }

        function cross(v1, v2) {
            return v1[0]*v2[1] - v1[1]*v2[0];
        }


        return this.each(function(){
            var el = $(this);
            el.append(tpl);
            
            var knob = $('.knob',el),
                knobTop = knob.find('.top'),
                lastVector = null,
                val = options.initVal,
                doc = $(document);

            function updateKnob() {
                if( val>1.0 ) val = 1.0;
                else if( val<0.01 ) val = 0.0;
                var deg = options.startDeg + val * options.degRange;
                knobTop.css('transform','rotate('+deg+'deg) translate(-50%, -50%)');
                options.onUpdate(val);
                $(this).val(val);
            }
            updateKnob(val);


            knob.on('mousedown touchstart', function(e) {
                e.preventDefault();
                e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;

                var offset = knob.offset();
                var center = {
                    y: offset.top + knob.height()/2,
                    x: offset.left + knob.width()/2
                };

                if( !window.isMobile ) {
                    var deg = norm(rad2deg(Math.atan2(center.y-e.pageY, center.x-e.pageX)));
                    deg = norm(deg - props.startDeg);
                    val = deg / props.degRange;
                    if( deg-props.degRange > (360-props.degRange)/2 )
                        val = 0;
                    updateKnob(val);
                }

                knob.on('mousemove.rem touchmove.rem',function(e){
                    e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
                    
                    var nowVector = [
                        e.pageY - center.y,
                        e.pageX - center.x
                    ];
                    if(lastVector === null)
                        lastVector = nowVector;
                    var deg = getAngleDegree(nowVector, lastVector);
                    if( cross(nowVector, lastVector) < 0 )
                        deg = -deg;
                    
                    // Calculating knob val
                    val += deg/options.degRange;

                    lastVector = nowVector;
                    updateKnob();
                });
            
                doc.on('mouseup.rem  touchend.rem',function(){
                    knob.off('.rem');
                    doc.off('.rem');
                    
                    // Marking the last degree as invalid
                    lastVector = null;
                });
            });
        });
    };
    


    // Patch for IoTtalk
    var colors = [
        '#26e000','#2fe300','#37e700','#45ea00','#51ef00',
        '#61f800','#6bfb00','#77ff02','#80ff05','#8cff09',
        '#93ff0b','#9eff09','#a9ff07','#c2ff03','#d7ff07',
        '#f2ff0a','#fff30a','#ffdc09','#ffce0a','#ffc30a',
        '#ffb509','#ffa808','#ff9908','#ff8607','#ff7005',
        '#ff5f04','#ff4f03','#f83a00','#ee2b00','#e52000',
        '#ff0000',
    ];
    var deg2rad = Math.PI/180;

    $.fn.knobKnob = function(props) {
        props = $.extend({
            startDeg: -45,
            degRange: 270,
            initVal: 0.6,
            numColorbar: 31,
            onUpdate: function(){}
        }, props || {});

        var onUpdate = props.onUpdate;
        var minDeg = props.startDeg;
        var maxDeg = props.startDeg + props.degRange;

        if( props.numColorbar > 31 )
            props.numColorbar = 31;
        if( props.numColorbar < 2 )
            props.numColorbar = 2;

        return this.each(function() {
            var ele = $(this);
            // Knob content
            var knobBlock = $('<div class="knob-block">');
            
            // Knob controller
            $('<div class="control">').appendTo(knobBlock);
            $('<div class="zero-text">').text('0.0').css({
                top: -Math.sin(minDeg*deg2rad)*110+100,
                left: Math.cos((180-minDeg)*deg2rad)*110+100,
            }).appendTo(knobBlock);
            $('<div class="one-text">').text('1.0').css({
                top: -Math.sin(maxDeg*deg2rad)*110+100,
                left: Math.cos((180-maxDeg)*deg2rad)*110+100,
            }).appendTo(knobBlock);

            var logger = $('<div class="logger">').appendTo(knobBlock);
            
            // Knob color bar
            var deg = props.startDeg;
            var cid = 0;
            var degStep = parseInt(props.degRange/(props.numColorbar-1), 10);
            var colStep = 30/(props.numColorbar-1);
            for(var i=0; i<props.numColorbar; ++i) {
                // Create the colorbars
                $('<div class="colorBar">').css({
                    width: (i%5==0)? '30px' : '10px',
                    background: colors[Math.floor(cid)],
                    transform: 'translate(-50%, -50%) rotate('+deg+'deg)',
                    top: -Math.sin(deg*deg2rad)*80+100,
                    left: Math.cos((180-deg)*deg2rad)*80+100,
                }).appendTo(knobBlock);

                deg += degStep;
                cid += colStep;
            }

            // Knob color bar animation            
            var colorBars = knobBlock.find('.colorBar');
            props.onUpdate = function(val) {
                var numBars = Math.round(colorBars.length * val);
                colorBars.addClass('unactive').slice(0, numBars).removeClass('unactive');
                $(ele).val(val);
                $(logger).text(val.toFixed(3));
                onUpdate(val);
            }
            knobBlock.find('.control').__knobKnob(props, this);

            // Knobalize
            knobBlock.appendTo(this);
            knobBlock = null; 
        });
    };

})(jQuery);
