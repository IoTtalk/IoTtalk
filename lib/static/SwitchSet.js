let device_id = null;
var _ENDPOINT =  window.location.origin; 
var password = null;
var numberOfSwitches = 0;
var profile = {
    'dm_name': 'Remote_control',
    'df_list':[],
    'd_name': '',
};    

function set_device_id(d_id, count){
    device_id = d_id;
    numberOfSwitches = count;
    profile['d_name'] = d_id;
    for (var index=1; index<=count; index++) profile['df_list'].push('Switch'+String(index));
    csmapi.set_endpoint(_ENDPOINT);   
}

function regisration_state(state, d_name, passwd){
    if (state){ 
        console.log('Register successfully.');
        password = passwd;
        load_alias_and_switchState(device_id, numberOfSwitches);	    
    }
    else console.log('Register failed.');
}

function state_check(data, exception=null){
    if (exception){
        if (String(exception.responseText).indexOf('mac_addr not found') != -1){
            console.log('Device is not existed. Try to register.');
            console.log('device_id =', device_id);
            csmapi.register(device_id, profile, regisration_state);
        }
        else if(String(exception.responseText).indexOf('password-key error') != -1){
	    console.log('Password is expired. Re-register.');
            console.log('Because device_auth is enabled, the Switch state cannot be loaded.');
	    csmapi.register(device_id, profile, regisration_state);
        }
        else{
            console.log('Error occurred!');
            console.log('Response:', exception.responseText);
            console.log('Status:', exception.statusText);
            console.log('Endpoint =', _ENDPOINT);
        }
    }
    else{
        console.log('Device is existed. Continue.');
        if (profile['df_list'].length > data['df_list'].length){
            console.log('Required number of Switches larger than that in the server. Re-register.');
            csmapi.register(device_id, profile, regisration_state);
        }
	else load_alias_and_switchState(device_id, numberOfSwitches);
           
    }
}

function check_registerion_state(mac_addr){
    csmapi.pull(mac_addr, password, 'profile', state_check);
}

$(function () {
    $(document).on('click', '.toggle', function() {
	var self_id = $(this)[0].childNodes[0].id;
	console.log (self_id);
	var clicked = $(this).hasClass('btn-primary');
        csmapi.push(device_id, password, self_id, [clicked ? 1 : 0]);
    });
});

function get_alias(mac_addr, df_name, callback){
    var alias;
    var ajax_obj = $.ajax({
        url: '/get_alias/' + mac_addr+ '/' + df_name,
        type: 'GET',
        data: {alias},
    }).done(function(alias){
        if(typeof callback === 'function') callback(df_name, alias['alias_name'][0]);
    });
}

function update_alias(df_name, alias){
    if (alias!=undefined) $('.'+df_name)[0].innerText = alias;
}

function load_alias_and_switchState(mac_addr, count){
    for(var index=1; index<=count; index++){
	    get_alias(mac_addr, 'Switch'+index.toString(), update_alias);
	    csmapi.pull(mac_addr, password, 'Switch'+String(index), update_switch_state);
    }
}

function update_switch_state(data, exception, df_name){
    if (data.length != 0)
        if (data[0][1][0] == 1) $('#'+df_name).bootstrapToggle('on');
}

function close_page(){
    document.location.href=window.location.origin;
}

function dereg(mac_addr) {
    var decision = confirm("警告: Delete this Controller.\nAre you sure?");
    if (decision){ 
        console.log('Deregister this reomte control and close the page now.');
	csmapi.deregister(mac_addr, close_page);
    }
    else{
        console.log('Won\'t deregister.');
    }
}

$(function () {
    console.log('SwitchSet JS has been successfully loaded.');
});
