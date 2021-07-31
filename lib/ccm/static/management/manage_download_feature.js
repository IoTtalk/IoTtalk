let key = 'bloothentminsteryinowste';//'zysomentionsuroppostreye';
let pass = 'a5ceb5c190f71f9f79a080ac4cdcfaa5306316d3';//'917cd9025d2b18056cd0d61657f65fc372e33d25';
let mdb_url = "https://iottalk.cloudant.com/device_feature/";
let query = '_all_docs?include_docs=true&conflicts=true';
var df_data = null;

function init(){
    $.ajaxSetup({
        async: false,
        cache: false,
        dataType: 'html',
        error: function( jqXHR, error, responseText){
            alert ( "[ "+ this.url +" ] Can't do because: " + responseText );
        },
    });

    let window_height = window.innerHeight-$('nav').height()-2;
    $('html').css('height', window_height);
    $('#connect_block').css('height', window_height);
    $('#work_area').css('height', window_height);

    reload_mdb_data();

    let df_type = Object.keys(df_data)[0];
    let df_category = Object.keys(df_data[df_type])[0];
    create_new_feature_without_detail(df_type, df_category);
    bind_click_category();
}

function reload_mdb_data (callBack) {
    let ajax_obj = $.ajax({
        url: mdb_url + query,
        type: 'GET',
        beforeSend: function (xhr) {
            $('#loading').show();
            xhr.setRequestHeader ("Authorization", "Basic " + btoa(key + ":" + pass));
        },
        complete: function () {
            $('#loading').hide();
        }
    });

    let mdb_data = $.parseJSON(ajax_obj.responseText);
    df_data = parse_mdb_data(mdb_data);
}

function parse_mdb_data (mdb_data) {
    let data = {'idf': {}, 'odf': {}};

    let category_list = ajax_get_all_category();
    category_list.forEach(function (category, index) {
        data['idf'][category] = {};
        data['odf'][category] = {};
    }); 

    //check all documents
    mdb_data['rows'].forEach(function (doc, index) {
        let doc_id = doc['doc']['_id'];

        //filter self upload
        //if (doc_id == mdb_id) { return; }
        
        //check all features
        doc['doc']['device_feature'].forEach(function (df, index) {
            let type = (df['type'] == 'input') ? ('idf') : ('odf');
            let category = df['category'];
            let df_name = df['name'];
            let count = 1;

            if (!data[type][category]) {
                return;
            }

            //check duplicate name
            while (true) {
                if (!data[type][category][df_name + ' -' + String(count)]) {
                    break;
                }
                count += 1;
            }

            data[type][category][df_name + ' -' + String(count)] = df;
        });
    });

    return data;
}

function refresh_feature_list (df_category, df_type) {
    let target_select = $('#df_window_outer .name-select'); 
    target_select.empty();

    df_type = df_type.toLowerCase();

    if (!df_data[df_type] || !df_data[df_type][df_category]) {
        return;
    }

    for (let key in df_data[df_type.toLowerCase()][df_category]) {
        let df_name = df_data[df_type.toLowerCase()][df_category][key]['name'];
        target_select.append($('<option>', { 'text': df_name } ));
    }
    $('#df_window_outer .name-select option:selected').prop('selected', false);
}

function create_new_feature_without_detail(df_type, df_category){
    let df_list = [];

    for (let key in df_data[df_type.toLowerCase()][df_category]) {
        df_list.push(key);
    }

    let admin_left_body = make_feature_management_html_without_detail(df_category, df_list);

    $('#dm_window_outer').empty();
    let df_window = $('#df_window_outer');
    df_window.empty();
    df_window.append(admin_left_body);

    let target_select = $('#df_window_outer .name-select');
    $('.name-select').attr('size','4');
    
    $('#df_window_outer .labe-dfc-df-type input[id="'+df_type.toUpperCase()+'"]').prop('checked', true);
    $('#df_window_outer .name-select option:selected').prop('selected', false);

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
        let result = ajax_download_feature();
        location.reload();
    });
    */
}

function create_new_feature (df_type, df_category, df_name) {
    let df_info = df_data[df_type.toLowerCase()][df_category][df_name];
    let df_list = [];
    for (let key in df_data[df_type.toLowerCase()][df_category]) {
        df_list.push(key);
    }

    let admin_left_body = make_feature_management_html(df_category, df_list, df_info);

    let df_window = $('#df_window_outer');
    df_window.empty();
    df_window.append(admin_left_body);

    $('#df_window_outer .labe-dfc-df-type input[id="'+df_type+'"]').prop('checked', true)
    $('#df_window_outer .name-select > option').filter(function(index) { return $(this).text() == df_name; }).prop('selected', true);

    show_feature_comment(df_info['description']);

    bind_select_feature();
    bind_change_feature_type();
    bind_download_feature();
}

function bind_click_category(){
    $('.menu > .category').unbind();
    $('.menu > .category').on('click', function(e){
        let df_category = $(this).find('a').text();
        let df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

        create_new_feature_without_detail(df_type, df_category)
    });
}

function bind_change_feature_type () {
    $('#df_window_outer .labe-dfc-df-type input:radio').unbind();
    $('#df_window_outer .labe-dfc-df-type input:radio').change(function(){
        let df_category = $('#df_window_outer .label-dfc').next().text();
        let df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

        create_new_feature_without_detail(df_type, df_category);
    });
}

function bind_select_feature(){
    $( "#df_window_outer .name-select" ).change(function() {
        let df_name = $(this).find('option:selected').text();
        let df_category = $('#df_window_outer #df_type span').text(); 
        let df_type = $('#df_window_outer .labe-dfc-df-type input:checked').attr('id');

        create_new_feature(df_type, df_category, df_name);
    });
}

function bind_download_feature () {
    $('.input-dfc-download-button').unbind('click');
    $('.input-dfc-download-button').on('click', function(e){
        let df_name = $('#df_window_outer .name-select option:selected').text();
        let df_category = $('#df_window_outer #df_type span').text(); 
        let df_type = $('#df_window_outer #df_type input:checked').attr('id'); 
        let df_info = df_data[df_type.toLowerCase()][df_category][df_name];
        show_save_gif(".input-dfc-download-button");
        let resp = ajax_save_download_feature(df_info);
        if (resp['status'] == 'ok') {
            alert('download success');
        }
        else {
            alert(resp['msg']);
        }
    });
}

function show_save_gif (unit_name) {
    $('#save-gif').remove();
    let img = $('<img>', { 
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
    div.append($('<textarea>', {'class': 'input-dfc-comment', 'value':comment, 'text':comment, 'readonly': true}));

    div.appendTo($('#dm_window_outer'));
}

function ajax_get_all_category () {
    var ajax_obj = $.ajax({
        url: '/get_all_category',
        type:'POST',
    });

    var category_list = $.parseJSON(ajax_obj.responseText);
    return category_list;
}

function ajax_save_download_feature (df_info) {
    df_info = JSON.stringify(df_info);
    var ajax_obj = $.ajax({
        url: '/save_download_feature',
        type:'POST',
        data: {df_info: df_info},
    });

    var category_list = $.parseJSON(ajax_obj.responseText);
    return category_list;
}
