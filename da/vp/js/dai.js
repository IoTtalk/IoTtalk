var id = 'VPython';
var project = window.location.hash.replace(/^#/,'');

const dai = function (profile) {
    csmapi.set_endpoint (window.location.origin);

    var odf_func = {};
    var idf_func = {};
	
    var mac_addr = (function () {
        function s () {
            return Math.floor((1 + Math.random()) * 0x10000)
                .toString(16)
                .substring(1);
        }
        return s() + s() + s();
    })();

    if (profile.idf_list == undefined) profile.idf_list = [];
    if (profile.odf_list == undefined) profile.odf_list = [];

    profile['df_list']=[];
    for (var i = 0; i < profile.odf_list.length; i++) {
        odf_name = profile.odf_list[i].name;
        if(odf_name[odf_name.length-2] == '_'){
            odf_name = odf_name.substr(0, odf_name.length-2) + '-' + odf_name.substr(odf_name.length-1);
        }
        odf_func[odf_name] = profile.odf_list[i];
		profile.odf_list[i] = odf_name;
		profile['df_list'].push(odf_name);
        console.log(odf_name);
    }
	
    for (var i = 0; i < profile.idf_list.length; i++) {
        idf_name = profile.idf_list[i].name;
        if(idf_name[idf_name.length-2] == '_'){
            idf_name = idf_name.substr(0, idf_name.length-2) + '-' + idf_name.substr(idf_name.length-1);
        }
        idf_func[idf_name] = profile.idf_list[i];
		profile.idf_list[i] = idf_name;
		profile['df_list'].push(idf_name);
        console.log(idf_name);
    }	
	
    function push(idf_name) {
	    data = idf_func[idf_name]();
            dan.push(idf_name, data);
	}
	
    function pull(odf_name, data) {
        if (odf_name == 'Control') {
            if (data[0] == 'SET_DF_STATUS'){
                dan.push('Control', ['SET_DF_STATUS_RSP', data[1]], function (res) {});
            }
        } else {
            odf_func[odf_name](data);
        }
    }

    function init_callback (result) {
        console.log('register:', result);
        document.title = profile.d_name;
    }

    function deregisterCallback (result) {
        console.log('deregister:', result);
    }

    function deregister () {
        dan.deregister(deregisterCallback);
    }

    window.onunload = deregister;
    window.onbeforeunload = deregister;
    window.onclose = deregister;
    window.onpagehide = deregister;

    dan.init(push, pull, csmapi.get_endpoint(), mac_addr, profile, init_callback);
};



/*==Basic==*/
var audio = {}

const preloadAudio = function(filename) {
  if (audio[filename] == undefined) {
    audio[filename] = new Audio('/da/vp/audio/' + filename);
  }
};

const playAudio = function(filename) {
  preloadAudio(filename);
  if (audio[filename] != undefined) {
    audio[filename].play();
  }
};

const execute = function (code) {
  const options = {
    lang: 'vpython',
    version: 2.1
  };

  const js_code = glowscript_compile(code, options);
  const program = eval(js_code);

  //console.log(js_code);
  program(function(err){
    if (err) console.log(err);
  });
};

const fetch_code = function(url){
  $.get(url)
   .done(function (data) {
     execute(data);
   })
   .fail(function (jqxhr, settings, execption) {
     console.log(execption);
  });
};

window.__context = {
  glowscript_container: $('#glowscript'),
};

var originHash;
$(function () {
  originHash = window.location.hash;
  fetch_code('/da/vp/py/'+ project + '.py');
});

$(window).on('hashchange', function (a) {
  if (window.location.hash != originHash) {
    window.location.hash = originHash;
  }
});

