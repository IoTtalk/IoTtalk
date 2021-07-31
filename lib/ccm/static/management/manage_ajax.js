function ajax_get_device_feature_list(){
    var ajax_obj = $.ajax({
        url: '/get_device_feature_list',
        type:'POST',
    });

    var df_list = $.parseJSON(ajax_obj.responseText);
    return df_list;
}

function ajax_get_type_list(){
    var ajax_obj = $.ajax({
        url: '/get_type_list',
        type:'POST',
    });

    var type_list = $.parseJSON(ajax_obj.responseText);
    return type_list;
}

function ajax_delete_device_feature(df_name){
    var ajax_obj = $.ajax({
        url: '/delete_device_feature',
        type:'POST',
        data: {df_name:df_name},
    });

    var return_value = ajax_obj.responseText;
    return return_value;
}


function ajax_get_feature_info(feature_name){
    var ajax_obj = $.ajax({
        url: '/get_feature_info',
        type:'POST',
        data: {feature_name:feature_name},
    });

    var df_info = $.parseJSON(ajax_obj.responseText);
    return df_info;
}

function ajax_get_category_by_df_name(df_name){
    var ajax_obj = $.ajax({
        url: '/get_category_by_df_name',
        type:'POST',
        data: {df_name:df_name},
    });

    var df_category = ajax_obj.responseText;
    return df_category;
}

function ajax_get_model_feature(dm_name){
    var ajax_obj = $.ajax({
        url: '/get_model_feature',
        type:'POST',
        data: {dm_name:dm_name}
    });

    var json = $.parseJSON(ajax_obj.responseText);
    return json;
}

function ajax_get_category_list(){
    var ajax_obj = $.ajax({
        url: '/get_category_list',
        type:'POST',
    });

    var category_list = $.parseJSON(ajax_obj.responseText);
    return category_list;
}

function ajax_get_category_feature(df_category){
    var ajax_obj = $.ajax({
        url: '/get_category_feature',
        type:'POST',
        data: {df_category:df_category},
    });

    var feature_list = $.parseJSON(ajax_obj.responseText);
    return feature_list;
}

function ajax_check_device_model_name_is_exist(dm_name){
    var ajax_obj = $.ajax({
        url: '/check_device_model_name_is_exist',
        type:'POST',
        data: {dm_name: dm_name},
    });

    var return_info = $.parseJSON(ajax_obj.responseText);
    return return_info;
}

function ajax_save_device_model(feature_list){
    feature_list = JSON.stringify(feature_list);
    var ajax_obj = $.ajax({
        url: '/save_device_model',
        type:'POST',
        data: {feature_list:feature_list},
    });

    var return_info = $.parseJSON(ajax_obj.responseText);
    return return_info;
}

function ajax_delete_device_model(dm_id){
    var ajax_obj = $.ajax({
        url: '/delete_device_model',
        type:'POST',
        data: {dm_id:dm_id},
    });

    var return_info = ajax_obj.responseText;
    return return_info;
}

function ajax_get_model_list(){
    var ajax_obj = $.ajax({
        url: '/get_model_list',
        type:'POST',
    });
    //will return [["model_name",dm_id],....]
    var model_list = $.parseJSON(ajax_obj.responseText);
    for(var i = 0; i < model_list.length; i++)
        model_list[i] = model_list[i][0];
    return model_list;
}

function ajax_check_device_feature_name_is_exist(df_name){
	var ajax_obj = $.ajax({
		url: '/check_device_feature_name_is_exist',
		type: 'POST',
		data: {df_name: df_name}
	});

	var return_value = $.parseJSON(ajax_obj.responseText);
    return return_value;
}

function ajax_save_device_feature(feature_info){
    feature_info = JSON.stringify(feature_info);
    var ajax_obj = $.ajax({
        url: '/save_device_feature',
        type:'POST',
        data: {feature_info:feature_info},
    });

    var return_value = $.parseJSON(ajax_obj.responseText);
    return return_value;
}

function ajax_save_model_feature_info(feature_info){
    feature_info = JSON.stringify(feature_info);
    var ajax_obj = $.ajax({
        url: '/save_model_feature_info',
        type:'POST',
        data: {feature_info:feature_info},
    });

    var return_value = $.parseJSON(ajax_obj.responseText);
    return return_value;
}

function ajax_get_device_feature_info(feature_name, dm_id){
    var model_info = {'df_name':feature_name, 'dm_id':dm_id};
    model_info = JSON.stringify(model_info);
    var ajax_obj = $.ajax({
        url: '/get_device_feature_info',
        type:'POST',
        data: {model_info:model_info},
    });

    var df_info = $.parseJSON(ajax_obj.responseText);
    return df_info;
}

function ajax_get_unit_list() {
    var ajax_obj = $.ajax({
        url: '/get_unit_list',
        type: 'POST',
    });

    var unit_list = $.parseJSON(ajax_obj.responseText);
    return unit_list;
}

function ajax_add_unit(unit_name) {
    var ajax_obj = $.ajax({
        url: '/add_unit',
        type:'POST',
        data: {unit_name: unit_name},
    });

    var result = $.parseJSON(ajax_obj.responseText);
    return result;
}

function ajax_download_feature() {
    var ajax_obj = $.ajax({
        url: '/download_feature',
        type:'POST',
        data: {},
    });

    var result = $.parseJSON(ajax_obj.responseText);
    return result;
}

function ajax_upload_feature(username, df_id=null) {
    var ajax_obj = $.ajax({
        url: '/upload_feature',
        type:'POST',
        data: {
                username:username,
                df_id: df_id,
              },
    });

    var result = $.parseJSON(ajax_obj.responseText);
    return result;
}
