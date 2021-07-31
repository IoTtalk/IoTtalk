var dan = (function () {
    var RETRY_COUNT = 3;
    var RETRY_INTERVAL = 2000;
    var POLLING_INTERVAL = 500;
    var _pull;
    var _push;
    var _mac_addr = '';
    var _profile = {};
    var _registered = false;
    var _idf_list;
    var _odf_list;
    var _df_list;
    var _df_selected = {};
    var _odf_timestamp = {};
    var _suspended = false;
    var _ctl_timestamp = '';
    var _password = '';	

    function init (push, pull, endpoint, mac_addr, profile, callback) {
        _pull = pull;
	_push = push;
        _mac_addr = mac_addr;

        function init_callback (result) {
            if (result) {
                callback(csmapi.get_endpoint());
            } else {
                callback('register failed');
            }
        }
        register(endpoint, profile, init_callback);
    }

    function register (endpoint, profile, callback) {
        //profile['d_name'] = (Math.floor(Math.random() * 99)).toString() + '.' + profile['dm_name'];
        _profile = profile;
        csmapi.set_endpoint(endpoint);

        var retry_count = 0;
        function register_callback (result, d_name, password = '') {
            if (result) {
                if (!_registered) {
                    _registered = true;
                    _password = password;
		    profile.d_name = d_name;
		    _idf_list = profile['idf_list'].slice();
		    _odf_list = profile['odf_list'].slice();
		    _df_list = profile['df_list'].slice();
                    			

                    for (var i = 0; i < _df_list.length; i++) {
                        _df_selected[_df_list[i]] = false;
					}
                    for (var i = 0; i < _odf_list.length; i++) {
                        _odf_timestamp[_odf_list[i]] = '';
                    }
                    _ctl_timestamp = '';
                    _suspended = false;					
                    setTimeout(pull_ctl, 0);
                }
                callback(true);
            } else {
                if (retry_count < 2) {
                    retry_count += 1;
                    setTimeout(function () {
                        csmapi.register(_mac_addr, profile, register_callback);
                    }, RETRY_INTERVAL);
                } else {
                    callback(false);
                }
            }
        }
        csmapi.register(_mac_addr, profile, register_callback);
    }

    function pull_ctl () {
        if (!_registered) {
            return;
        }

        function pull_ctl_callback (dataset, error) {
            if (has_new_data(dataset, _ctl_timestamp)) {
                _ctl_timestamp = dataset[0][0];
                if (handle_command_message(dataset[0][1])) {
                    _pull('Control', dataset[0][1]);
                } else {
                    console.log('Problematic command message:', dataset[0][1]);
                    }
            }

            pull_odf(0);
        }

        csmapi.pull(_mac_addr, _password,'__Ctl_O__', pull_ctl_callback);
    }

    function pull_odf (index) {
		if (!_registered) {
            return;
        }

        if (_suspended || index >= _odf_list.length) {
            setTimeout(push_idf, POLLING_INTERVAL, 0);
            return;
        }

        var _odf_name = _odf_list[index];

        if (!_df_selected[_odf_name]) {
            pull_odf(index + 1);
            return;
        }

        function pull_odf_callback (dataset, error) {
            if (has_new_data(dataset, _odf_timestamp[_odf_list[index]])) {
                _odf_timestamp[_odf_list[index]] = dataset[0][0];
                _pull(_odf_list[index], dataset[0][1]);
            }

            setTimeout(pull_odf, POLLING_INTERVAL, index + 1);
			
        }
        csmapi.pull(_mac_addr, _password,_odf_name, pull_odf_callback);
    }

    function push_idf (index) {
	if (!_registered) {
            return;
        }

        if (_suspended || index >= _idf_list.length) {
            setTimeout(pull_ctl, POLLING_INTERVAL);
            return;
        }
	    
        var _idf_name = _idf_list[index];
        if (!_df_selected[_idf_name]) {
            push_idf(index + 1);
            return;
        }
	    
        _push(_idf_list[index]);
        setTimeout(push_idf, POLLING_INTERVAL, index + 1);
    }	
	
    function handle_command_message (data) {
        switch (data[0]) {
        case 'RESUME':
            _suspended = false;
            break;
        case 'SUSPEND':
            _suspended = true;
            break;
        case 'SET_DF_STATUS':
            flags = data[1]['cmd_params'][0]
            if (flags.length != _df_list.length) {
                console.log(flags, _df_list);
                return false;
            }

            for (var i = 0; i < _df_list.length; i++) {
                _df_selected[_df_list[i]] = (flags[i] == '1');
            }
            break;
        default:
            console.log('Unknown command:', data);
            return false;
        }
        return true;
    }

    function has_new_data (dataset, timestamp) {
        if (dataset.length == 0 || timestamp == dataset[0][0]) {
            return false;
        }
        return true;
    }

    function push(idf_name, data, callback) {
        if(!Array.isArray(data))
            data = [data];

        if (idf_name == 'Control') {
            idf_name = '__Ctl_I__';
        }

        if (idf_name == '__Ctl_I__' || _df_selected[idf_name]) {
            csmapi.push(_mac_addr, _password, idf_name, data, callback);
        }
    }

    function deregister (callback) {
        _registered = false;
        csmapi.deregister(_mac_addr, callback);
    }

    return {
        'init': init,
        'register': register,
        'push': push,
        'deregister': deregister,
    };
})();
