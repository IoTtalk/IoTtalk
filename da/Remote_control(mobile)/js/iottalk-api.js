var passwd = null;
(function() {

function register(mac, profile, callback) {
    var ret = null;
    $.ajax({
        type: 'POST',
        url: '/' + mac,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'profile': profile}),
        success: function(res) {
            //console.log(res);
            console.log('register success');
            ret = res;
        },
        error: function(err, st) {
            console.log(err);
            console.log(st);
            console.log('register failed');
        },
        complete: function() {
            passwd = JSON.parse(ret).password;
            if( typeof callback === 'function' )
                callback(ret);
        },
        dataType: 'text',
    });
}


function detach(mac, callback) {
	$.ajax({
        type: "DELETE",
        url: '/' + mac,
        success: function(res) {
            console.log(res);
            console.log('Detach success');
        },
        error: function(err, st) {
            console.log(err);
            console.log(st);
            console.log('Detach failed');
        },
        complete: function() {
            if( typeof callback === 'function' )
                callback();
        },
        dataType: 'text',
    });
}


function update(mac, feature, data, callback) {
    $.ajax({
        type: "PUT",
        url: '/' + mac + '/' + feature,
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({'data': [data]}),
	headers: {'password-key': passwd},
        error: function(err, st) {
            console.log(err);
            console.log(st);
            console.log('Update failed');
        },
        complete: function() {
            if( typeof callback === 'function' )
                callback();
        },
        dataType: 'text',
    });
}


function get(mac, feature, callback) {
    var ret = 0;
    $.ajax({
        type: "GET",
        cache: false,
        url: '/' + mac + '/' + feature,
	headers: {'password-key': passwd},
        success: function(res) {
            ret = JSON.parse(res);
            if( typeof ret !== 'object' || 
                    !ret['samples'] ||
                    !ret['samples'][0] ||
                    !ret['samples'][0][1] )
                ret = [];
            else
                ret = ret['samples'][0][1];
        },
        error: function(err, st) {
            console.log(err);
            console.log(st);
            console.log('Get failed');
        },
        complete: function() {
            if( typeof callback === 'function' )
                callback(ret);
        },
        dataType: 'text',
    });   
}




// Export to browser's global for debug
window.IoTtalk = {
    register: register,
    detach: detach,
    update: update,
    get: get,
};


})();
