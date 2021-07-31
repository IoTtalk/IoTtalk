function init(){
    $.ajaxSetup({
        async: false,
        cache: false,
        dataType: 'html',
        error: function( jqXHR, error, responseText){
            alert ( "[ "+ this.url +" ] Can't do because: " + responseText );
        },
    });

    var window_height = window.innerHeight-$('nav').height()-2;
    $('html').css('height', window_height);
    $('#connect_block').css('height', window_height);
    $('#work_area').css('height', window_height);

    create_new_feature_without_detail();
    bind_switch_mode();
    bind_click_category();
}

function bind_switch_mode(){
    $('#dm_df_switch').unbind();
    $('#dm_df_switch').on('click', function(e){
        $('#df_window_outer').empty();
        $('#dm_window_outer').empty();

        if ($('#dm_df_switch a').text() == 'Device Feature'){
            $('#dm_df_switch a').text('Device Model');
            create_new_model();
        } else {
            $('#dm_df_switch a').text('Device Feature');
            create_new_feature_without_detail();
        }
    });
}

function bind_click_category(){
    $('.menu > .category').unbind();
    $('.menu > .category').on('click', function(e){
        var target_window = $('#dm_df_switch').find('a').text();

        if (target_window == 'Device Feature'){
            var df_category = $(this).find('a').text();
            var df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

            if ($('.div-dfc-range-setting').length == 0){   // df window 的初始畫面
                refresh_feature_list(df_category, df_type);
                $('#df_window_outer .label-dfc').next().text(df_category);
            } else {
                create_new_feature(df_category, df_type);
            }
        }
    });
}

// ======================== feature management ========================
function refresh_feature_list (df_category, df_type) {
    var target_select = $('#df_window_outer .name-select'); 
    target_select.empty();
    target_select.append($('<option>', { 'text': 'add new DF' }));

    var feature_list = ajax_get_category_feature(df_category);
    $.each( feature_list[df_type.toLowerCase()], function( index, value ) {
        target_select.append($('<option>', { 'text': value[0] }));
    });
}

function create_new_feature_without_detail(){
    var df_info = ajax_get_feature_info('');
    var df_category = df_info['df_category'];

    var df_type;
    if (df_info['df_type'] == 'input') {
        df_type = 'IDF';
    }
    else {
        df_type = 'ODF';
    }

    var df_list = ['add new DF'];
    var feature_list = ajax_get_category_feature(df_category);
    $.each( feature_list[df_type.toLowerCase()], function (index, value) {
        df_list.push(value[0]);
    });

    var admin_left_body = make_feature_management_html_without_detail(df_category, df_list);

    var df_window = $('#df_window_outer');
    df_window.empty();
    df_window.append(admin_left_body);
    
    $('#df_window_outer .labe-dfc-df-type input[id="'+df_type+'"]').prop('checked', true);
    $('#df_window_outer .name-select option:selected').prop('selected', false);

    var target_select = $('#df_window_outer .name-select');
    $('.name-select').attr('size','4');

    bind_select_feature();
    bind_change_feature_type();

    //show feature upload download
    /*
    //download all feature
    let download_li = $('<li/>', {'id': 'df_download', 'style': 'float:right',});
    download_li.append($('<a/>', {'style': 'color:black', 'text': 'download'}));
    $('.menu').append(download_li);
    $('#df_download').bind('click', function () {
        console.log('download');
        var result = ajax_download_feature();
        location.reload();
    });
    */

    //upload all feature
    let upload_li = $('<li/>', {'id': 'df_upload', 'style': 'float:right',});
    upload_li.append($('<a/>', {'style': 'color:black', 'text': 'upload'}));
    $('.menu').append(upload_li);
    $('#df_upload').bind('click', function () {
        let username = 'yb';

        //input username, cancel by yb
        /*
        while (true) {
            username = prompt("Please enter your name.")
            if (!username) {
                return;
            }

            if (username.trim() == "") {
                alert('invalid name');
                continue;
            }
            break;
        }
        */

        let result = ajax_upload_feature(username);
        if (result['status'] == 'ok') {
            alert('upload success');
        }
        else {
            alert('upload fail\n'+result['message']);
        } 
    });
}

function create_new_feature (df_category, df_type, df_name='') {
    var feature_list = ajax_get_category_feature(df_category);
    var df_list = ['add new DF'];
    $.each( feature_list[df_type.toLowerCase()], function( index, value ) {
        df_list.push(value[0]);
    });

    var df_info;
    if (df_list.length == 1 || df_name == 'add new DF') {
        df_info = ajax_get_feature_info('');
    }
    else {
        if (!df_name) {
            df_name = df_list[1];
        }
        df_info = ajax_get_feature_info(df_name);
    }

    var admin_left_body = make_feature_management_html(df_category, df_list, df_info);

    var df_window = $('#df_window_outer');
    df_window.empty();
    df_window.append(admin_left_body);

    $('#df_window_outer .labe-dfc-df-type input[id="'+df_type+'"]').prop('checked', true)
    $('#df_window_outer .name-select > option').filter(function(index) { return $(this).text() == df_name; }).prop('selected', true);

    bind_save_device_feature();
    bind_delete_device_feature();
    bind_upload_device_feature();
    bind_change_parameter_number();
    bind_change_unit();
    bind_select_feature();
    bind_change_feature_type();
    show_feature_comment(df_info['df_comment']);
}

function bind_change_feature_type () {
    $('#df_window_outer .labe-dfc-df-type input:radio').unbind();
    $('#df_window_outer .labe-dfc-df-type input:radio').change(function(){
        var df_category = $('#df_window_outer .label-dfc').next().text();
        var df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

        if ($('.div-dfc-range-setting').length == 0){   // df window 的初始畫面
            refresh_feature_list(df_category, df_type);
        } else {
            create_new_feature(df_category, df_type);
        }
    });
}

function bind_select_feature(){
    $( "#df_window_outer .name-select" ).change(function() {
        var feature_name = $(this).find('option:selected').text();
        var df_category = $('#df_window_outer #df_type span').text(); 
        var df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

        if (feature_name == 'add new DF'){
            create_new_feature(df_category, df_type, feature_name);
        }else{
            create_new_feature(df_category, df_type, feature_name);
        }
    });
}

function bind_save_device_feature(){

    $('.input-dfc-save-button').unbind('click');
    $('.input-dfc-save-button').on('click', function(e){
        let df_name = $('#df_window_outer .name-select option:selected').text();
		var new_df_name;
        while (true) {
            new_df_name = prompt("The device feature name: ", df_name);
            if (!new_df_name) {
                return;
            }
            else if (new_df_name.trim() == "" || new_df_name == "add new DF") {
                alert("invalid name");
                continue;
            }

            let return_value = ajax_check_device_feature_name_is_exist(new_df_name);
            if (return_value == '1'){
			    if (!confirm('The feature name exists.\nDo you want to replace it?')){
				    continue;
			    }
		    }
            break;
        }

        let df_comment = $('.input-dfc-comment').val();
        let df_category = $('#df_window_outer #df_type span').text(); 
        let df_type = $('#df_window_outer #df_type input:checked').attr('id'); 
        let type = [];
        $('.div-dfc-range-column-type').find('select option:selected').each(function( index ) {
            type.push($(this).text());
        });

        let min = []
        $('.div-dfc-range-column-min').find('input').each(function( index ) {
            min.push($(this).val());
        });

        let max = []
        $('.div-dfc-range-column-max').find('input').each(function( index ) {
            max.push($(this).val());
        });

        let unit = []
        $('.div-dfc-range-column-unit').find('select option:selected').each(function( index ) {
            unit.push(parseInt($(this).attr('value')));
        });

        let feature_info = {
            'df_name':new_df_name, 
            'df_comment':df_comment, 
            'df_category':df_category, 
            'df_type':df_type, 
            'type':type, 
            'min':min, 
            'max':max,
            'unit':unit,
        };

        show_save_gif(".input-dfc-save-button");
		let return_value = ajax_save_device_feature(feature_info);
        if (return_value == '1'){
            alert('This feature is allready in use.');
        }
        reload_exist_feature();
        $('#df_window_outer .name-select option:contains("'+new_df_name+'")').prop('selected', true);
    });
}

function reload_exist_feature(){

    var df_category = $('#df_window_outer #df_type span').text(); 
    var feature_list = ajax_get_category_feature(df_category);
    var df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

    var selected_one = $('#df_window_outer .name-select option:selected').text();
    var target_select = $('#df_window_outer .name-select'); 
    target_select.empty();
    var df_list = ['add new DF'];
    if (df_type == 'IDF'){
        $('<option>', { 'text': 'add new DF' }).appendTo(target_select);
        $.each( feature_list['idf'], function( index, value ) {
            $('<option>', { 'text': value[0] }).appendTo(target_select);
            df_list.push(value[0]);
        });
    } else if (df_type == 'ODF'){
        $('<option>', { 'text': 'add new DF' }).appendTo(target_select);
        $.each( feature_list['odf'], function( index, value ) {
            $('<option>', { 'text': value[0] }).appendTo(target_select);
            df_list.push(value[0]);
        });
    }

    target_select.find('option:contains('+selected_one+')').prop('selected', true);
}

function bind_delete_device_feature(){
    $('.input-dfc-delete-button').unbind('click');
    $('.input-dfc-delete-button').on('click', function(e){
        var df_name = $('#df_window_outer .name-select option:selected').text();
        var return_value = ajax_delete_device_feature(df_name);
        if (return_value == '1'){
            alert('This feature is already in use.');
        } else {
            var df_category = $('#df_window_outer #df_type span').text(); 
            var df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

            create_new_feature(df_category, df_type);
        }
    });
}
function bind_upload_device_feature() {
    $('.input-dfc-upload-button').unbind('click');
    $('.input-dfc-upload-button').on('click', function(e){
        let df_id = $(this).attr('df_id');
        let username = 'yb';

        //input username, cancel by yb
        /*
        while (true) {
            username = prompt("Please enter your name.")
            if (!username) {
                return;
            }

            if (username.trim() == "") {
                alert('invalid name');
                continue;
            }
            break;
        }
        */

        let result = ajax_upload_feature(username, df_id);
        if (result['status'] == 'ok') {
            alert('upload success');
        }
        else {
            alert('upload fail\n'+result['message']);
        }
    });
}

function bind_change_parameter_number(){
    
    $('.input-dfc-df-number').change(function() {

        var para_length = parseInt($('.input-dfc-df-number').val());
        if (para_length > 0){

            $('.div-dfc-range-setting').empty();
            var range_setting = $('.div-dfc-range-setting');
            var type_column = $('<div>', { 'class': 'div-dfc-range-column-type', });
            var column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
            $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Type', }).appendTo(column_title);
            column_title.appendTo(type_column);

            //repeat
            var df_type_list = ajax_get_type_list();
            for( var index=0;index<para_length;index++){
                var setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 'style':'border-style:solid;border-width:1px'});
                var type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none; height:23px'});
                $.each( df_type_list, function( index, parameter_type ) {
                    $('<option>', { 'text': parameter_type }).appendTo(type_selection);
                });
                type_selection.appendTo(setting_list);
                setting_list.appendTo(type_column);    
                type_column.appendTo(range_setting);
            };
            //end
            

            var range_column = $('<div>', { 'class': 'div-dfc-range-column-min', });
            column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
            $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Min', }).appendTo(column_title);
            column_title.appendTo(range_column);
            setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
            //repeat
            for( var index=0;index<para_length;index++){
                $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': '0', }).appendTo(setting_list);
            };
            //end
            setting_list.appendTo(range_column);
            range_column.appendTo(range_setting);


            range_column = $('<div>', { 'class': 'div-dfc-range-column-max', });
            column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
            $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Max', }).appendTo(column_title);
            column_title.appendTo(range_column);
            setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
            //repeat
            for( var index=0;index<para_length;index++){
                $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': '0', }).appendTo(setting_list);
            }
            //end
            setting_list.appendTo(range_column);
            range_column.appendTo(range_setting);

            // Unit start
            range_column = $('<div>', { 'class': 'div-dfc-range-column-unit', });
            column_title = $('<div>', { 'class': 'div-dfc-range-column-title', 'style':'border-right-width:1px'});
            $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Unit',}).appendTo(column_title);
            column_title.appendTo(range_column);

            // repeat
            for( var index=0;index<para_length;index++){    
                setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 
                                        'style':'border-right-width:1px; border-style:solid;border-width:1px;'});
                type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none;height:23px'});
                //$('<option>', { 'text': 'm/s', }).appendTo(type_selection);
                type_selection.appendTo(setting_list);
                setting_list.appendTo(range_column);
                refresh_unit_list(type_selection);
            }
            range_column.appendTo(range_setting);
            // Unit end

        } else {
            alert('Parameter length type error, can\'t be zero or string.');
        }
    });
}


// ======================== model management ========================

function create_new_model(){
    $('#df_download').remove();
    $('#df_upload').remove();

    $('#df_window_outer').empty();
    $('#dm_window_outer').empty();

    var model_list = ajax_get_model_list();
    model_list.unshift('add new DM');

    var outer_block = make_model_setting_html2(model_list)
    $('#dm_window_outer').append(outer_block);

    $('.name-select').attr('size', '4');
    $('.name-select').find(':selected').prop('selected', false);

    bind_change_model();
}

function bind_change_model(){
    $( "#dm_window_outer .name-select" ).change(function() {
        $('#df_window_outer').empty();
        $('#dm_window_outer').empty();
        var model_name = $(this).find('option:selected').text();

        if (model_name == 'add new DM'){
            // 畫出 model creation 畫面
            var json = ajax_get_model_feature('');
            var model_list = ajax_get_model_list();
            model_list.unshift('add new DM');
            var category_list = ajax_get_category_list();
            var outer_block = make_model_setting_html(json, model_list, category_list['idf_category']);
            outer_block.appendTo('#dm_window_outer');

            // 顯示目前選到 category 的 feature list
            var idf_category = $('.idf-category-select').find('option:selected').text();
            var idf_feature_list = ajax_get_category_feature(idf_category);
            var category_list = ajax_get_category_list();

            $('#df_setting_block').remove();
            var idf_outer_block = make_model_df_setting('idf', idf_feature_list, category_list['idf_category']);
            $('#model_save').before(idf_outer_block);

            bind_change_category();
            bind_save_device_model( $('#name-input').val(), '0');
            bind_delete_device_model('0');
            bind_model_change_feature();
            bind_change_df_type();
            bind_change_model();
        }else{
            var json = ajax_get_model_feature(model_name);
            var model_list = ajax_get_model_list();
            model_list.unshift('add new DM');
            var category_list = ajax_get_category_list();
            var outer_block = make_model_setting_html(json, model_list, category_list['idf_category']);
            outer_block.appendTo('#dm_window_outer');
            $('.name-select').val(json['model_name']);

            // 顯示目前選到 category 的 feature list
            var idf_category = $('.idf-category-select').find('option:selected').text();
            var idf_feature_list = ajax_get_category_feature(idf_category);
            var category_list = ajax_get_category_list();
            $('#df_setting_block').remove();
            var idf_outer_block = make_model_df_setting('idf', idf_feature_list, category_list['idf_category']);
            $('#model_save').before(idf_outer_block);
 
            bind_change_category();
            bind_save_device_model( $('#name-input').val(), json['model_id']);
            bind_delete_device_model( json['model_id']);
            bind_model_change_feature();
            bind_select_model_feature();
            bind_change_df_type();
            bind_change_model();

            $('#name-input').val(json['model_name']);
            $('input:radio[id='+json['model_type']+']').attr('checked','checked')
        }
    });
}

function change_feature_list(df_category, df_type){
    $('#df_setting_block').remove();
    $('#df_window_outer').empty();

    var feature_list = ajax_get_category_feature(df_category);
    var category_list = ajax_get_category_list();
    if (df_type == 'input'){
        var df_outer_block = make_model_df_setting('idf', feature_list, category_list['idf_category'], df_category);
    } else{
        var df_outer_block = make_model_df_setting('odf', feature_list, category_list['odf_category'], df_category);
    }
    $('#model_save').before(df_outer_block);
    bind_model_change_feature();
    bind_change_category();
    bind_change_df_type();
}

function bind_change_df_type(){
    $('#dm_window_outer .labe-dfc-df-type input').change(function(){
        var df_type = $(this).attr('id');
        var category_list = ajax_get_category_list();

        if (df_type == 'IDF'){
            var df_category = category_list['idf_category'][0];
            change_feature_list(df_category, 'input');
        } else {
            var df_category = category_list['odf_category'][0];
            change_feature_list(df_category, 'output');
        }
    });
}

function bind_select_model_feature(){
    $('.selected-odf > label').unbind();
    $('.selected-odf > label').on('click', function (){
        var df_name = $(this).text();
        var df_id = $(this).attr('id');
        var df_category = ajax_get_category_by_df_name(df_name);

        change_feature_list(df_category, 'output');
        show_model_feature_info(df_name, df_id);
    });

    $('.selected-idf > label').unbind();
    $('.selected-idf > label').on('click', function (){
        var df_name = $(this).text();
        var df_id = $(this).attr('id');
        var df_category = ajax_get_category_by_df_name(df_name);

        change_feature_list(df_category, 'input');
        show_model_feature_info(df_name, df_id);
    });

}

function bind_change_category(){
    $( ".idf-category-select" ).change(function() {
        var df_category = $(this).find('option:selected').text();
        change_feature_list(df_category, 'input');
    });

    $( ".odf-category-select" ).change(function() {
        var df_category = $(this).find('option:selected').text();
        change_feature_list(df_category, 'output');
    });

}

function bind_delete_device_model(dm_id){
    $('#model_delete').unbind('click');
    $('#model_delete').on('click', function(e){
        var return_value = ajax_delete_device_model(dm_id);
        if (return_value == '1'){
            alert('This model is already in use..');
        } else {
            create_new_model(); 
        }
    });
}

function bind_save_device_model(model_name, dm_id){

    $('#model_save').unbind('click');
    $('#model_save').on('click', function(e){            
        var dm_name = $('#dm_window_outer .name-select option:selected').text();
        var new_dm_name;

        while (true) {
            new_dm_name = prompt("The device model name: ", dm_name);

            if (!new_dm_name) {
                return;
            }
            else if (new_dm_name.trim() == "" || new_dm_name == "add new DM") {
                alert("invalid name");
                continue;
            }

            var return_info = ajax_check_device_model_name_is_exist(new_dm_name);
            if (return_info == '1') {
                if (!confirm('The model name exists.\nDo you want to replace it?')) {
				    continue;
                }
            }
            break;
        }

        // make model info
        var feature_list = {'idf_list':[], 'odf_list':[]};
        
        $('.selected-idf').find('label').each(function(){
            feature_list['idf_list'].push([$(this).text(), $(this).attr('id')]);
        });

        $('.selected-odf').find('label').each(function(){
            feature_list['odf_list'].push([$(this).text(), $(this).attr('id')]);
        });

        feature_list['dm_name'] = new_dm_name; 
        feature_list['dm_id'] = $('#model_save').attr('class');
        feature_list['dm_type'] = 'other'; 
        /*
            feature_list = {
                'odf_list': [[df_name, df_id], ...], 
                'idf_list': [[df_name, df_id], ...], 
                'dm_name': dm_name,
                'dm_id': dm_id,
                'dm_type': dm_type,
            }
        */

        // call ajax to save
        show_save_gif(".input-dfc-save-button");
        var return_info = ajax_save_device_model(feature_list);
        if (return_info['save_status'] == '1'){
            alert('This model is already in use!');
        }
        $('#model_save').attr('class', return_info['dm_id']);
        
        reload_exist_model();
        $('#dm_window_outer .name-select option:contains('+new_dm_name+')').prop('selected', true);
    });
}

function reload_exist_model(){
    var model_list = ajax_get_model_list();
    var target_select = $('#dm_window_outer .name-select'); 
    target_select.empty();
    $('<option>', { 'text': 'add new DM' }).appendTo(target_select);
    $.each( model_list, function( index, value ) {
        $('<option>', { 'text': value }).appendTo(target_select);
    });

    bind_change_model();    
}

function bind_model_change_feature(){
    $('input:checkbox').unbind();
    $('input:checkbox').click(function() {
        var feature_name = $(this).parent().text();
        var feature_id = $(this).parent().attr('id');

        if ($(this).is(':checked')) {
            // selected
            if ($(this).attr('class') == 'idf-input'){
                $('<label>', { 'id':feature_id, 'text': feature_name, 'class':'feature-margin', }).appendTo($('.selected-idf'));
                $('<br>').appendTo($('.selected-idf'));
            } else {
                $('<label>', { 'id':feature_id, 'text': feature_name, 'class':'feature-margin', }).appendTo($('.selected-odf'));
                $('<br>').appendTo($('.selected-odf'));
            }
            bind_select_model_feature();
            bind_model_change_feature();
            show_model_feature_info(feature_name, feature_id);
        } else {
            //removed
            $('#df_window_outer').empty();
            if ($(this).attr('class') == 'idf-input'){
                var target = $('.selected-idf').find('label[id='+feature_id+']');
                target.next().remove();
                target.remove();
            } else {
                var target = $('.selected-odf').find('label[id='+feature_id+']');
                target.next().remove();
                target.remove();
            }
        }
    });
}

function show_model_feature_info(feature_name, feature_id){
    var dm_id = $('#model_save').attr('class');
    var df_info = ajax_get_device_feature_info(feature_name, dm_id);

    var feature_creation_block = make_model_feature_management_html(df_info, feature_id, feature_name);

    $('#df_window_outer').empty();
    feature_creation_block.appendTo($('#df_window_outer'));

    bind_save_model_feature();
    bind_change_unit();
}

function bind_save_model_feature(){
    $('.input-dfc-save-button').unbind('click');
    $('.input-dfc-save-button').on('click', function(e){

        var dm_id = $('#model_save').attr('class');
        var df_id = $('.input-dfc-save-button').attr('id'); 

        type = [];
        $('.div-dfc-range-column-type').find('select option:selected').each(function( index ) {
            type.push($(this).text());
        });

        min = []
        $('.div-dfc-range-column-min').find('input').each(function( index ) {
            min.push($(this).val());
        });

        max = []
        $('.div-dfc-range-column-max').find('input').each(function( index ) {
            max.push($(this).val());
        });

        unit = []
        $('.div-dfc-range-column-unit').find('select option:selected').each(function () {
            unit.push(parseInt($(this).attr('value')));
        }); 

        var feature_info = {'dm_id':dm_id, 'df_id':df_id, 'type':type, 'min':min, 'max':max, 'unit':unit };

        show_save_gif(".input-dfc-save-button");
        var return_value = ajax_save_model_feature_info(feature_info);
        if (return_value == '1') {
            alert('This model is already in use..');
        }
    });
}

//======================================================= ksoy add

function refresh_unit_list (select, unit_id) {
    select.innerHTML = '';

    var unit_list = ajax_get_unit_list();
    unit_list.forEach(function (unit) {
        if (unit_id && unit.unit_id == unit_id){
            $(select).append($('<option>', { 'text': unit.unit_name, 'value': unit.unit_id, 'selected': 'selected'}));
        }
        else {
            $(select).append($('<option>', { 'text': unit.unit_name, 'value': unit.unit_id }));
        }
    })

    $(select).append($('<option>', { 'text': 'add new unit', 'value': 0 }));
}

function bind_change_unit () {
    $('.div-dfc-range-column-unit').find('select').unbind();
    $('.div-dfc-range-column-unit').find('select').on('change', function(e){
        if ($(this).find(':selected').attr('value') == '0') {

            //input the new unit name
            var new_unit_name = "";
            while (true) {
                new_unit_name = prompt("Please enter new unie name: ");
                if (!new_unit_name) {
                    return;
                }
                else if (new_unit_name == "add new unit" || !new_unit_name.trim()) {
                    alert('invalid unit name');
                }
                else {
                    break;
                }
            }

            //send add request
            var result = ajax_add_unit(new_unit_name);
            unit_id = result['unit_id'];

            //refresh unit list
            $('.div-dfc-range-column-unit').find('select').each(function (index, object) {
                let pre_id = $(object).find(':selected').attr('value');
                if (pre_id == 0) {
                    refresh_unit_list(object, unit_id);
                }
                else {
                    refresh_unit_list(object, pre_id);
                }
            });       
        }
    });
}

function show_save_gif (unit_name) {
    $('#save-gif').remove();
    var img = $('<img>', { 
        'src': '/static/images/save.gif', 
        'class': 'save_image',
        'id': 'save-gif',
        'style':'height:25px;margin-right: 4px; margin-top: 1px;' 
    });

    $(img).insertAfter(unit_name);
    $(img).fadeIn(300).delay(500).fadeOut(500);
}

function show_feature_comment (comment) {
    $('#dm_window_outer').empty()
    let div = $('<div/>', {'class': 'div-df-comment'});
    div.append($('<label>', {'class': 'label-df-comment', 'text': 'Description'}));
    div.append($('<br/>'));
    div.append($('<textarea>', {'class': 'input-dfc-comment', 'value':comment, 'text':comment}));

    div.appendTo($('#dm_window_outer'));
}
