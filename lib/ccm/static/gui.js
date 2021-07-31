var Disable_IDF_default_value_editor = false;
var Disable_ODF_default_value_editor = false;
var plural_DF_list;
var special_model_list;
let illegal_function_names = ['x1', 'x2', 'x3','x4','x5',];

function gui_init() {

    $.ajaxSetup({
        async: false,
        cache: false,
        dataType: 'html',
        error: function(jqXHR, error, responseText) {
            console.log(error)
            alert ("[ "+ this.url +" ] Can't do because: " + responseText );
        },
    });
    bind_pwd_check_model();
    add_new_project();
    menu_component_show(false);
	plural_DF_list = ajax_get_plural_df_list();
	special_model_list = ajax_get_create_model_without_select_feature_list();
    /*************************************************************************/
    /*
    p_id:-1, add a new project
    p_id:-2, select a project
    */
    if(p_id == -1) {
          $('#alertMessage').text('Please add a project.');
           //bind add project btn with newPorjectModal
           $('#project_pull_down_menu').on('click',function() {
                $('#newPorjectModal').modal('show');
           });
           return
    }
    else if(p_id == -2){
        update_project_list_handler();
        $('#alertMessage').text('Please select a project.');
        return
    }
    /*************************************************************************/
}

var chart = [];
var updatedata = [];

function update_monitor_data(div, data, symbol, data_length, subscript, chartN) {
    var null_flag = 0;
    for (var value of data[0]) {
        if (value === null) {
            null_flag = 1;
        }
    }
    if (null_flag == 0) {
        var num_of_axis = data[0].length - 1;
        var div_width = div.width() - 20;
        var timestamp_width = 120;
        var axis_width = (div_width - timestamp_width) / num_of_axis - 1;
        var table_width = timestamp_width + axis_width * num_of_axis;

        if (div.children('.table-header').find('td').length != data_length || stage_changed == symbol) {
            div.empty();
            stage_changed = "";
        }
        
        if (div.children('.table-header').length == 0) {
            //generate chart
            var arrays = [['x']];
            for(var i = 1; i < data[0].length; i++){
                if(symbol == 'z')
                    label = symbol + subscript;
                else
                    label = symbol + i + subscript;
                arrays.push([label]);
            }
            chart[chartN] = c3.generate({
                bindto: '#chart' + chartN,
                size: {
                    height: 190
                },
                data: {
                    x: 'x',
                    xFormat: '%H:%M:%S',
                    columns: arrays
                },
                legend: {
                    position: 'right',
                    item: {
                        onclick: function (id) {}
                    }
                },
                axis: {
                    x: {
                        type: 'timeseries',
                        tick: {
                            rotate: 75,
                            format: '%H:%M:%S'
                        }
                    }

                }
            });
            updatedata[chartN] = [];

            // generate header
            var table_header = $('<table>', {
                'class': 'table table-bordered table-condensed table-header',
                'style': 'float: left; position: absolute; background: #E9E9E9; margin-bottom:0px; margin-top:0px; width: ' + table_width,
            });
            var tr = $('<tr>');
            var td = $('<td>', {'style': 'width: '+timestamp_width}).text('Timestamp');
            td.appendTo(tr);
            for (i=1; i<data[0].length; i++) {
                if (symbol == 'z') {
                    var td = $('<td>', {'style': 'width: '+axis_width});
                    $('<div>', {
                        'style': 'overflow: hidden; height: 1.4em',
                    }).append("<p>"+symbol + "<sub>F</sub></p>").appendTo(td);
                    td.appendTo(tr);
                }
                else{
                    var td = $('<td>', {'style': 'width: '+axis_width});
                    $('<div>', {
                        'style': 'overflow: hidden; height: 1.4em',
                    }).append("<p>"+symbol+"<sub>"+i+subscript+"</sub></p>").appendTo(td);
                    td.appendTo(tr);
                }

            }
            tr.appendTo(table_header);
            table_header.appendTo(div);
			
			// insert one row
            {
                var tbl_div = $('<div>', {
                    'class': 'monitor_data_inner_div',
                });
                tbl_div.appendTo(div);
                var tbl = $('<table>', {
                    'class': 'table table-bordered table-condensed table-hover',
                    'style': 'min-height: 30px; margin: 0; width: ' + table_width,
                });

                var tr = $('<tr>');
                var td = $('<td>', {'style': 'width: '+timestamp_width}).text('00:00:00');     //timestamp
                td.appendTo(tr);
                for (j=1; j<data[0].length; j++) {
                    var td = $('<td>', {'style': 'width: '+axis_width});
                    $('<div>', {
                        'style': 'overflow: hidden; height: 1.4em',
                    }).text(data[0][j]).appendTo(td);
                    td.appendTo(tr);
                }
                tr.appendTo(tbl);
                tbl.appendTo(tbl_div);
            }
        }
        var last_time = div.children('.monitor_data_inner_div').last().find('td').first().text();
        if (last_time != data[0][0]) {
            // insert data
            var tbl_div = $('<div>', {
                'class': 'monitor_data_inner_div',
            });
            tbl_div.appendTo(div);
            var tbl = $('<table>', {
                'class': 'table table-bordered table-condensed table-hover',
                'style': 'min-height: 30px; margin: 0; width: ' + table_width,
            });

            for (i=0; i<data.length; i++) {
                var tr = $('<tr>');

                // timestamp.
                var td = $('<td>', {'style': 'width: '+timestamp_width}).text(data[i][0]);     //timestamp
                td.appendTo(tr);

                if(div.children('.monitor_data_inner_div').length > 0) { //first row is old data, don;t show
                    if(updatedata[chartN].length == 0)
                        updatedata[chartN].push(['x', data[i][0]]);
                    else {
                        updatedata[chartN][0].push(data[i][0]);
                        if(updatedata[chartN][0].length > 16)
                            updatedata[chartN][0].splice(1, 1);
                    }
                }

                // other axis.
                for (j=1; j<data[i].length; j++) {
                    if(symbol == 'z')
                        label = symbol + subscript;
                    else
                        label = symbol + j + subscript;
                    if(div.children('.monitor_data_inner_div').length > 0) { //first row is old data, don;t show
                        if(updatedata[chartN][0].length == 2)
                            updatedata[chartN].push([label, data[i][j]]);
                        else {
                            updatedata[chartN][j].push(data[i][j]);
                            if(updatedata[chartN][j].length > 16)
                                updatedata[chartN][j].splice(1, 1);
                        }
                    }

                    var td = $('<td>', {'style': 'width: '+axis_width});
                    $('<div>', {
                        'style': 'overflow: hidden; height: 1.4em',
                    }).text(data[i][j]).appendTo(td);
                    td.appendTo(tr);
                }
                
                tr.appendTo(tbl);
            }
            tbl.appendTo(tbl_div);
        }

        if(isTabHidden == false && updatedata[chartN].length != 0)  {
            var length = 0;
            if(chart[chartN].x()[label])
                length = Math.max(0, chart[chartN].data.shown()[0].values.length + updatedata[chartN][0].length - 1 - 15);
            
            chart[chartN].flow({
                columns: updatedata[chartN],
                duration: 150,
                length: length
            });

            updatedata[chartN].length = 0;
        }

        if (i == 0) {
            div.text('No data received now.');
        }
        var scroll_height = div.get(0).scrollHeight;
        div.parents('.div-intro-block').scrollTop(scroll_height);
    }
}

function stop_and_continue_event_handler() {
    $('.stop_continue_button').unbind('click');
    $('.stop_continue_button').on('click', function(e) {
        var dfo_id = $(this).parent().find('select.input-df-select option:selected').attr('name');

        if ($(this).text() == 'Step') {
            $(this).text('Continue');
            $('button#step-button').attr('disabled','disabled');
            $('button#step-button').css('color','rgb(187, 177, 177)');
            $('button#specific-send-button').attr('disabled','disabled');
            $('button#specific-send-button').css('color','rgb(187, 177, 177)');
            pull_monitored_data(1000,'Continue');

        } else if ($(this).text() == 'Continue') {
            $(this).text('Step');
            $('button#step-button').removeAttr('disabled');
            $('button#step-button').removeAttr('style');
            $('button#specific-send-button').removeAttr('disabled');
            $('button#specific-send-button').removeAttr('style');
        }
    });
}

function step_event_handler() {
    $('.input-step-button').unbind('click');
    $('.input-step-button').on('click', function(e) {
        var dfo_id = $(this).parent().find('select.input-df-select option:selected').attr('name');
        sleep(0.5);
        pull_monitored_data(1000, 'Step');
    });
}

function send_event_handler() {
    $('.input-send-button').unbind('click');
    $('.input-send-button').on('click', function(e) {
        var dfo_id = $(this).parent().parent().find('select.input-df-select option:selected').attr('name');
        var data = $('.push-data-input').val();

        ajax_push_user_input_data(dfo_id, data);

        sleep(0.5);
        pull_monitored_data(1000, 'Step');
    });
}

function table_or_chart_event_handler(id, father) {
    $(id).unbind('click');
    $(id).on('click', function(e) {
        if($(this).text() == 'Chart') {
            $(this).text('Table');
            $("father svg").hide();
            $("father table").show();
        }
        else {
            $(this).text('Chart');
            $("father table").hide();
            $("father svg").show();
        }
    });
}

function pull_monitored_data(delay, exec_mode) {
    var na_id =  $('.div-idf-monitor-outer').find('label').attr('name');
    var idfo_id =  $('.div-idf-monitor-outer').find('select.input-df-select option:selected').attr('name');
    var in_stage =    $('.div-idf-monitor-outer select.step-select option:selected').text();
    var odfo_id = $('.div-odf-monitor-outer').find('select.output-df-select option:selected').attr('name');
    var out_stage =   $('.div-odf-monitor-outer select.step-select option:selected').text();
    var execution_mode = $('.input-step-button').attr('disabled');
    var is_multiple_join = $('.div-idf-monitor-outer select.step-select option').eq(3).text() == 'Normalization';
    if (execution_mode == undefined ) execution_mode = 'Step';
    else {
        execution_mode = 'Continue';
    }
    if (exec_mode == 'Step' ) execution_mode = 'Continue';

    var data_path_info = {'na_id': Number(na_id), 'idfo_id': Number(idfo_id), 'i_substage': in_stage,
                          'o_substage': out_stage, 'odfo_id': Number(odfo_id),
                          'execution_mode': execution_mode, 'is_multiple_join': is_multiple_join};
    data_path_info = JSON.stringify(data_path_info);

    $.ajax({ 
        url: '/pull_monitored_data', //TODO
        timeout: delay,
        type:'POST',
        data: {data_path_info:data_path_info},
        error: function(request,error) {
            monitor_timer = setTimeout(function() {
                if ($('.div-idf-monitor-outer').length != 0 ||  $('.div-odf-monitor-outer').length != 0) {
                    pull_monitored_data(delay, 'Continue');
                }
            }, delay);

        },
        success: function(data) {
            var data_info = $.parseJSON(data);
            var i_subscript = "";
            if (in_stage == "Input" ) i_subscript = "";
            else i_subscript = ','+in_stage[0];
            var o_subscript = "";
            if (in_stage == "Scaling" ) o_subscript = "";
            else o_subscript = ','+out_stage[0];
            if ($('.div-idf-monitor-outer').find('.monitor_data_div').length > 0) {
                var div = $('.div-idf-monitor-outer').find('.monitor_data_div');
                div.attr('id', 'chart0');
                if (data_info['in'].length != 0){
                    update_monitor_data(div, data_info['in'], 'x', data_info['in'][0].length, i_subscript, 0);
                    if($(idf_tableorchart).text() == 'Chart'){
                        $(".div-idf-monitor-outer table").hide();
                        $(".div-idf-monitor-outer svg").show();
                    }
                    else{
                        $(".div-idf-monitor-outer svg").hide();
                        $(".div-idf-monitor-outer table").show();
                    }
                }
            }

            if (!$('.div-join-monitor-outer').hasClass('join-mointor-hidden')) {
                var div = $('.div-join-monitor-outer').find('.monitor_data_div');
                div.attr('id', 'chart1');
                if (data_info['join'].length != 0){
                    update_monitor_data(div, data_info['join'], 'z', data_info['join'][0].length, 'F', 1);
                    if($(join_tableorchart).text() == 'Chart'){
                        $(".div-join-monitor-outer table").hide();
                        $(".div-join-monitor-outer svg").show();
                    }
                    else{
                        $(".div-join-monitor-outer svg").hide();
                        $(".div-join-monitor-outer table").show();
                    }
                }
            }

            if ($('.div-odf-monitor-outer').find('.monitor_data_div').length > 0) {
                var div = $('.div-odf-monitor-outer').find('.monitor_data_div');
                div.attr('id', 'chart2');
                if (data_info['out'].length != 0){
                    update_monitor_data(div, data_info['out'], 'y', data_info['out'][0].length, o_subscript, 2);
                    if($(odf_tableorchart).text() == 'Chart'){
                        $(".div-odf-monitor-outer table").hide();
                        $(".div-odf-monitor-outer svg").show();
                    }
                    else{
                        $(".div-odf-monitor-outer svg").hide();
                        $(".div-odf-monitor-outer table").show();
                    }
                }
            }
            if (execution_mode == 'Continue')
                monitor_timer = setTimeout(function() {
                    if ($('.div-idf-monitor-outer').length != 0 ||  $('.div-odf-monitor-outer').length != 0) {
                        pull_monitored_data(delay, 'Continue');
                    }
                }, delay);
            else
                clearTimeout(monitor_timer);
        }
    });
};

function feature_change_event_handler(df_type, is_multiple_join) {
    $('.'+df_type+'-df-select').change(function() {
        var dfo_id = $(this).find('option:selected').attr('name');
        if (df_type == 'input') {
            step_event_handler();
            stop_and_continue_event_handler();

            $(this).siblings().filter('button.stop_continue_button').text('Continue');
            $('button#step-button').attr('disabled','disabled');
            $('button#step-button').css('color','rgb(187, 177, 177)');
            $('button#specific-send-button').attr('disabled','disabled');
            $('button#specific-send-button').css('color','rgb(187, 177, 177)');
        }

        //update stage list
        $(this).parents('.div-add-function-outer').find('.monitor_data_div').empty()
        var na_id =  $('.div-idf-monitor-outer').find('label').attr('name');
        var odfo_id = $('.div-odf-monitor-outer').find('select.output-df-select option:selected').attr('name');
        var stage_info = ajax_get_substage_list(na_id, odfo_id, is_multiple_join);
        update_substage_list(stage_info);
    });
}

function sleep(sec) {
    var time = new Date().getTime();
    while (new Date().getTime() - time < sec * 1000);
}

function remove_all_data() {
    $('#out_device_column').children().each(function(index ) {
        $(this).remove();
    });

    $('#in_device_column').children().each(function(index ) {
        $(this).remove();
    });

    $('.map-block').each(function(index ) {
        $(this).removeAttr('name');
    });

    $('.map-column').find('.connected').each(function(index ) {
        $(this).find('.join-input').addClass('hidden-flag');
        $(this).find('img').addClass('hidden-flag');
        $(this).removeClass('connected');
    });
    $('.feature-circle-clicked').removeClass('feature-circle-clicked');

    $('#management_window').empty();
}
function sort_device_featrue(reload_info){
    var in_device_length = reload_info["in_device"].length;
    var out_device_length = reload_info["out_device"].length;
    var group = [];
    var pre = null;
    var regex = /(\d+)/g;
    var match;
    var index = -1;
    var odf_sort_data = [];
    var idf_sort_data = [];
    function group_sort(group){
        group.sort(function(a,b){
            var na = -1;
            var nb = -1;
            while((match = regex.exec(a[0])) != null){
                na = match.index;
            }
            while((match = regex.exec(b[0])) != null){
                nb = match.index;
            }    
            return Number(a[0].substring(na, a[0].length)) - 
                Number(b[0].substring(nb, b[0].length));
        });
    }
    for(var i = 0; i < out_device_length; i++){
        p_odf_list_length = reload_info["out_device"][i]["p_odf_list"].length;
        for(var j = 0; j < p_odf_list_length; j++){
            s = reload_info["out_device"][i]["p_odf_list"][j][0],
            obj = reload_info["out_device"][i]["p_odf_list"][j];
            while((match = regex.exec(s)) != null)
                index = match.index;
            if(index == -1 || (pre!= null && pre != s.substring(0, index))){
                group_sort(group);
                odf_sort_data.push(group.slice(0));
                group = [];
                group.push(obj);
                if(index == -1)
                    pre = s;
                else
                    pre = s.substring(0, index);
            }
            else{
                group.push(obj);
                pre = s.substring(0, index);
                //console.log(group);
            }
        }
        group_sort(group);
        odf_sort_data.push(group.slice(0));
        group = [];
        var odf_list = [];
        for(var k = 0; k < odf_sort_data.length; k++){
            odf_list = odf_list.concat(odf_sort_data[k]);
        }
        reload_info["out_device"][i]["p_odf_list"] = odf_list;
        odf_sort_data = [];
    }
    index = -1;
    pre = null;
    group = [];
    for(var i = 0; i < in_device_length; i++){
        p_idf_list_length = reload_info["in_device"][i]["p_idf_list"].length;
        for(var j = 0; j < p_idf_list_length; j++){
            s = reload_info["in_device"][i]["p_idf_list"][j][0],
            obj = reload_info["in_device"][i]["p_idf_list"][j];
            while((match = regex.exec(s)) != null)
                index = match.index;
            if(index == -1 || (pre!= null && pre != s.substring(0, index))){
                group_sort(group);
                idf_sort_data.push(group.slice(0));
                group = [];
                group.push(obj);
                if(index == -1)
                    pre = s;
                else
                    pre = s.substring(0, index);
            }
            else{
                group.push(obj);
                pre = s.substring(0, index);
            }
        }
        group_sort(group);
        idf_sort_data.push(group.slice(0));
        group = [];
        var idf_list = [];
        for(var k = 0; k < idf_sort_data.length; k++){
            idf_list = idf_list.concat(idf_sort_data[k]);
        }
        reload_info["in_device"][i]["p_idf_list"] = idf_list;
        idf_sort_data = [];
    }
    return reload_info;
}

function reload_all_data() {
    if (reload_info = ajax_reload_data(p_id)) {
        remove_all_data();
        reload_info = sort_device_featrue(reload_info);
        for (var i=0; i<reload_info['join'].length; i++) {
            var join_div = $('.map-block').get(reload_info['join'][i][2]);
            var join_input = $('.join-input').get(reload_info['join'][i][2]);
            $(join_div).attr('name', reload_info['join'][i][0]);
            $(join_div).addClass('connected');
            $(join_input).text(reload_info['join'][i][1]);
            $(join_input).removeClass('hidden-flag');
            $(join_div).find('img').removeClass('hidden-flag');
        }

        for (var i=0; i<reload_info['in_device'].length; i++) {
            var model_block = make_model_block_html(reload_info['in_device'][i], 'in');
            var in_device_column = $('#in_device_column');
            model_block.appendTo(in_device_column);
            $('#management_window').empty();
        }

        for (var i=0; i<reload_info['out_device'].length; i++) {
            var model_block = make_model_block_html(reload_info['out_device'][i], 'out');
            var out_device_column = $('#out_device_column');
            model_block.appendTo(out_device_column);
            $('#management_window').empty();
        }

        redraw_connect_line();

        click_right_event_handler();
        mount_device_event_handler();
        connect_feature_event_handler();
        connect_feature_circle_event_handler();
        click_right_circle_event_handler();
    }
    else {
        alert('reload data fail!', 'Error');
    }

}

function update_project_list_handler(){
    $('#project_pull_down_menu').on('mouseenter', function () {
        project_list = ajax_get_project_list();
        project_pull_down_menu = $('#project_pull_down_menu');
        project_pull_down_menu.children('ul').empty();
        $.each(project_list, function(index, project) {
            item = $('<li>');
            $('<a>', {'text':project[0]}).attr("name",project[1]).appendTo(item);
            item.attr("class","project-list");
            item.appendTo(project_pull_down_menu.children('ul'));
        });
        choose_project_event_handler();
    });
}

function update_model_event_handler() {
    $('#model_pull_down_menu').on('mouseenter', function () {
        model_list = ajax_get_model_list();

        model_pull_down_menu = $('#model_pull_down_menu');
        model_pull_down_menu.children('ul').empty();
        $.each(model_list, function(index, model ) {
            item = $('<li>');
            $('<a>', {'text':model[0]}).appendTo(item);
            item.attr("val",model[1]);
            item.appendTo(model_pull_down_menu.children('ul'));
        });

        $('#model_pull_down_menu li').unbind('click');
        $('#model_pull_down_menu li').on('click', handle_click_model_event);
    });
}

function delete_device_object_event_handler() {
    $('#delete_model').unbind('click');
    $('#delete_model').click(function() {
        var r = confirm("Are you sure to delete this device object?");
        if (r == true) {
            $('img.feature-circle-clicked').removeClass('feature-circle-clicked');
            var do_id = $('.div-wa-model-title > label').attr('name');
            ajax_delete_device_object(do_id, p_id)
            reload_all_data();
            ajax_restart_project();
        }
    });
}

function add_new_project() {
      var clearModal = function(){
            $("#projectNameAlert").text('');
            $("#projectPwdAlert").text('');
            $('#newPorjectModal').find('#project-name').val('');
            $('#newPorjectModal').find('#project-pwd').val('');   
      }
      var modalOKBtnHandler = function(){
            var projectName  = $('#newPorjectModal').find('#project-name')
            var projectPwd = $('#newPorjectModal').find('#project-pwd')
            var projectNameAlert = $("#projectNameAlert");
            var projectPwdAlert = $("#projectPwdAlert");
            var regDict = {
                "Length of prject name not between 1 to 255" : [ projectName, projectNameAlert, /.{1,255}/, false ],
                "Can not name project with \"add project\"": [ projectName, projectNameAlert, /^add project$/, true ],
                //"Length of prject password not between 4 to 32" : [ projectPwd, projectPwdAlert, /.{4,32}/, false ]
            };
            var valid = true;
            projectNameAlert.text('');
            projectPwdAlert.text('');
            for(var key in regDict) {
                if(regDict.hasOwnProperty(key)) {
                    if( regDict[key][2].test(regDict[key][0].val()) === regDict[key][3] ){
                        regDict[key][1].text(regDict[key][1].text() + key + ". ");
                        valid = false;
                    }
                }
            }
            var res = ajax_check_project_name_is_exist(projectName.val());
            if (res.status == "ok" && res.is_exist == true){
                projectNameAlert.text('The project name is existed! Please re-enter a new name.');
                valid = false;
            }
            if(!valid)
                return;
            else{
                var new_p_id = ajax_new_project(projectName.val(), projectPwd.val());
                //window.location = '/connection';
                enter_project(new_p_id, projectName.val(), projectPwd.val());

            }
            $('#newPorjectModal').modal('hide');
      }
      var modalEnterHandler = function(event){
            if(event.keyCode == 13){
                modalOKBtnHandler();
            }
      };
      $('#newPorjectModal').on('shown.bs.modal', function (event) {
            clearModal();
            $( "#project-name" ).focus();
            $( "#modalOKBtn" ).bind( "click", modalOKBtnHandler);
            $( "#project-name" ).bind( "keydown", modalEnterHandler);
            $( "#project-pwd" ).bind( "keydown", modalEnterHandler);
      });
      $('#newPorjectModal').on('hidden.bs.modal', function (event) {
            $( "#modalOKBtn" ).unbind( "click", modalOKBtnHandler);
            $( "#project-name" ).unbind( "keydown", modalEnterHandler);
            $( "#project-pwd" ).unbind( "keydown", modalEnterHandler);
      });
}
function menu_component_show(s){
    if(s){
        $("#model_pull_down_menu").show();
        $("#switch_off_project").show();
        $("#delete_project").show();
    }
    else{
        $("#model_pull_down_menu").hide();
        $("#switch_off_project").hide();
        $("#delete_project").hide();
    }
}

var bind_pwd_check_model = function(){
    $('#passwordCheckModal').on('show.bs.modal', function (event) {
        $("#checkPwdHeader").html('Enter ' + projectName + ' password');
    });
    $('#passwordCheckModal').on('shown.bs.modal', function (event) {
        $("#checkPwdAlert").text('');
        $('#passwordCheckModal').find('#check-pwd').val('');
        $( "#check-pwd" ).focus();
        $( "#checkPwdBtn" ).bind( "click", checkPwdHandler);
        $( "#check-pwd" ).bind( "keydown", checkPwdKeyCodeHandler);
    });
    $('#passwordCheckModal').on('hidden.bs.modal', function (event) {
        $("#checkPwdAlert").text('');
        $('#passwordCheckModal').find('#check-pwd').val('');
        $( "#checkPwdBtn" ).unbind( "click");
        $( "#check-pwd" ).unbind( "keydown");
    });
};
var projectID;
var projectName
var pwd;
var enter = function(){
    old_p_id = p_id;
    //set global p_id
    p_id = projectID;
    //bind p_id and p_name on project_pull_down_menu
    $("#project_pull_down_menu").attr("name",p_id);
    $("#project_pull_down_menu").find("a")[0].innerHTML = projectName;
    menu_component_show(true);
    //clear alertMessage
    $("#alertMessage").text('');
    
    check_project_status();
    if(old_p_id < 0){
        switch_project_event_handler();
        delete_project_event_handler();
        update_model_event_handler();
        alert_message_event_handler();
        $(window ).resize(function() {
            redraw_connect_line();
        });
    }

    // make canvas object
    var background_width = window.innerWidth;
    var background_height = window.innerHeight - $('nav').height()+2;
    $('canvas').attr('width', background_width);
    $('canvas').attr('height', background_height);
    ctx = document.getElementById("background").getContext("2d");
    reload_all_data();
    $('#project_pull_down_menu').unbind('click');
    update_project_list_handler();

    exception_poll(3000);
    ajax_turn_on_project();
};
var checkPwdKeyCodeHandler = function(event){
    $("#checkPwdAlert").text('');
    if(event.keyCode == 13){
        checkPwdHandler();
    }
};
var checkPwdHandler = function(){
    var pwd = $("#check-pwd").val();
    var response = ajax_select_project(projectID,pwd);
    if(!response.result)
        $("#checkPwdAlert").text('Password wrong!');
    else{
        $('#passwordCheckModal').modal('hide');
        enter();
    }
};
function enter_project(pid,pName,paswd){
    projectID = pid;
    projectName = pName;
    pwd = paswd;
    var passwordExist = ajax_check_project_password_is_exist(projectID);
    if(passwordExist.is_exist){
        if(pwd != undefined){
            var response = ajax_select_project(projectID,pwd);
            if(!response.result){
                alert("Password wrong!");
                return;
            }
            else
                enter();
        }
        else
            $('#passwordCheckModal').modal('show');
    }
    else
        enter();
}
function choose_project_event_handler() {
    $('.project-list a').unbind('click');
    $('.project-list a').on('click', function(e) {
        if ($(this).text() != 'add project') {
            enter_project($(this).attr('name'), $(this).text());
        } else {
            $('#newPorjectModal').modal('show');
        }
    });
}
function handle_click_model_event(){
    var model_name = $(this).text();
    if($.inArray(model_name, special_model_list) != -1){
        make_special_device_object($(this));
    }
    else
        get_model_feature($(this));
    
}
function make_special_device_object(click_model){

    var dm_id = click_model.attr("val");
    var dm_name = click_model.text();
    var feature_name_array = [];
    var do_id = -1;
    var return_info = ajax_get_device_list(feature_name_array, do_id, dm_id);
    var device_array = return_info['device_info'];
    var is_mounted = return_info['is_mounted'];
    console.log(device_array);
    console.log(is_mounted);

    if (device_array == "") {
        $('#work_area #management_window').html("<h2>Please register a device</h2>");
    }
    else{
        $('#work_area #management_window').empty();
        var outer_d = $('<div>').attr('id', 'dname-list');
        for (var i = 0; i < device_array.length; i++) {
            var a =  $('<a>').attr('href', '#').text(device_array[i][0]);
            a.attr('name', device_array[i][2]);
            var d = $('<div>').append(a);
            outer_d.append(d);
        }

        var work_area = $('#work_area #management_window').empty();
        outer_d.appendTo(work_area);

        //choose_device_event_handler();
        $('#dname-list div').unbind('click');
        $('#dname-list div').on('click', function(e) {

            var df = ajax_get_all_device_feature_by_dm_id(dm_id);
            var odf_list = [];
            var idf_list = [];
            if(df['odf_list'].length > 0)
                odf_list.push(df['odf_list'][0]);
            if(df['idf_list'].length > 0)
                idf_list.push(df['idf_list'][0]);
            var device_object = ajax_create_device_object(p_id, dm_name, idf_list, odf_list);
            var do_id = device_object['ido_id'] || device_object['odo_id']

            var device_name = $(this).text();
            var is_unmount = false;
            $('.choosed').attr('style', 'cursor:pointer;color:blue');

            if ($(this).hasClass('is-unmount')) {
                device_name = "";
                is_unmount = true;
            } else {
                $('.choosed').val(device_name);
            }

            var d_id = $(this).children().attr('name');

            var return_info = ajax_bind_device(do_id, device_name, d_id );
            $('.choosed').attr('name', d_id);
            if (is_unmount ) {
                $('.choosed').val(return_info['p_dm_name']);
            }
            $('#work_area #management_window').empty();
            ajax_restart_project();
            reload_all_data();
        });
    }
}
function get_model_feature(click_model) {
    var model_name = click_model.text();
    // 1. 取得指定 model 的資訊
    var json = ajax_get_model_info(model_name);
    var do_id = '0'; // 因為此時尚未產生 device model icon

    // 判斷該 model 的 device feature 是不是只有一個
    if (json['number_of_df'] > 1 ) {
        // 畫出 DA module 和 DF selection module
        var management_window = $('#management_window').empty();
        // var da_module = make_da_install_module_html();
        // da_module.appendTo(management_window);
        send_da_event_handler(json['model_name']);

        var outer_block = make_model_setting_html(json);  // render the df selection web page
        outer_block.appendTo(management_window);


        // choose checkbox if click label
        $('.label-model-feature').on('click', function(e) {
            l = $(this).prev();
            if (l.prop('checked') == false) {l.prop('checked', true); }
            else{ l.prop('checked', false);}
        });
        delete_device_object_event_handler();
        create_device_object_event_handler(model_name, do_id);

    } else {
        feature_list = {
            'idf_list': json['idf'],
            'odf_list': json['odf'],
            'model_name': json['model_name'],
            'do_id': do_id,
            'p_id': p_id,
        }
        if (ajax_save_device_object_info(feature_list)) {
            reload_all_data();
        }

        var management_window = $('#management_window').empty();
        // var da_module = make_da_install_module_html();
        // da_module.appendTo(management_window);
        send_da_event_handler(json['model_name']);

        setTimeout(function() {
            console.log("AutoMount: ", json['model_name']);
            $('input[value='+ json['model_name'] + ']').click();
        }, 1000);
    }
}

function send_da_event_handler(dm_name) {
    $('#email-send').unbind('click');
    $('#email-send').on('click', function(e) {
        if (email = $('#email-input').val()) {
            ajax_send_da_link(dm_name, '', email);
            show_save_gif ("#email-send", id='save-gif-da')
        }
        $('#management_window').empty();
    });

    $('#sms-send').unbind('click');
    $('#sms-send').on('click', function(e) {
        if (phone = $('#phone-input').val()) {
            ajax_send_da_link(dm_name, phone, '');
            show_save_gif ("#email-send", id='save-gif-da')
        }
        $('#management_window').empty();
    });
}

function create_device_object_event_handler(model_name, do_id) {
    $('#save_model').unbind('click');
    $('#save_model').on('click', function() {
        dm_name = $('.device_model_name').text();
        /*
        if (dm_name == "ML_device") {
        
            console.log('aaa');
            var child = window.open('http://140.113.215.25:9999', 'asdasd', 'height=700,width=400'); //,status=0
            var timer = setInterval(checkChild, 500);
    
            function checkChild() {
                if (child.closed) {
                    myaaa();   
                    clearInterval(timer);
                }
            }
        } else {
            myaaa();
        }
        */
        if (dm_name == "ML_device") {
            console.log('002');
            var x = Math.floor((Math.random() * 89) + 10);
            
            $.ajax({
                dataType: 'jsonp',
                jsonp: 'jsonp_callback',
		url: 'http://ml1.iottalk.tw/set_name_'+x+'.ML_device',
                //success: function () {
                  // do stuff
                //},
            });
            
            
        }
        
        var _a = 0
        console.log(_a);
        for (i = 0; i < 2; i++) {
            var currentdate = new Date(); 
            var _t0 = currentdate.getSeconds();
            var _t1 = currentdate.getSeconds();
            
            while (_t0 == _t1) {
                _a += 1
                var currentdate = new Date(); 
                var _t1 = currentdate.getSeconds();
            }
            console.log(_a);
        }
        
        myaaa();
        
        function myaaa() {
        dm_name = $('.device_model_name').text();
        p_id = $('#project_pull_down_menu').attr('name');
        

        idf_list = [];
        if (dm_name == "Folder_I") { //WTF -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            $('.IDF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.IDF').each(function() {selected_df.push($(this).text());});

            $(selected_df).each(function(index, df_name) {
                if (selected_num[index].toString() != "None") {
                    console.log(df_name);
                    idf_list.push(df_name);
                    idf_list.push(selected_num[index].toString());
                }
            });
        }
        else if (plural_DF_list.indexOf(dm_name) != -1) { //WTF -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            let single_df =[];
            $('.IDF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.IDF').each(function() {selected_df.push($(this).text());});
            $('label[tag="SINGLE"]').each(function() {single_df.push($(this).text());});

            //console.log('B:', selected_num);
            //console.log(selected_df);

            $(selected_df).each(function(index, df_name) {
                if (single_df.indexOf(df_name) == -1)
                    for (num=0; num<selected_num[index]; num=num+1) idf_list.push(df_name+(num+1).toString());
                else if (selected_num[index]>0) idf_list.push(df_name);
            });
        }
        else{
            $('.idf_table > input:checked').each(function() {
                idf_list.push($(this).attr('name'));
            });
        }

        odf_list = [];
        if (dm_name == "Folder_O") { //WTF -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            $('.ODF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.ODF').each(function() {selected_df.push($(this).text());});

            $(selected_df).each(function(index, df_name) {
                if (selected_num[index].toString() != "None") {
                    odf_list.push(df_name);
                    odf_list.push(selected_num[index].toString());
                }
            });
        }
        else if (plural_DF_list.indexOf(dm_name) != -1) { //WTF 2  -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            let single_df =[];
            $('.ODF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.ODF').each(function() {selected_df.push($(this).text());});
            $('label[tag="SINGLE"]').each(function() {single_df.push($(this).text());});

            //console.log('B:', selected_num);
            //console.log(selected_df);

            $(selected_df).each(function(index, df_name) {
                if (single_df.indexOf(df_name) == -1)
                    for (num=0; num<selected_num[index]; num=num+1) odf_list.push(df_name+(num+1).toString());
                else if (selected_num[index]>0) odf_list.push(df_name);
            });
        }
        else{
            $('.odf_table > input:checked').each(function() {
                odf_list.push($(this).attr('name'));
            });
        }

        // send DA download link
        var email = $('#email-input').val();
        var phone = $('#phone-input').val();
        if (email) {
            ajax_send_da_link(dm_name, '', email);
        }
        if (phone) {
            ajax_send_da_link(dm_name, phone, '');
        }

        // save device object
        ajax_create_device_object(p_id, dm_name, idf_list, odf_list);
        reload_all_data();

        setTimeout(function() {
            console.log("AutoMount: ", dm_name);
            $('input[value='+ dm_name + ']').click();
        }, 1000);
    }
    });
}
function advance_device_model_event_handler(model_name) {
    $('#advance').unbind('click');
    $('#advance').on('click', function(e) {
        dm_name = $('.device_model_name').text();
        
        if (model_name == "ML_device") {
        
            var _i = $( "select[name$='Feature']" ).val();
            var child = window.open('http://ml1.iottalk.tw', _i, 'height=800,width=700,left=300,top=100'); //,status=0		
            var timer = setInterval(checkChild, 500);
            
            var my_flag = 0;
            
            function checkChild() {
                if (child.closed) {
                    setTimeout(function() {
                        console.log("AutoMount: ", model_name);
                        $('input[value='+ model_name + '][style="cursor:pointer;"]').click();
                        $('input[value='+ model_name + '][style="cursor:pointer;color:rgb(85, 85, 85)"]').click();
                    }, 1000);
                    my_flag = 1;
                    clearInterval(timer);
                    
                }
            }
            console.log(my_flag);
            
            var timer_0 = setInterval(afterCheckChild, 1000);
            
            console.log(my_flag);
            function afterCheckChild() {
                if (child.closed) {
                    console.log(my_flag);
                    if (my_flag>=1) {
                        my_flag += 1;
                    }
                    if (my_flag>=5) {
                        enter();
                    }
                    if(my_flag>=10) {
                        clearInterval(timer_0);
                    }
                }
            }
        }
    });
}
    
function save_e_device_model_event_handler(model_name, do_id) {
    $('#save_model').unbind('click');
    $('#save_model').on('click', function(e) {
        var feature_list = {'idf_list':[], 'odf_list':[]};

        //for IDF
        if (model_name == "Folder_I") { //WTF -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            $('.IDF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.IDF').each(function() {selected_df.push($(this).text());});

            $(selected_df).each(function(index, df_name) {
                if (selected_num[index].toString() != "None") {
                    feature_list['idf_list'].push(df_name);
                    feature_list['idf_list'].push(selected_num[index].toString());
                }
            });
        }
        else if (plural_DF_list.indexOf(model_name) != -1) {
            let selected_num = [];
            let selected_df = [];
            let single_df =[];
            let json = ajax_get_model_feature(model_name);

            $('.IDF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.IDF').each(function() {selected_df.push($(this).text());});
            $('label[tag="SINGLE"]').each(function() {single_df.push($(this).text());});

            //console.log('A:', selected_num);
            //console.log(selected_df);

            $(selected_df).each(function(index, df_name) {
                if (single_df.indexOf(df_name) == -1) {      // mutiple device feature html code 
                    for (num=0; num<selected_num[index]; num=num+1) {
                        for (var object in json['idf']) {
                            if (json['idf'][object][0] == df_name+(num+1).toString()) { 
                                feature_list['idf_list'].push([df_name+(num+1).toString(), json['idf'][object][1]]);
                                break;
                             }
                        }      
                    }
                } 
                else if (selected_num[index]>0) {            // single device feature html code
                    for (let object in json['idf']) {
                        if (json['idf'][object][0] == df_name ) {
                            feature_list['idf_list'].push([df_name, json['idf'][object][1]]);
                            break;
                        }
                    }
                }
            });
        }
        else{
            // make model info
            var input_checkbox = $(this).siblings().find('input.idf-input:checked')
            input_checkbox.each(function() {
                var label = $(this).next();
                feature_list['idf_list'].push([label.text(), label.attr('name')]); 
            });
        }
      
        //For ODF 
        if (model_name == "Folder_O") { //WTF -> Special case assignmentg by the Someone, or do you have another good idea?
            let selected_num = [];
            let selected_df = [];
            $('.ODF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.ODF').each(function() {selected_df.push($(this).text());});

            $(selected_df).each(function(index, df_name) {
                if (selected_num[index].toString() != "None") {
                    feature_list['odf_list'].push(df_name);
                    feature_list['odf_list'].push(selected_num[index].toString());
                }
            });
        }
        else if (plural_DF_list.indexOf(model_name) != -1) { 
            let selected_num = [];
            let selected_df = [];
            let single_df =[];
            let json = ajax_get_model_feature(model_name);

            $('.ODF_list option:selected').each(function() {selected_num.push($(this).text());});
            $('.label-model-feature.ODF').each(function() {selected_df.push($(this).text());});
            $('label[tag="SINGLE"]').each(function() {single_df.push($(this).text());});
  
            //console.log('A:', selected_num);
            //console.log(selected_df);

            $(selected_df).each(function(index, df_name) {
                if (single_df.indexOf(df_name) == -1) {      // mutiple device feature html code
                    for (num=0; num<selected_num[index]; num=num+1) {
                        for (var object in json['odf']) {
                            if (json['odf'][object][0] == df_name+(num+1).toString()) {
                                feature_list['odf_list'].push([df_name+(num+1).toString(), json['odf'][object][1]]);
                                break;
                             }
                        }
                    }
                }
                else if (selected_num[index]>0) {            // single device feature html code
                    for (let object in json['odf']) {
                        if (json['odf'][object][0] == df_name ) {
                            feature_list['odf_list'].push([df_name, json['odf'][object][1]]);
                            break;
                        }
                    }
                }
            });
        }
        else{
            var output_checkbox = $(this).siblings().find('input.odf-input:checked')
            output_checkbox.each(function() {
                var label = $(this).next();
                feature_list['odf_list'].push([label.text(), label.attr('name')]);
            });
        }

        feature_list['model_name'] = model_name;
        feature_list['do_id'] = do_id;
        feature_list['p_id'] = p_id;
         /*
            feature_list = {
                'odf_list': [[df_name, df_id], ...],
                'idf_list': [[df_name, df_id], ...],
                'model_name': dm_name,
                'do_id': do_id,
            }
         */

        if (ajax_save_device_object_info(feature_list)) {
            reload_all_data();
        }

        // change to send button
        var email = $('#email-input').val();
        var phone = $('#phone-input').val();
        if (email) {
            ajax_send_da_link(model_name, '', email);
        }
        if (phone) {
            ajax_send_da_link(model_name, phone, '');
        }
    });
}

function check_project_status() {
    if (response = ajax_get_project_status(p_id)) {
        if (response == 'Exec') {
            $('#switch_off_project').attr('src', '/static/images/off.png');
        } else if (response == 'Stop') {
            $('#switch_off_project').attr('src', '/static/images/on.png');
            if (!$('.alert-message').hasClass('alert-message-hidden')) {
                $('.alert-message').addClass('alert-message-hidden');
            }
        }
    }
}

function delete_project_event_handler() {
    $('#delete_project').on('click', function(e) {
	var decision = confirm("Delete this project?");    
	if (decision){    
            clearTimeout(exception_timer);
            if (ajax_delete_project(p_id)) {
                window.location = '/connection';
            }
        }
    });
}

function switch_project_event_handler() {
    $('#switch_off_project').on('click', function(e) {
        var st = $(this).attr('src');
        st = st.split('/');
        if (st[3] == 'off.png') {
            ajax_turn_on_project();
            $('#switch_off_project').attr('src', '/static/images/on.png');
            if (!$('.alert-message').hasClass('alert-message-hidden')) {
                $('.alert-message').addClass('alert-message-hidden');
            }
        }else {
            ajax_turn_off_project();
            $('#switch_off_project').attr('src', '/static/images/off.png');


            setTimeout(function() {        //Enable Project AutoOn
                ajax_turn_on_project();
                $('#switch_off_project').attr('src', '/static/images/on.png');
                if (!$('.alert-message').hasClass('alert-message-hidden')) {
                    $('.alert-message').addClass('alert-message-hidden');
                }
            }, 1000);
        }
    });
}

function choose_device_event_handler() {
    $('#dname-list div').unbind('click');
    $('#dname-list div').on('click', function(e) {
        var device_name = $(this).text();
        var is_unmount = false;
        $('.choosed').attr('style', 'cursor:pointer;color:blue');

        if ($(this).hasClass('is-unmount')) {
            device_name = "";
            is_unmount = true;
        } else {
            $('.choosed').val(device_name);
        }

        var do_id = $('.choosed').parents().filter('.div-outer').find('.setting_obj').attr('name');
        var d_id = $(this).children().attr('name');

        var return_info = ajax_bind_device(do_id, device_name, d_id );
        $('.choosed').attr('name', d_id);
        if (is_unmount ) {
            $('.choosed').val(return_info['p_dm_name']);
        }
        $('#work_area #management_window').empty();
        ajax_restart_project();
    });
}

function unmount_device(do_id) {
    var device_name = "";
    var is_unmount = true;
    $('.choosed').attr('style', 'cursor:pointer;color:rgb(85, 85, 85)');
    var model_id = $('.choosed').parent().parent().find('.setting_obj').attr('name');
    var return_info = ajax_unbind_device(do_id, device_name, 0);
    $('.choosed').val(return_info['p_dm_name']);
    $('#work_area #management_window').empty();
    ajax_restart_project();
}

function mount_device_event_handler() {
    $('div[name=out_device] input, div[name=in_device]  input').unbind('click');
    $('div[name=out_device] input, div[name=in_device]  input').on('click', function () {
        var feature_name_array = [];
        var device = $(this).parents().get(2);
        var device_model_icon = $(this).parents().get(1);
        var do_id = $(device_model_icon).find('img.setting_obj').attr('name');
        $('.choosed').removeClass('choosed');
        $(this).addClass('choosed');
        $('.choosed').css('color', '').css('cursor', 'pointer');
        var feature_array = $(device).children().find('label.label-feature');

        feature_array.each(function(index ) {
            feature_name_array.push($(this).text());
        });
        var return_info = ajax_get_device_list(feature_name_array, do_id);
        var device_array = return_info['device_info'];
        var is_mounted = return_info['is_mounted'];

        if (is_mounted) {
            unmount_device(do_id);
        }
        else if (device_array == "") {
            $('#work_area #management_window').empty();
        }
        else if (device_array.length > 1) {
            $('#work_area #management_window').empty();

            var outer_d = $('<div>').attr('id', 'dname-list');
            for (var i = 0; i < device_array.length; i++) {
                var a =  $('<a>').attr('href', '#').text(device_array[i][0]);
                a.attr('name', device_array[i][2]);
                var d = $('<div>').append(a);
                outer_d.append(d);
            }

            var work_area = $('#work_area #management_window').empty();
            outer_d.appendTo(work_area);
            choose_device_event_handler();
        } else {
            var device_name = device_array[0][0];
            $('.choosed').attr('style', 'cursor:pointer;color:blue');

            $('.choosed').val(device_name);
            var do_id = $('.choosed').parent().parent().find('.setting_obj').attr('name');
            var return_info = ajax_bind_device(do_id, device_name, device_array[0][2]);
            $('.choosed').attr('name', return_info['d_id']);
            ajax_restart_project();

            // 顯示 unmount 在 right subwindow
            $('#work_area #management_window').empty();
            var outer_d = $('<div>').attr('id', 'dname-list');
            var work_area = $('#work_area #management_window').empty();
            outer_d.appendTo(work_area);
            choose_device_event_handler();
        }
    });
}

function check_duplicate_and_circle_connection(circle_node, feature_node) {
    if ($(feature_node.parents().filter('.device-obj')).attr('name')[0] == 'i') var df_type = 'input';
    else var df_type = 'output';
    var na_id = $(circle_node.parents().get(1)).attr('name');
    var na_idx = circle_node.attr('name');
    var df_id = feature_node.attr('name');

    check = ajax_check_duplicate_circle_connection(na_id, df_id, df_type);

    if (check['is_duplicate'] == '0') {
        // deaw line and save conenction
        draw_line_between_feature_circle(feature_node, circle_node);
        ajax_save_circle_connect_setting(na_idx, na_id, df_id);

        // make df module in workspace window
        var odfo_id = null;
        if (df_type == 'output') {
           odfo_id = df_id;
        } else {
           odfo_id = '0';
        }
        construct_stage1_setting_block(na_id, odfo_id);
    }
    else{
        if (check['remove_circle'] == 1) {
            var c_node = $('div[name='+check['na_id']+'].map-block img')
            c_node.addClass('hidden-flag');
            var c_label = $(c_node.parents().get(1)).find('label');
            c_label.addClass('hidden-flag');
        }

        if (df_type == 'output') {
            construct_stage1_setting_block(na_id, df_id);
        }
    }
    ajax_restart_project();
}

function connect_feature_circle_event_handler() {
    $('.map-img-div img').unbind('click');
    $('.map-img-div img').on('click', function(e) {
        if ($('img.feature-circle-clicked').length != 0) {
            $('img.feature-circle-clicked').removeClass('feature-circle-clicked');
        } else if ($('div.feature-circle-clicked').length == 0) {
            $(this).addClass('feature-circle-clicked');
        } else {
            var feature_node = $($('div.feature-circle-clicked').get(0));
            var circle_node = $(this);
            check_duplicate_and_circle_connection(circle_node, feature_node);
            feature_node.removeClass('feature-circle-clicked');
            feature_node.removeClass('feature-clicked');
        }
        var na_id = $(this).parent().parent().attr('name');
        construct_stage1_setting_block(na_id, '0');
    });
}

function send_connection_data_to_server(circle_node, start_node, end_node) {
    connection_info = [];
    var join_name = $(circle_node.parents().get(1)).find('label').text();
    var join_idx = $(circle_node.parents().get(1)).find('label').attr('name');
    var idfo_id = $(start_node.get(0)).attr('name');    // start_feature_id
    var odfo_id = $(end_node.get(0)).attr('name');      // end_feature_id
    connection_info.push(join_name);
    connection_info.push(join_idx);
    connection_info.push(idfo_id);
    connection_info.push(odfo_id);

    var id_dict = ajax_save_connection_line(connection_info, p_id);

    // set na_id to circle_node
    $(circle_node.parents().get(1)).attr('name', id_dict['na_id']);
    construct_stage1_setting_block(id_dict['na_id'], id_dict['odfo_id']);
}


function plot_single_device_feature_module(device_feature) {
    $('#management_window').empty();
    $('<div>',{ 'id':'module_mapping_setting_outer_block'}).appendTo('#management_window');

    var dfo_id = $($(device_feature).get(0)).attr('name');
    var fn_info = ajax_get_stage1_df_info(dfo_id);

    // 2. 檢查是 idf 還是 odf，取得 device feature id
    if ($($(device_feature).parents().get(1)).attr('name')[0] == 'i') { 
        // 是 idf name="in_device"
        if (Disable_IDF_default_value_editor == true){
            console.log('IDF default value editor is disabled.');
            return;
        }
        var df_outer_block = make_single_idf_block_html(fn_info);
    } else {
        // 是 odf
        if (Disable_ODF_default_value_editor == true){
            console.log('ODF default value editor is disabled.');
            return;
	}	
        var df_outer_block = make_single_odf_block_html(fn_info);
    }

    df_outer_block.appendTo('#module_mapping_setting_outer_block');

    bind_rename_df_alias();
    save_idf_default_event_handler();
    save_odf_default_event_handler();
    // get_mf_function_list();
}

function bind_rename_df_alias() {
    $('.div-odf-first-tab-title, .div-idf-tab-title-left').unbind('click');
    $('.div-odf-first-tab-title, .div-idf-tab-title-left').bind('click', function () {
        $(this).unbind('click');
        $(this).find('.label-odf, .label-idf').attr('hidden', true);
        let alias_name = $(this).find('.label-odf, .label-idf').text();
        let textarea = $('<input>', {'id':'tb-alias-name', 'value': alias_name, 'type':'text', 'width': '100%'});
        textarea.appendTo($(this));
        $(textarea).select();
        $(textarea).focusout(function(){
            save_alias_name();
            bind_rename_df_alias();
        });
        $(textarea).keyup(function (e) {
            if (e.keyCode == 13) {
                save_alias_name();
            }
        });
    });
}

function save_alias_name() {
    let textarea = $('.div-odf-first-tab-title, .div-idf-tab-title-left').find('#tb-alias-name');
    let label = $('.div-odf-first-tab-title, .div-idf-tab-title-left').find('.label-odf, .label-idf')

    let dfo_id = label.attr('name');
    let dfo_name = label.text();
    let new_name = textarea.val().replace(/^\s+|\s+$/g, ''); //trim() need be a base function
    label.attr('hidden', false);
    textarea.remove();

    if (new_name && new_name != dfo_name) {
        label.text(new_name);
        $('<span>', { 'class':'glyphicon glyphicon-pencil'}).appendTo(label);
    }
}

function connect_feature_and_feature(device_feature) {
    var start_node = $($('div.feature-clicked').get(0));
    var end_node = device_feature;

    // if click different column
    if (start_node.parent().parent().attr('name') != $(device_feature).parent().parent().attr('name')) { // name="in_device" vs name="out_device"

        // check these two feature connection is duplicate
        if ($($(end_node).parents().get(1)).attr('name')[0] == 'i') {
            var idf_id = $($(device_feature).get(0)).attr('name');
            var odfo_id = $(start_node.get(0)).attr('name');
        } else {
            var odfo_id = $($(end_node).get(0)).attr('name');
            var idf_id = $(start_node.get(0)).attr('name');
        }

        var feature_id_list = [idf_id, odfo_id];
        var check = ajax_check_duplicate_connection(feature_id_list);

        if (check['is_duplicate'] == '0') {
            // 沒有重複，畫線
            var this_node = $(end_node);
            var circle_node = draw_line_between_two_feature(this_node, start_node);
            f_info = send_connection_data_to_server(circle_node, start_node, this_node);
            circle_node.removeClass('hidden-flag');
            var circle_label = $(circle_node.parents().get(1)).find('label');
            circle_label.removeClass('hidden-flag');
            ajax_restart_project();
        }
    } // end if click different column

    start_node.removeClass('feature-clicked');
    start_node.removeClass('feature-circle-clicked');
}

function connect_circle_and_feature(device_feature) {
    var circle_node = $('img.feature-circle-clicked');
    var feature_node = $(device_feature);
    check_duplicate_and_circle_connection(circle_node, feature_node);
    circle_node.removeClass('feature-circle-clicked');
}

function save_connection_line() {
    var is_odf = $($(this).parents().get(2)).attr('id') == 'out_device_column';
    var df_id = $(this).attr('name');
    var na_id = '0';
    if (is_odf) {
        na_id = ajax_check_dfo_is_connected(df_id);
    }

   // 1. 檢查 circle 有沒有被點
	if ($('img.feature-circle-clicked').length != 0) {
		// 有被點

		// 檢查是不是 odf
		if (is_odf) {
			// 檢查有沒有 dup line
			if (ajax_check_duplicate_circle_connection(na_id, df_id, 'output')['is_duplicate'] == '1') {
				// 有 dup line，變紅線、畫 workspace window
				construct_stage1_setting_block(na_id, df_id);
			} else {
				// 沒有 dup line，連線
				connect_circle_and_feature(this);
			}
		} else{
			connect_circle_and_feature(this);
		}
	// 2. 檢查另一邊的 feature 有沒有被點
	} else if ($('div.feature-clicked').length != 0) {
		// 有被點
		// 畫線 feature with feature
		connect_feature_and_feature(this)
	} else {
		// 沒有被點
		// 變藍色
		$(this).addClass('feature-clicked');
		$(this).addClass('feature-circle-clicked');

		plot_single_device_feature_module(this);
	}
}

function connect_feature_event_handler() {
    $('.feature_obj').unbind('click');
    $('.feature_obj').on('click', save_connection_line);
}

function redraw_connect_line() {
    var wid = $('.div-catagory').width() + "px";
    $('.div-catagory').css('height', wid);
    $('.setting_obj').css('height', wid);

    $('.div-device').css('height', wid);
    $('.label-device').css('line-height', wid/2);
    $('.label-feature').css('line-height', wid);
    $('.div-obstacle').css('height', wid);

    $('.img-input-feature').css('height', wid);
    $('.img-input-feature').css('width', wid);
    $('.img-output-feature').css('height', wid);
    $('.img-output-feature').css('width', wid);
    $('.feature_obj').css('height', wid);

    var work_area_padding = $('#work_area').outerHeight() - $('#management_window').outerHeight();

    var in_device_column_height = 0;
    var out_device_column_height = 0;
    var work_area_height = 0;
    var window_height = window.innerHeight-$('nav').height() - 2;
    if ($('#in_device_column').find('.div-outer').length > 0) {
        in_device_column_height = $('#in_device_column').find('.div-outer').last().offset().top + $('#in_device_column').find('.div-outer').last().height();
    }
    if ($('#out_device_column').find('.div-outer').length > 0) {
        out_device_column_height = $('#out_device_column').find('.div-outer').last().offset().top + $('#out_device_column').find('.div-outer').last().height();
    }
    if ($('#management_window').find('div').length > 0) {
        work_area_height = $('#in_device_column').offset().top + $('#management_window').find('div').first().height();
    }
    var general_height = Math.max(in_device_column_height, out_device_column_height, work_area_height, window_height, 1000);
    $('#graphical_layout_window').css('height', general_height);
    $('#work_area').css('height', general_height);
    var canvas = $('#background');
    var ctx = document.getElementById("background").getContext("2d");
    ctx.canvas.height = general_height;
    ctx.clearRect(0 , 0 , canvas.width(), canvas.height());

    //draw lines
    var connection_pair = ajax_reload_connect_line(p_id);
    $.each(connection_pair, function (index, value ) {
        var feature_node = $('.feature_obj[name='+value[1]+']');
        var circle_node = $('.map-block[name='+value[0]+']').find('img');
        var color = value[2];
        draw_line_between_feature_circle(feature_node, circle_node, color);
    });

    if ($('.div-idf-monitor-outer').length == 0 && $('.div-odf-monitor-outer').length == 0) {
        var outer_height =  $('.div-idf-monitor-outer .div-add-function-outer').height() - 70;
        $('.div-idf-monitor-outer .div-intro-block').css('height', outer_height);

        var outer_height =  $('.div-join-monitor-outer .div-add-function-outer').height() - 70;
        $('.div-join-monitor-outer .div-intro-block').css('height', outer_height+30);

        var outer_height =  $('.div-odf-monitor-outer .div-add-function-outer').height() - 70;
        $('.div-odf-monitor-outer .div-intro-block').css('height', outer_height);
    }
}

function bind_move_in_df_function_list() {
    $('#add_function').unbind('click');
    $('#add_function').on('click', function(e) {
        if ($('.other_function_select option:selected').length != 0) {
            var fn_info = {'fn_id':'', 'dfo_id':'' };
            fn_info['dfo_id'] = parseInt($('.div-program-title > label').attr('name'));
            fn_info['fn_id'] = parseInt($('.other_function_select option:selected').attr('name'));

            var fn_list = ajax_move_in_df_function_list(fn_info); 
            // positive_list = { 'other_list': [['x1', 1],...], 'quick_list':[['x2', 3], ...]}
            var other_function_select = $('.other_function_select');
            other_function_select.empty();
            for (var i=0; i<fn_list['other_list'].length; i++) {
                $('<option>', { 'text': fn_list['other_list'][i][0],  // function name
                                'name':fn_list['other_list'][i][1] }).appendTo(other_function_select); // function id
            }

            var exist_function_select = $('.exist_function_select');
            update_positive_list_of_function_management(exist_function_select, fn_list);
        }
    });

}

function bind_move_out_df_function_list() {
    $('#remove_function').unbind('click');
    $('#remove_function').on('click', function(e) {
        if ($('.exist_function_select option:selected').length != 0) {
            // check if function can be remove
            var fn_name = $('.exist_function_select option:selected').text();
            if ($('.exist_function_select option:selected').length != 0 ) {
                var fn_name = $('.exist_function_select option:selected').text();
                if (ajax_check_function_is_used(fn_name)  == '1') {
                    alert('This function has been used, it can not be removed');
                    return;
                } else if (fn_name == 'add new function') {
                    return;
                }
            }
            else {
                return;
            }

            var fn_info = {'fn_id':'', 'dfo_id':'' };
            fn_info['dfo_id'] = parseInt($('.div-program-title > label').attr('name'));
            fn_info['fn_id'] = parseInt($('.exist_function_select option:selected').attr('name'));

            var fn_list = ajax_move_out_df_function_list(fn_info); 
            // positive_list = { 'other_list': [['x1', 1],...], 'quick_list':[['x2', 3], ...]}
            var other_function_select = $('.other_function_select');
            other_function_select.empty();
            for (var i=0; i<fn_list['other_list'].length; i++) {
                $('<option>', { 'text': fn_list['other_list'][i][0],  // function name
                                'name':fn_list['other_list'][i][1] }).appendTo(other_function_select); // function id
            }

            var exist_function_select = $('.exist_function_select');
            update_positive_list_of_function_management(exist_function_select, fn_list);
        }
    });

}

stage_changed = "";
function update_substage_list(substage_info) {
    if ($('.div-idf-monitor-outer').length != 0) {
        var target_select = $('.div-idf-monitor-outer').find('.step-select');
        target_select.empty();
        $.each(substage_info['idf'], function(index, value) {
            $('<option>', {'text':value}).appendTo(target_select);
        });
        target_select.unbind('change');
        target_select.change(function() {
            stage_changed = "x";
        });
    }

    if ($('.div-odf-monitor-outer').length != 0) {
        var target_select = $('.div-odf-monitor-outer').find('.step-select');
        target_select.empty();
        var i = 1;
        $.each(substage_info['odf'], function(index, value) {
            $('<option>', {'text':value}).appendTo(target_select);
        });
        target_select.unbind('change');
        target_select.change(function() {
           stage_changed = "y";
        });

    }
}

function click_right_event_handler() {
    $('.setting_obj').unbind();
    $('.setting_obj').click(function() {
        // 1. 取得 do_id
        var div_outer = $(this).parents().get(1);
        var do_id = $(div_outer).find('img.setting_obj').attr('name');

        // 2. 抓取 model 的資料
        var json = ajax_get_model_icon_info(do_id);

        // 3. 重畫出選擇 device feature 的頁面
        var management_window = $('#management_window').empty();

       // var da_module = make_da_install_module_html();
       // da_module.appendTo(management_window);

        var outer_block = make_model_feature_selector_html(json);
        outer_block.appendTo(management_window);

        // choose checkbox if click label
        $('.label-model-feature').on('click', function(e) {
            l = $(this).prev();
            if (l.prop('checked') == false) {l.prop('checked', true); }
            else{ l.prop('checked', false);}
        });

        delete_device_object_event_handler();
        save_e_device_model_event_handler(json['model_name'], do_id);
        send_da_event_handler(json['model_name']);
        $('.feature-circle-clicked').removeClass('feature-circle-clicked');
    });
}

function alert_message_event_handler() {
    $('.alert-message img').click(function() {
        var alert_div = $('<div>', {'id':'alert-dialog', 'title':'Exception Message'});
        $('<textarea>', {'text':alert_message, 'disabled':'disabled'}).appendTo(alert_div);
        alert_div.dialog({
           closeOnEscape: true,
           position: {my: 'top', at: 'top+150'},
           modal: true,
           width: 630,
           height: 500,
           dialogClass: '.alert-class',
        });
        $('.ui-dialog-titlebar').css('background','rgb(57, 97, 113)');
        $('.ui-widget-header').css('border','#087CE7');
     });
}

function exception_poll(delay) {
    $.ajax({
        url: '/get_exception_status', //TODO
        type:'POST',
        data: {p_id:p_id},
        error: function(request,error) {
            exception_timer = setTimeout(function() {
                exception_poll(delay);
            }, delay);
        },
        success: function(response) {
            var return_info = $.parseJSON(response);

            // 這段註解打開可以開啟 exception 功能
            if (return_info['exception_msg'] != "") {
                $('.alert-message').removeClass('alert-message-hidden');
                alert_message = return_info['exception_msg'];
            } else {
                $('.alert-message').addClass('alert-message-hidden');
                alert_message = "";
            }
            if (return_info['btn_status'] == 'Exec') {
                $('#switch_off_project').attr('src','/static/images/off.png');
            } else if (return_info['btn_status'] == 'Stop') {
                $('#switch_off_project').attr('src','/static/images/on.png');
            }
            if (return_info['redraw'] == true ) {
                reload_all_data();
               /* $(".div-catagory-device").each(function(){
					var do_id = $(this).find(".setting_obj").prop("name");
					var d_id = $(this).find(".label-device").prop("name");
					console.log("set df status code: " + ajax_set_df_status(do_id, d_id));
				});*/
            }
            // End of 開啟 exception 功能

            exception_timer = setTimeout(function() {
                exception_poll(delay);
            }, delay);
        }
    }); // ajax
}

function click_right_circle_event_handler() {
    $('.map-img-div img').unbind('mousedown');
    $('.map-img-div img').unbind('contextmenu');
    $('.map-img-div img').bind("contextmenu", function() { return false; });
    $('.map-img-div img').mousedown(function(e) {
        if (e.which == 3) {   // 點擊右鍵

            // 1. 取得 do_id
            //var div_outer = $(this).parents().filter('.device-obj')
            var na_id =$(this).parent().parent().attr('name');

            if ($('.div-idf-monitor-outer').length == 0 && $('.div-odf-monitor-outer').length == 0) {
                $('#management_window').empty();
                var div_join_monitor_outer = make_join_monitor_block_html();
            }
            // 2. 取得 monitor 資料
            var monitor_info = ajax_get_monitor_info(na_id);
            monitor_info['na_id'] = na_id;
            var monitor_type = $(this).parent().parent().parent().attr('name');

            var substage_list = [];
            var div_idf_monitor_outer = make_idf_monitor_block_html(monitor_info, substage_list);
            stop_and_continue_event_handler();
            step_event_handler();
            send_event_handler();
            feature_change_event_handler('input', monitor_info['is_multiple_join']);
            table_or_chart_event_handler('#idf_tableorchart', '.div-idf-monitor-outer');

            var substage_list = [];
            monitor_info['monitor_type'] = 'output';
            var div_odf_monitor_outer = make_odf_monitor_block_html(monitor_info, substage_list);
            feature_change_event_handler('output', monitor_info['is_multiple_join']);
            table_or_chart_event_handler('#odf_tableorchart', '.div-odf-monitor-outer');


            // 更新 input monitor 跟 output monitor 的 substage_list
            var na_id =  $('.div-idf-monitor-outer').find('label').attr('name');
            var odfo_id = $('.div-odf-monitor-outer').find('select.output-df-select option:selected').attr('name');
            var substage_info = ajax_get_substage_list(na_id, odfo_id, monitor_info['is_multiple_join']);
            update_substage_list(substage_info);

            $('.div-idf-monitor-outer').on("remove", function () {
                $('div[name="in_device"]').removeAttr('style');
            });

            $('.div-odf-monitor-outer').on("remove", function () {
                $('div[name="out_device"]').removeAttr('style');
            });

            // 顯示或隱藏 join monitor
            if (monitor_info['is_multiple_join'] == true) {
                if ($('.div-join-monitor-outer').hasClass('join-mointor-hidden')) 
                    $('.div-join-monitor-outer').removeClass('join-mointor-hidden');
            } else {
                if (!$('.div-join-monitor-outer').hasClass('join-mointor-hidden'))
                    $('.div-join-monitor-outer').addClass('join-mointor-hidden');
            }
            table_or_chart_event_handler('#join_tableorchart', '.div-join-monitor-outer');
            clearTimeout(monitor_timer);
            pull_monitored_data(1000, 'Continue');
        }
    });
}

function construct_stage1_setting_block(na_id, odfo_id) {
    var f_info = ajax_get_stage1_info(na_id, odfo_id);

    var management_window = $('#management_window').empty();

    if (f_info['all_idf_info'].length + f_info['odf_info'].length > 0) {
        var join_name = $('.map-block[name='+f_info['na_id']+']').find('label.join-input').text()
        var outer_block = $('<div>',{ 'id':'module_mapping_setting_outer_block'});

        var connection_name_div = $('<div>',{ 'style':'width:100%', 'id':'connection_name_div'});
        $('<label>',{ 'style':'margin:2%', 'text':'Connection Name:', 'name':f_info['na_id'] }).appendTo(connection_name_div);
        $('<input>',{ 'type':'text', 'style':'width:10%', 'class':'join_name', 'value':join_name }).appendTo(connection_name_div);
        $('<button>', { 'name':f_info['na_id'], 'class':'mapping_save save_button','text': 'Save',}).appendTo(connection_name_div);
        $('<button>', { 'class':'mapping_delete save_button','text': 'Delete',}).appendTo(connection_name_div);
        connection_name_div.appendTo(outer_block);

        for (var i=0; i<f_info['all_idf_info'].length; i++) {
            var idf_outer_block = make_idf_module_html(f_info, i);

            idf_outer_block.appendTo(outer_block);
        }

        if (f_info['join_fn_id'] != null) {
            var join_outer_block = make_join_module_html(f_info);
            join_outer_block.appendTo(outer_block);
        } else {
            $('<hr>', { 'style':'margin-bottom:10px; margin-top:10px;' }).appendTo(outer_block);
        }

        if (f_info['odf_info'].length > 0) {
            var odf_outer_block = make_odf_module_html(f_info);
            odf_outer_block.appendTo(outer_block);
        }

        outer_block.appendTo(management_window);

        // get_df_function_list_event_handler();
        delete_single_connection_line_event_handler();
        delete_all_connection_line_event_handler();
        save_connection_line_event_handler();
        redraw_connect_line();
    }
}

function delete_single_connection_line_event_handler() {
    $('.module-delete-button').unbind('click');
    $('.module-delete-button').on('click', function(e) {
        // 找出 working area 上面的 odfo_id
        var odfo_id = $('.odf-module-name').attr('name');
        if (typeof odfo_id == 'undefined') {
            odfo_id = '0';
        }

        // 找出要砍掉的線段 df_id,na_id
        var outer_table = $(this).parents('table')
        var kill_dfo_id = "";
        if ($(outer_table).attr('class') == 'idf-module') {
            kill_dfo_id = $(outer_table).find('.idf-module-name').attr('name');
        } else{
            kill_dfo_id = $(outer_table).find('.odf-module-name').attr('name');
        }
        var na_id = $('#connection_name_div label').attr('name');

        // call route 砍線
        var remove_line_info = ajax_delete_connection_line_segment(na_id, kill_dfo_id, odfo_id);
        $('.feature-circle-clicked').removeClass('feature-circle-clicked');


        // remove circle
        var circle_node = $('div[name='+na_id+'].map-block img')

        if (remove_line_info['remove_circle'] == "1") {
            $('div[name='+na_id+'].map-block').removeAttr('name');
            $(circle_node.parents().get(1)).removeClass('connected');
            circle_node.addClass('hidden-flag');
            var circle_label = $(circle_node.parents().get(1)).find('label');
            circle_label.addClass('hidden-flag');
        }

        // 重畫 working area 的畫面
        construct_stage1_setting_block(remove_line_info['na_id'], remove_line_info['odfo_id']);
        redraw_connect_line();
        ajax_restart_project();
    });
}

function delete_all_connection_line_event_handler() {
    $('.mapping_delete').unbind('click');
    $('.mapping_delete').on('click', function(e) {
        var join_name = $('#connection_name_div > input').val();
        var r = confirm("Are you sure to delete the "+join_name+' ?');
        if (r == true) {
            var na_id = $('.mapping_save').attr('name');
            ajax_delete_connection_line(na_id);
            $('.map-block[name='+na_id+']').removeClass('connected');
            $('.map-block[name='+na_id+'] > .map-lable-div > label').addClass('hidden-flag');
            $('.map-block[name='+na_id+'] > .map-img-div > img').addClass('hidden-flag');
            $('.map-block[name='+na_id+'] > .map-img-div > img').removeClass('feature-circle-clicked');
            ajax_restart_project();
            reload_all_data();
        }
    });
}

function check_arr_dup(A ) {
    var i, j, n;
    n=A.length;
    for (i=0; i<n; i++) {
        for (j=i+1; j<n; j++) {
            if (A[i]==A[j]) return true;
    }   }
    return false;
}

function save_connection_line_event_handler() {
    $('.mapping_save').unbind('click');
    $('.mapping_save').on('click', function(e) {
        is_save_flag = 1;

        if ($('table.join-module').length == 0) { // Single Join (只有一個 IDF)

            // 檢查 idf function 和 odf function 兩個其中一個一定要設定
            is_set_idf_func =  1;
            if ($('table.idf-module .idf-module-func .idf-module-select option:selected').text() == 'disabled') {
                is_set_idf_func =  0;
            }
            is_set_odf_func =  1;
            $('table.odf-module .odf-module-select option:selected').each(function() {
                if ($(this).text() == 'disabled') {
                    is_set_odf_func = 0;
                }
            });
            //if (is_set_idf_func == 0 && is_set_odf_func == 0) {
            //    alert('One of IDF function and ODF function should be set.');
            //    is_save_flag = 0;
            //}
        } else {
            var join_index_arr = []
            $('table.join-module .join-module-line .join-module-select option:selected').each(function() {
                join_index_arr.push($(this).text());
            });
            if (check_arr_dup(join_index_arr)) {
                alert('Join index can not duplicate.');
                is_save_flag = 0;
            }
        }

        if (is_save_flag == 1) {
            ajax_restart_project();

            var info = {
                'join_name':'',
                'na_id':'',
                'all_idfo_id':[],
                'all_idf_info':[],
                'all_idf_fn_id':[],
                'odfo_id': '',
                'odf_info': [],
                'join_fn_id': '',
                'join_index':[],
            };

            info['join_name'] = $('#connection_name_div > input').val();
            info['na_id'] = $(this).attr('name');

            $('.idf-module-name').each(function (index) {
                info['all_idfo_id'].push($(this).attr('name'));
            });

            $('table.idf-module').each(function(index) {
                var idf_info = [];
                var idf_type_list = $(this).find('.idf-module-type select option:selected');
                idf_type_list.each(function(index) {
                    idf_info.push($(this).text());
                });
                info['all_idf_info'].push(idf_info);
            });

            $('table.idf-module').each(function(index) {
                var idf_func_list = $(this).find('.idf-module-func select option:selected');
                idf_func_list.each(function(index) {
                    info['all_idf_fn_id'].push($(this).attr('name'));
                });
            });

            info['odfo_id'] = $('.odf-module-name').attr('name');
            $('table.odf-module').find('.odf-module-func select').each(function(index) {
                info['odf_info'].push($(this).find('option:selected').attr('name'));
            });

            info['join_fn_id'] = $('table.join-module').find('.join-module-func select option:selected').attr('name');
            $('table.join-module').find('.join-module-line select').each(function(index) {
                info['join_index'].push($(this).find('option:selected').text());
            });

            /*
                join_name = "join name"
                na_id = na_id
                all_idfo_id = [idfo_id, idfo_id]
                all_idf_info = ['sample', 'variant', ...]
                all_idf_fn_id = [fn_id, fn_id]
                odfo_id = odfo_id
                odf_info = [fn_id, fn_id]
                join_fn_id = fn_id
                join_index = [1,3,2]
            */

            if (ajax_save_connection_configuration(info, p_id)) {
                // set join name to circle label
                var join_name = $('#management_window').find('input.join_name').val();
                $('.map-block[name=' + info['na_id'] + ']').find('label').text(join_name);
            }

            show_save_gif (".mapping_save", id='save-gif-user')
        }
    });
}

function draw_line_between_two_feature(feature1_node, feature2_node) {
    // user two feature node to get circle node
    var circle_node = get_circle_node(feature1_node, feature2_node);
    // draw_line: input feature->circle, output feature->circle
    draw_line_between_feature_circle(feature1_node, circle_node);
    draw_line_between_feature_circle(feature2_node, circle_node);
    return circle_node;
}

function get_circle_node(feature_node1, feature_node2) { //this , start_node
    var device_column_width = $('#in_device_column').outerWidth();
    var in_device_column_position = $('#in_device_column').position();
    var out_device_column_position = $('#out_device_column').position();

    var end_x = out_device_column_position.left;
    var end_y = feature_node1.position().top + feature_node1.outerHeight()/2 + out_device_column_position.top;
    var start_x = device_column_width + in_device_column_position.left;
    var start_y = feature_node2.position().top + feature_node2.outerHeight()/2 + in_device_column_position.top;
    var circle_node = count_circle_node(start_x, start_y, end_x, end_y);
    return circle_node;
}

function count_circle_node(x1, y1, x2, y2) {
    var circle_x = $('.map-column').position().left + $('.map-column').width() / 2;
    var m = (y1-y2)/(x1-x2);
    var tmp_y = y2 - m*(x2 - circle_x)

    var map_block_top = $($('div.map-block').get(0)).children().find('img').position().top;
    var map_column_top = $('div.map-column').position().top;
    var map_block_image_half_top = 20/2;
    var first_map_block  = map_column_top + map_block_top + map_block_image_half_top;

    var i = 0;
    for (i=0; i<100; i++) {
        if (first_map_block + 60*i > tmp_y) {
            if ($($('div.map-block').get(i-1)).hasClass('connected')) {
                continue;
            }
            circle_y = first_map_block + 45*(i-1);
            break;
        }
    }

    var choosed_map_block = i-1;
    $($('div.map-block').get(choosed_map_block)).addClass('connected')
    return $($('div.map-block').get(choosed_map_block)).find('img');
}

function draw_line_between_feature_circle(feature_node, circle_node, color) {
    var start_x_y = count_feature_coordinate(feature_node);
    var circle_x_y = count_circle_coordinate(circle_node);
    draw_line(start_x_y[0], start_x_y[1], circle_x_y[0], circle_x_y[1], color);
}

function count_feature_coordinate(feature_node ) {
    if (feature_node.parents().filter('.device-obj').parent().attr('id') == 'in_device_column') {
        var node_x = $('#in_device_column').outerWidth() + $('#in_device_column').position().left;
        var node_y = feature_node.position().top + feature_node.outerHeight()/2 + $('#in_device_column').position().top;
    }
    else if (feature_node.parents().filter('.device-obj').parent().attr('id') == 'out_device_column') {
        var node_x = $('#out_device_column').position().left;
        var node_y = feature_node.position().top + feature_node.outerHeight()/2 + $('#out_device_column').position().top;
    }
    return [node_x, node_y];
}

function count_circle_coordinate(circle ) {
    var map_block_top = $($('div.map-block').get(0)).children().find('img').position().top;
    var map_column_top = $('div.map-column').position().top;
    var map_block_image_half_top = 20/2;
    var first_map_block  = map_column_top + map_block_top + map_block_image_half_top;
    var circle_y = first_map_block + 45* parseInt(circle.attr('name'));
    var circle_x = $('.map-column').position().left + $('.map-column').width() / 2;
    return [circle_x, circle_y];
}

function draw_line(start_x, start_y, end_x, end_y, color) {
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineCap = 'round';
    ctx.shadowBlur = 1;
    ctx.shadowColor = color;
    ctx.lineWidth = 1.5;
    ctx.moveTo(start_x, start_y);
    ctx.lineTo(end_x, end_y);
    ctx.stroke();
}

function save_idf_default_event_handler() {
    $('.idf_setting_save').unbind('click');
    $('.idf_setting_save').on('click', function(e) {
        var setting_list = {'dfo_id':'', 'df_info':[]};

        var idf_outer = $('.div-idf-outer');
        var idf_col_left = $(idf_outer).children()[0];
        var idf_col_right = $(idf_outer).children()[1];

        // idf_fn_id
        idf_fn_id = $(idf_col_right).find('option:selected').attr('name');

        var idf_num = $(idf_col_left).find('option:selected').length;
        // get idf info
        for (i=0; i< idf_num ;i++) {
            setting_list['df_info'].push([
                $($($(idf_col_left).find('option:selected'))[i]).val(),
                $($($(idf_col_right).find('.div-idf-tab-normal-left > input'))[i]).val(),
                $($($(idf_col_right).find('.div-idf-tab-normal-right > input'))[i]).val(),
                idf_fn_id]
            ); 
        } 

        setting_list['dfo_id'] = $(idf_col_left).find('.div-idf-tab-title-left > label').attr('name');
        setting_list['alias_name'] = $('.div-idf-tab-title-left').find('.label-idf').text()

        ajax_save_feature_default(setting_list); 
        show_save_gif (".idf_setting_save", 'save-gif-single-idf');
        reload_all_data();
    });
}

function save_odf_default_event_handler() {
    $('.odf_setting_save').unbind('click');
    $('.odf_setting_save').on('click', function(e) {
        var setting_list = {'dfo_id':'', 'df_info':[]};

        // get odf info
        odf_col_right = $('.div-odf-outer').children()[1];
        odf_num = $(odf_col_right).find('option:selected').length;
        for (i=0; i< odf_num ;i++) {
            setting_list['df_info'].push([
                "sample",
                $($(odf_col_right).find('.div-odf-tab-normal-left > input')[i]).val(),
                $($(odf_col_right).find('.div-odf-tab-normal-right > input')[i]).val(),
                $($(odf_col_right).find('option:selected')[i]).attr('name')]
            );
        }

        // get odf dfo id
        odf_col_left = $('.div-odf-outer').children()[0];
        setting_list['dfo_id'] = $(odf_col_left).find('.div-odf-first-tab-title > label').attr('name');
        setting_list['alias_name'] = $('.div-odf-first-tab-title').find('.label-odf').text();
        ajax_save_feature_default(setting_list); 
        show_save_gif (".odf_setting_save", 'save-gif-single-odf');
        reload_all_data();
    });
}

function show_save_gif (after_object, id='save-gif') {
    $('#'+id).remove()
    var img = $('<img>', { 
        'src': '/static/images/save.gif', 
        'id': id,
        'class': 'save_image', 
        'style':'float:right; height:25px;margin-right: 5px; margin-top: 6px;' 
    });
    $(img).insertAfter(after_object);
    $(img).fadeIn(300).delay(500).fadeOut(500);
}
