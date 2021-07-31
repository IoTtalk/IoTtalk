function make_feature_management_html_without_detail(df_category, df_list){
    // Title
    var div_dfc_outer = $('<div>', { 'class': 'div-dfc-outer', });
    $('<label>', { 'class': 'label-dfc-title', 'text': 'Device Feature Window', }).appendTo(div_dfc_outer);

    // Type
    div_gap = $('<div>', { 'class': 'div-dfc-gap', 'id':'df_type'});
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Type', 'style':'margin-right:10px'}).appendTo(div_gap);
    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'IDF', 'style':'width:100px'});
    $('<input>', { 'type': 'radio', 'name': 'df', 'value': '1', 'id': 'IDF',
                   'style': 'margin: 5%',}).appendTo(df_label);
    $('<a>', { 'style': 'color: black', 'text': 'IDF', }).appendTo(df_label);
    df_label.appendTo(div_gap);

    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'ODF', 'style':'width:100px'});
    $('<input>', { 'type': 'radio', 'name':'df', 'value':'1', 'id':'ODF', 
                   'style': 'margin: 5%;',}).appendTo(df_label);
    $('<a>', { 'style': 'color: black', 'text': 'ODF', }).appendTo(df_label);
    df_label.appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    // Category 
    $('<label>', { 'class': 'label-dfc', 'text': 'Category', 'style':'margin-right:10px; font-weight:bold'}).appendTo(div_gap);
    $('<span>', { 'text': df_category}).appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    // Name 
    div_gap = $('<div>', { 'class': 'div-dfc-gap'});
    $('<label>', { 'class': 'label-dfc-subtitle', 'style':'float:left','text': 'DF Name', }).appendTo(div_gap);
    var feature_select = $('<select>', {'class':'name-select' });
    $.each( df_list, function( index, value ) {
        $('<option>', { 'text': value, }).appendTo(feature_select);
    });
    feature_select.appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);
    
    return div_dfc_outer;
}

function make_feature_management_html(df_category, df_list, df_info){
    var div_dfc_outer = make_feature_management_html_without_detail(df_category, df_list);
    
    //parameters
    div_gap = $('<div>', { 'class': 'div-dfc-gap', });
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Number of parameters', }).appendTo(div_gap);
    $('<input>', { 'class': 'input-dfc-df-number', 'type': 'text', 'readonly': true, 'value': df_info['parameter'].length,}).appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    var parameter_info = $('<div>', { 'class': 'div-dfc-range-setting' });

    //parameter-type
    var column_type = $('<div>', { 'class': 'div-dfc-range-column-type', });
    var title_type = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Type', }).appendTo(title_type);
    title_type.appendTo(column_type);

    $.each( df_info['parameter'], function( index, para ) {
        var type_value_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'readonly': true, 'value': para['data_type'], }).appendTo(type_value_list); 
        type_value_list.appendTo(column_type);
    });
    column_type.appendTo(parameter_info);
    
    //parameter-min
    var column_min = $('<div>', { 'class': 'div-dfc-range-column-min', });
    var title_min = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Min', }).appendTo(title_min);
    title_min.appendTo(column_min);

    $.each( df_info['parameter'], function( index, para ) {
    var min_value_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'readonly': true, 'value': para['min'], }).appendTo(min_value_list);
        min_value_list.appendTo(column_min);
    });
    column_min.appendTo(parameter_info);

    //parameter-max 
    var column_max = $('<div>', { 'class': 'div-dfc-range-column-max', });
    var title_max = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Max', }).appendTo(title_max);
    title_max.appendTo(column_max);

    $.each( df_info['parameter'], function( index, para ) {
        var max_value_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'readonly': true, 'value': para['max'], }).appendTo(max_value_list);
        max_value_list.appendTo(column_max);
    });
    column_max.appendTo(parameter_info);

    //parameter-Unit
    var column_unit = $('<div>', { 'class': 'div-dfc-range-column-unit', });
    var title_unit = $('<div>', { 'class': 'div-dfc-range-column-title', 'style':'border-right-width:1px'});
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Unit',}).appendTo(title_unit);
    title_unit.appendTo(column_unit);

    $.each( df_info['parameter'], function( index, para ) {
        var unit_value_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'readonly': true, 'value': para['unit'], }).appendTo(unit_value_list);
        unit_value_list.appendTo(column_unit);
    });
    column_unit.appendTo(parameter_info);

    parameter_info.appendTo(div_dfc_outer);

    //button
    var div_download = $('<div>', {});
    $('<input>', { 'type': 'button', 'value': 'Download', 'class': 'input-dfc-download-button', }).appendTo(div_download);
    div_download.appendTo(div_dfc_outer);

    return div_dfc_outer;
}
