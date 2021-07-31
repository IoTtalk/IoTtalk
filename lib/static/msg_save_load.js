function save_info(callback){
    var name=[];
    $('.name').each(function(){ name.push($(this)[0].value); });

    var message=[];
    $('.message').each(function(){ message.push($(this)[0].value); });

    var msg_info = {'name':name, 'message':message };
    
    msg_info = JSON.stringify(msg_info);

    $.ajax({
        url: '/save_msg_info',
        type:'POST',
        contentType: 'application/json',
        data: msg_info,
    }).done(function (msg) {
        console.log('Save successfully: '+ msg);
        $('#message').text('Successed: '+ msg);
    }).fail(function (msg) {
        console.log('failed: '+ msg.status +','+ msg.responseText);
        $('#message').text('failed: '+ msg.status +','+ msg.responseText);
    }).always(function() {
        if(typeof callback === 'function')
            callback();
    });
}

var number_of_name=0;
function load_info(count){
    var ajax_obj = $.ajax({
        url: '/load_msg_info',
        type: 'POST',
    }).done(function(){
        if (count) number_of_name=count;

        var obj= $.parseJSON(ajax_obj.responseText);
	    
        if (JSON.stringify(obj) != "{}"){
  
            $.each(obj.name, function(index, content){
                if (index+1 > number_of_name) return false;
                $('.name')[index].value = content;
            });

            $.each(obj.message, function(index, content){
                if (index+1 > number_of_name) return false;
                $('.message')[index].value = content;
	    	    
            });
        }
        console.log('Load successfully.');
    }).fail(function (msg){
        console.log('Load failed: '+ msg.status +','+ msg.responseText);
        $('#message').text('failed: '+ msg.status +','+ msg.responseText);
    });

    load_aliases(count);
}

function load_aliases(count){
    var aliases = [];
    for (var index=1; index<=count; index++) aliases.push('Name' + String(index));

    var alias;
    $.each(aliases, function(index, content){
        var ajax_obj = $.ajax({
            url: '/get_alias/IoTtalk_Message/' + content,
            type: 'GET',
            data: {alias}
        }).done(function(alias){
            $('.alias')[index].innerText =  alias['alias_name'][0];
        });
    });
}

function clear_info(){
    for (var index=0; index < number_of_name; index++) $('.name')[index].value = '';
    for (var index=0; index < number_of_name; index++) $('.message')[index].value = '';
    save_info();
}

function clear_row(index){
    $('.name')[index].value = '';
    $('.message')[index].value = '';
    save_info();
}



