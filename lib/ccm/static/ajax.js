function ajax_turn_on_project(){
    $.ajax({
        url: '/turn_on_project',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_turn_off_project(){
    $.ajax({
        url: '/turn_off_project',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_turn_on_simulation(){
    $.ajax({
        url: '/turn_on_simulation',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_turn_off_simulation(){
    $.ajax({
        url: '/turn_off_simulation',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_restart_project(){
    $.ajax({
        url: '/restart_project',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_delete_function_info(fnvt_idx){
    $.ajax({
        url: '/delete_function_info',
        type:'POST',
        data: {fnvt_idx:fnvt_idx},
    });
}

function ajax_delete_all_temp_function(df_id){
    $.ajax({
        url: '/delete_all_temp_function',
        type:'POST',
        data:{df_id:df_id},
    });
}

function ajax_delete_connection_line(na_id){
     $.ajax({
        url: '/delete_connection_line',
        type:'POST',
        data: {na_id:na_id},
    });
}

function ajax_save_feature_default(setting_list){
    setting_list = JSON.stringify(setting_list);
    console.log(setting_list);

    $.ajax({
        url: '/save_feature_default',
        type:'POST',
        data: {setting_list:setting_list},
    });
}

function ajax_delete_device_object(do_id, p_id) {
    var recycle_info = {'do_id':do_id, 'p_id':p_id};
    recycle_info = JSON.stringify(recycle_info);
    $.ajax({
        url: '/delete_device_object',
        type:'POST',
        data: {recycle_info:recycle_info},
    });
}

function ajax_save_circle_connect_setting(na_idx, na_id, df_id){
    var connect_info = [ na_idx, na_id, df_id ];
    var circle_connect_info = {'connect_info':connect_info, 'p_id':p_id};
    circle_connect_info = JSON.stringify(circle_connect_info);

    $.ajax({
        url: '/save_circle_connect_setting',
        type:'POST',
        data: {circle_connect_info:circle_connect_info},
    });
}

function ajax_save_non_df_argument(non_df_argument, fnvt_idx){
    var argu_info = {'non_df_argument':non_df_argument, 'fnvt_idx':fnvt_idx };
    argu_info = JSON.stringify(argu_info);

    $.ajax({
        url: '/save_non_df_argument',
        type:'POST',
        data: {argu_info:argu_info},
    });
}

function ajax_push_user_input_data(dfo_id, data){
    var user_input = {'idfo_id':dfo_id, 'data':data};
    user_input = JSON.stringify(user_input);

    $.ajax({
        url: '/push_user_input_data',
        type:'POST',
        data: {user_input:user_input},
    });
}

function ajax_check_project_name_is_exist(project_name) {
    var ajax_obj = $.ajax({
        url: '/check_project_name_is_exist',
        type:'POST',
        data: {project_name:project_name},
    });
        
    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_function_is_switch(fn_id){
    var ajax_obj = $.ajax({
        url: '/check_function_is_switch',
        type:'POST',
        data: {fn_id:fn_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_monitor_info(na_id){
    var ajax_obj = $.ajax({
        url: '/get_monitor_info',
        type:'POST',
        data: {na_id:na_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_category_feature(df_category){
    var ajax_obj = $.ajax({
        url: '/get_category_feature',
        type:'POST',
        data: {df_category:df_category},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_model_feature(dm_name){
    var ajax_obj = $.ajax({
        url: '/get_model_feature',
        type:'POST',
        data: {dm_name:dm_name},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_select_project(p_id, p_pwd){
    var ajax_obj = $.ajax({
        url: '/connection_with_p_id_p_pwd',
        type:'POST',
        data: {p_id:p_id, p_pwd:p_pwd},
    });
    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_project_password_is_exist(p_id){
    var ajax_obj = $.ajax({
        url: '/check_project_password_is_exist',
        type:'POST',
        data: {p_id:p_id},
    });
    return $.parseJSON(ajax_obj.responseText);
}

function ajax_new_project(p_name, p_pwd){
    var ajax_obj = $.ajax({
        url: '/new_project',
        type:'POST',
        data: {p_name:p_name, p_pwd:p_pwd},
    });

    return ajax_obj.responseText;
}

function ajax_get_function_info(fn_id){
    var ajax_obj = $.ajax({
        url: '/get_function_info',
        type:'POST',
        data: {fn_id:fn_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_function_version_body(fnvt_idx){
    var ajax_obj = $.ajax({
        url: '/get_function_version_body',
        type:'POST',
        data: {fnvt_idx:fnvt_idx},
    });

    return ajax_obj.responseText;
}

function ajax_get_dfo_function_list(dfo_id){
    var ajax_obj = $.ajax({
        url: '/get_dfo_function_list',
        type:'POST',
        data: {dfo_id:dfo_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_function_is_used(fn_name){
    var ajax_obj = $.ajax({
        url: '/check_function_is_used',
        type:'POST',
        data: {fn_name:fn_name},
    });

    return ajax_obj.responseText;
}

function ajax_get_temp_function_list(dfo_id){
    var ajax_obj = $.ajax({
        url: '/get_temp_function_list',
        type:'POST',
        data:{dfo_id:dfo_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}
function ajax_get_project_list(){
    var ajax_obj = $.ajax({
        url: '/get_project_list',
        type:'POST',
    });
    return $.parseJSON(ajax_obj.responseText);
}
function ajax_get_model_list(){
    var ajax_obj = $.ajax({
        url: '/get_model_list',
        type:'POST',
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_stage1_info(na_id, odfo_id) {
    var id_list = {'na_id':na_id, 'odfo_id':odfo_id}
    var stage1_info = {'id_list':id_list, 'p_id':p_id};
    stage1_info = JSON.stringify(stage1_info);

    var ajax_obj = $.ajax({
        url: '/get_stage1_info',
        type:'POST',
        data: {stage1_info:stage1_info},
    });

    return $.parseJSON(ajax_obj.responseText)
}
function ajax_set_df_status(do_id, d_id){
    var device_save_info = [ do_id, d_id];
    device_save_info = JSON.stringify(device_save_info);

    var ajax_obj = $.ajax({
        url: '/set_df_status',
        type:'POST',
        data: {device_save_info:device_save_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}
function ajax_bind_device(do_id, d_name, d_id){
    var device_save_info = [ do_id, d_name, d_id];
    device_save_info = JSON.stringify(device_save_info);

    var ajax_obj = $.ajax({
        url: '/bind_device',
        type:'POST',
        data: {device_save_info:device_save_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_unbind_device(do_id, d_name, d_id){
    var device_save_info = [ do_id, d_name, d_id];
    device_save_info = JSON.stringify(device_save_info);

    var ajax_obj = $.ajax({
        url: '/unbind_device',
        type:'POST',
        data: {device_save_info:device_save_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_duplicate_circle_connection(na_id, df_id, df_type){
    var id_list = [na_id, df_id, df_type];
    var check_info = {'id_list':id_list, 'p_id':p_id};
    check_info = JSON.stringify(check_info);

    var ajax_obj = $.ajax({
        url: '/check_duplicate_circle_connection',
        type:'POST',
        data: {check_info:check_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_model_info(model_name){
    var model_info = {'model_name':model_name, 'p_id':p_id};
    var model_info = JSON.stringify(model_info);

    var ajax_obj = $.ajax({
        url: '/get_model_info',
        type:'POST',
        data: {model_info:model_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}
function ajax_get_all_device_feature_by_dm_id(dm_id){
    var feature_info = {'dm_id':dm_id};
    feature_info = JSON.stringify(feature_info);
    var ajax_obj = $.ajax({
        url: '/get_all_device_feature_by_dm_id',
        type:'POST',
        data: {feature_info:feature_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}
function ajax_get_device_list(feature_name_array, do_id, dm_id){
    var arg_dict = {'device_feature_list':feature_name_array, 'do_id':do_id, 
        'dm_id':dm_id };
    var feature_info = {'mount_info':arg_dict, 'p_id':p_id};
    feature_info = JSON.stringify(feature_info);
    var ajax_obj = $.ajax({
        url: '/get_device_list',
        type:'POST',
        data: {feature_info:feature_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_delete_connection_line_segment(na_id, kill_dfo_id, odfo_id){
    var wa_id_list = {'na_id':na_id, 'kill_dfo_id':kill_dfo_id, 'odfo_id':odfo_id};
    wa_id_list = JSON.stringify(wa_id_list);

    var ajax_obj = $.ajax({
        url: '/delete_connection_line_segment',
        type:'POST',
        data: {wa_id_list:wa_id_list},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_stage1_df_info(dfo_id){
    var stage1_info = {'dfo_id':dfo_id, 'p_id':p_id};
    stage1_info = JSON.stringify(stage1_info);
    var ajax_obj = $.ajax({
        url: '/get_stage1_df_info',
        type:'POST',
        data: {stage1_info:stage1_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_dfo_is_connected(dfo_id){
    var check_info = {'dfo_id':dfo_id, 'p_id':p_id};
    check_info = JSON.stringify(check_info);

    var ajax_obj = $.ajax({
        url: '/check_dfo_is_connected',
        type:'POST',
        data: {check_info:check_info},
    });

    return ajax_obj.responseText;
}

function ajax_get_updated_positive_config_info(dfo_id, param_i, na_id){
    var p_df_info = {'dfo_id':dfo_id, 'param_i':param_i, 'na_id':na_id };
    p_df_info = JSON.stringify(p_df_info);

    var ajax_obj = $.ajax({
        url: '/get_updated_positive_config_info',
        type:'POST',
        data: {p_df_info:p_df_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_save_function_info(func_name, df_id, fnvt_idx, func_content, is_switch, ver_enable, non_df_argument){
    var fn_info = { 'fn_name':func_name, 'fnvt_idx':fnvt_idx, 'code':func_content,
                    'df_id':df_id, 'is_switch':is_switch, 'ver_enable':ver_enable, 'non_df_argument':non_df_argument };
    fn_info = JSON.stringify(fn_info);

    var ajax_obj = $.ajax({
        url: '/save_function_info',
        type:'POST',
        data: {fn_info:fn_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_model_icon_info(do_id) {
    var model_icon_info = {'do_id':do_id, 'p_id':p_id};
    model_icon_info = JSON.stringify(model_icon_info);

    var ajax_obj = $.ajax({
        url: '/get_model_icon_info',
        type:'POST',
        data: {model_icon_info:model_icon_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_substage_list(na_id, odfo_id, is_multiple_join) {
    var monitor_info = {'na_id': Number(na_id), 'odfo_id': Number(odfo_id), 'is_multiple_join': is_multiple_join};
    monitor_info = JSON.stringify(monitor_info);

    var ajax_obj = $.ajax({
        url: '/get_substage_list',
        type:'POST',
        data: {monitor_info:monitor_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_update_dfo_alias_name(dfo_id, alias_name) {
    var ajax_obj = $.ajax({ 
        url: '/update_dfo_alias_name',
        type:'POST',
        data: {
            dfo_id : dfo_id, 
            alias_name : alias_name
        },
    });

    return $.parseJSON(ajax_obj.responseText);
}
function ajax_save_connection_line(connection_info, p_id) {
    var setting_info = {'connect_info':connection_info, 'p_id':p_id};
    setting_info = JSON.stringify(setting_info);

    var ajax_obj = $.ajax({
        url: '/save_connection_line',
        type:'POST',
        data: {setting_info:setting_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_check_duplicate_connection(feature_id_list) {
    feature_id_list = JSON.stringify(feature_id_list);
    
    var ajax_obj = $.ajax({
        url: '/check_duplicate_connection',
        type:'POST',
        data: {feature_id_list:feature_id_list},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_reload_connect_line(p_id) {
    var ajax_obj = $.ajax({
        url: '/reload_connect_line',
        type:'POST',
        data:{p_id:p_id},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_create_device_object(p_id, dm_name, idf_list, odf_list) {
    var dm_info = {
        'p_id': p_id,
        'dm_name': dm_name,
        'idf_list': idf_list,
        'odf_list': odf_list,
    }
    dm_info = JSON.stringify(dm_info);
    var ajax_obj = $.ajax({
        url: '/create_device_object',
        type:'POST',
        data: {dm_info:dm_info},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_move_in_df_function_list(fn_info) {
    fn_info = JSON.stringify(fn_info);

    var ajax_obj = $.ajax({
        url: '/move_in_df_function_list',
        type:'POST',
        data: {fn_info:fn_info},
    });

    if (ajax_obj.status == 200)
        return $.parseJSON(ajax_obj.responseText);
}

function ajax_move_out_df_function_list(fn_info) {
    fn_info = JSON.stringify(fn_info);

    var ajax_obj = $.ajax({
        url: '/move_out_df_function_list',
        type:'POST',
        data: {fn_info:fn_info},
    });

    if (ajax_obj.status == 200)
        return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_project_status (p_id) {
    var ajax_obj = $.ajax({
        url: '/get_project_status',
        type:'POST',
        data: {p_id:p_id}
    });

    if (ajax_obj.status == 200)
        return ajax_obj.responseText;
}

function ajax_get_sim_status(p_id) {
    var ajax_obj = $.ajax({
        url: '/get_sim_status',
        type:'POST',
        data: {p_id:p_id},
    });

    if (ajax_obj.status == 200)
        return ajax_obj.responseText;
}
function ajax_reload_data(p_id) {
    var ajax_obj = $.ajax({
        url: '/reload_data',
        type:'POST',
        data: {p_id:p_id},
    });

    if (ajax_obj.status == 200)
        return $.parseJSON(ajax_obj.responseText);
}

function ajax_delete_project(p_id) {
    var ajax_obj = $.ajax({
        url: '/delete_project',
        type:'POST',
        data: {p_id:p_id},
    });

    return ajax_obj.status == 200;
}

function ajax_save_connection_configuration(info, p_id) {
    var function_setting = {'setting_list':info, 'p_id':p_id};
    function_setting = JSON.stringify(function_setting);

    var ajax_obj = $.ajax({
        url: '/save_connection_configuration',
        type:'POST',
        data: {function_setting:function_setting},
    });

    return ajax_obj.status == 200;
}

function ajax_save_device_object_info(model_info) {
    model_info = JSON.stringify(model_info);
    var ajax_obj = $.ajax({
        url: '/save_device_object_info',
        type:'POST',
        data: {model_info:model_info},
    });

    return ajax_obj.status == 200;
}

function ajax_send_da_link(dm_name, phone_num, mail_addr) {
    var download_info = {'dm_name': dm_name, 'phone_num': phone_num, 'mail_addr': mail_addr};
    download_info = JSON.stringify(download_info);

    var ajax_obj = $.ajax({
        url: '/send_da_link',
        type:'POST',
        data: {download_info:download_info},
    });

    return ajax_obj.responseText;
}

function ajax_get_file_info() {

    var ajax_obj = $.ajax({
        url: '/get_file_info',
        type:'POST',
        data: {},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_create_model_without_select_feature_list() {

    var ajax_obj = $.ajax({
        url: '/create_model_without_select_feature_list',
        type:'GET',
        data: {},
    });

    return $.parseJSON(ajax_obj.responseText);
}

function ajax_get_plural_df_list() {

    var ajax_obj = $.ajax({
        url: '/plural_df_list',
        type:'GET',
        data: {},
    });

    return $.parseJSON(ajax_obj.responseText);
}
