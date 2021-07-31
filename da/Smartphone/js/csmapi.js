var csmapi = (function () {
    var ENDPOINT = null;

    function set_endpoint (endpoint) {
        ENDPOINT = endpoint;
    }

    function get_endpoint () {
        return ENDPOINT;
    }

    function register (mac_addr, profile, callback) {
        $.ajax({
            type: 'POST',
            url: ENDPOINT +'/'+ mac_addr,
            data: JSON.stringify({'profile': profile}),
            contentType:"application/json; charset=utf-8",
        }).done(function (result) {
            if (callback) {
                callback(true, result.d_name, result.password);
            }
        }).fail(function () {
            if (callback) {
                callback(false);
            }
        });
    }

    function deregister (mac_addr, callback) {
        $.ajax({
            type: 'DELETE',
            url: ENDPOINT +'/'+ mac_addr,
            contentType:"application/json; charset=utf-8",
        }).done(function () {
            if (callback) {
                callback(true);
            }
        }).fail(function () {
            if (callback) {
                callback(false);
            }
        });
    }

    function pull (mac_addr, password, odf_name, callback) {
        $.ajax({
            type: 'GET',
            url: ENDPOINT +'/'+ mac_addr +'/'+ odf_name,
            contentType:"application/json; charset=utf-8",
            headers: {'password-key': password},
        }).done(function (obj) {
            if (typeof obj === 'string') {
                obj = JSON.parse(obj);
            }

            if (callback) {
                callback(obj['samples']);
            }
        }).fail(function (error) {
            if (callback) {
                callback([], error);
            }
        });
    }

    function push (mac_addr, password, idf_name, data, callback) {
        $.ajax({
            type: 'PUT',
            url: ENDPOINT +'/'+ mac_addr +'/'+ idf_name,
            data: JSON.stringify({'data': data}),
            contentType:"application/json; charset=utf-8",
            headers: {'password-key': password},
        }).done(function () {
            if (callback) {
                callback(true);
            }
        }).fail(function () {
            if (callback) {
                callback(false);
            }
        });
    }

    return {
        'set_endpoint': set_endpoint,
        'get_endpoint': get_endpoint,
        'register': register,
        'deregister': deregister,
        'pull': pull,
        'push': push,
    };
})();
