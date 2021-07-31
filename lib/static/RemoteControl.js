let device_id = null;
let _ENDPOINT =  window.origin;
let password = ''

function set_device_id(d_id){
    device_id = d_id;
    csmapi.set_endpoint(_ENDPOINT);   
}

function get_alias(device_id, df_name, callback){
    var alias;
    var ajax_obj = $.ajax({
        url: _ENDPOINT +'/get_alias/' + device_id+ '/' + df_name,
        type: 'GET',
        data: {alias},
    }).done(function(alias){
        if(typeof callback === 'function') callback(df_name, alias['alias_name'][0]);
    });
}

function update_alias(df_name, alias){
    if (alias!=undefined) $('.'+df_name)[0].innerText = alias;
}

function load_alias(device_id, df_main_name, count){
    for(var index=1; index<=count; index++){
	    get_alias(device_id, df_main_name+index.toString(), update_alias);
    }
}

function update_switch_state(data, exception, df_name){
    if (data.length != 0)
        if (data[0][1][0] == 1) $('#'+df_name).bootstrapToggle('on');
	else $('#'+df_name).bootstrapToggle('off');
}

function load_state(df_main_name, count, callback){
    for(var index=1; index<=count; index++){
        csmapi.pull(device_id, password, df_main_name+String(index), callback);
    }
}

function close_page(result){
    if (result){ console.log('Deregister successfully.');}
    else{ console.log('Failed to deregister!');}
    setTimeout("document.location.href=window.location.origin", 1000 )

}

function dereg(device_id) {
    var decision = confirm("Warning : Delete this Controller.\nAre you sure?");
    if (decision){ 
        console.log('Deregister this reomte control and close the page now.');
	csmapi.deregister(device_id, close_page);
    }
    else{
        console.log('Won\'t deregister.');
    }
}

//Switch
$(function () {
    $(document).on('click', '.toggle', function() {
	var self_id = $(this)[0].childNodes[0].id;
	var clicked = $(this).hasClass('btn-primary');
        csmapi.push(device_id, password, self_id, [clicked ? 1 : 0]);
    });
});


// toggle
$(document).ready(function(){
  $(".off-button").addClass("active");
  $(".tri-state-toggle-button").click(function() {
    $(this).siblings(":button").removeClass("active");
    $(this).addClass("active");
  });
});

function update_toggle_state(data, exception, df_name){
    if (data.length != 0){
        $(".tri-"+df_name).removeClass("active");
        switch(data[0][1][0]){
            case 0:
                $('#'+df_name+'-button1').addClass("active");
                break;
            case 1:
                $('#'+df_name+'-button0').addClass("active");
                break;
            case 2:
                $('#'+df_name+'-button2').addClass("active");
                break;
            default:
                $('#'+df_name+'-button0').addClass("active");
        }
    }	    
}


// Knob
$(function () {
    // Init vars
    var knobs = $('.knob-container');
    var knobVal = [];
    knobVal.length = knobs.length;

    // Init knob appearance
    knobs.knobKnob({
        startDeg: -45,
        degRange: 270,
        initVal: 0.0,
        numColorbar: 31,
    });

    // Check knob val updated or not
    function knobChecker() {
        // Check update
        for(var i=0; i<knobs.length; ++i)
            if( knobVal[i] !== $(knobs[i]).val() ) {
                knobVal[i] = $(knobs[i]).val().toString();
                csmapi.push($(knobs[i]).attr('deviceId'), password, $(knobs[i]).attr('dfName'), [parseFloat(knobVal[i])]);
            }
    }
    setInterval(knobChecker, 250);
});

// Slider
$(function() {
    var feature_list = ['Slider1',
                        'Slider2',
                        'Slider3',
                        'Slider4',
                        'Slider5',
                        'Slider6',
                        'Slider7',
                        'Slider8',
                        'Slider9',];

    for(var index in feature_list) {
        var feature = feature_list[index];
        var name = "#" + feature + "-slider";
        $(document).on('input', name, function() {
            var data = $(this).val();
            var feature_name = $(this).attr('id').split('-')[0];
            var feature_val = "#" + feature_name + "_val";
            $(feature_val).text(data);
            //IoTtalk.update(mac, feature_name+"-I", Number(data));
            csmapi.push(device_id, password, feature_name, [parseFloat(data)]);
            console.log(feature_name, data);
        });
    }
});

function update_slider_state(data, exception, df_name){
    if (data.length != 0){
        var name = df_name + "-slider";
        var value = data[0][1][0];
        var feature_name = df_name;
        var feature_val = "#" + feature_name + "_val";
        $(feature_val).text(value);
        document.getElementById(name).value = value;
        console.log('Load:', feature_name, value);
    }
}


$(function () {
    console.log('SwitchSet JS has been successfully loaded.');
    
});
