function make_model_setting_html2(model_list){
    var outer_block = $('<div/>', { 'style':'width:85%; margin-left:7%', });
    $('<label>', { 'class': 'label-dmc-title', 'text': 'Device Model Window', }).appendTo(outer_block);

    var model_title = $('<div>', { 'id':'name-input-div',});
    model_title.appendTo(outer_block);

    var model_div = $('<div>', { 'class':'model-input-div',});
    $('<label>', {  'text':'DM Name', 'style':'font-weight:bold;float:left'}).appendTo(model_div);
    var model_select = $('<select>',{ 'class':'name-select' });
    $.each(model_list, function( index, value ) {
        $('<option>', { 'text': value }).appendTo(model_select);
    });
    model_select.appendTo(model_div);
    model_div.appendTo(outer_block);

    return outer_block;
}

function make_model_setting_html(json, model_list, idf_category_list){
    /* //////////////////////////////////////// */

    var model_title = $('<div>', { 'id':'name-input-div',});

    var model_div = $('<div>', { 'class':'model-input-div',});
    $('<label>', {  'text':'DM Name', 'style':'font-weight:bold'}).appendTo(model_div);
    var model_select = $('<select>',{ 'class':'name-select' });
    $.each(model_list, function( index, value ) {
        $('<option>', { 'text': value }).appendTo(model_select);
    });
    model_select.appendTo(model_div);

    var input_feature_setting_outer_block = $('<div/>', { 'id':'df_setting_block', 'style':'width:100%', });
    var idf_title = $('<div/>', {
        'class':'div-df-title',
    });

    $('<label>', { 
      'class':'label-wa-model',
      'text': 'Input Device Features', }).appendTo(idf_title);

    // type radio group
    var div_gap = $('<div>', { 'class': 'div-dfc-gap', 'id':'df_type'});
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Type', 'style':'margin-right:10px'}).appendTo(div_gap);
    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'IDF', 'style':'width:100px'});
    $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id':'IDF', 
                   'style':'margin: 5%;', 'checked':'checked'}).appendTo(df_label);
    $('<a>', { 'style': 'color: black', 'text': 'IDF', }).appendTo(df_label);
    df_label.appendTo(div_gap);

    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'ODF', 'style':'width:100px'});
    $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id':'ODF', 
                   'style': 'margin: 5%;'}).appendTo(df_label);
    $('<a>', { 'style': 'color: black', 'text': 'ODF', }).appendTo(df_label);
    df_label.appendTo(div_gap);
    div_gap.appendTo(idf_title);
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Type', 'style':'margin-right:10px'}).appendTo(idf_title);


    // category select
    var category_div = $('<div>', { 'class':'category-input-div',});
    $('<label>', {  'text':'Feature Category: ',}).appendTo(category_div);
    var category_select = $('<select>',{ 'class':'idf-category-select' });

    $.each(idf_category_list, function( index, value ) {
        $('<option>', { 'text': value }).appendTo(category_select);
    });
    category_select.appendTo(category_div);
    category_div.appendTo(idf_title);


    idf_title.appendTo(input_feature_setting_outer_block);

    //////////////////////////////////////// 
    var idf = $('<div/>', { 'class':'div-idf', });
    // -------- repeat N times -------------
    if( json['idf'].length > 0){
        $.each(json['idf'], function(index, value){
            $('<input>', { 
              'type':'checkbox',
              'class':'idf-input',
            }).appendTo(idf);

            $('<label>', { 
              'id':value[1],    // df_id
              'text': value[0], // df_name
              'class':'feature-margin label-model-feature',
            }).appendTo(idf);
            $('<br>').appendTo(idf);
        });
    }
    idf.appendTo(input_feature_setting_outer_block);

    var model_feature_outer_block = $('<div/>', { 'id':'model_feature_block', 'style':'width:100%;margin-bottom:10px', });
    var idf_title = $('<div/>', {
        'class':'selected-idf-title',
    });

    $('<label>', { 
      'class':'label-wa-model',
      'text': 'Input Device Features',
    }).appendTo(idf_title);
    idf_title.appendTo(model_feature_outer_block);

    /* //////////////////////////////////////// */
    var idf = $('<div/>', { 'class':'selected-idf', });
    /* -------- repeat N times -------------*/
    if( json['idf'].length > 0){
        $.each(json['idf'], function(index, value){

            $('<label>', { 
              'id':value[1],    // df_id
              'text': value[0], // df_name
              'class':'feature-margin',
            }).appendTo(idf);
            $('<br>').appendTo(idf);
        });
    }
    idf.appendTo(model_feature_outer_block);

    /* ----------------------------*/
    /* //////////////////////////////////////// */
    var odf_title = $('<div/>', { 'class':'selected-odf-title', });

    $('<label>', { 
      'class':'label-wa-model',
      'text': 'Output Device Features',
    }).appendTo(odf_title);
    odf_title.appendTo(model_feature_outer_block);
    /* //////////////////////////////////////// */
    var odf = $('<div/>', { 'class':'selected-odf', });
    /* -------- repeat N times -------------*/

    if( json['odf'].length > 0){
        $.each(json['odf'], function(index, value){
            $('<label>', { 
              'id':value[1],    // df_id
              'text': value[0], // df_name
              'class':'feature-margin',
            }).appendTo(odf);
            $('<br>').appendTo(odf);
        });
    }
    odf.appendTo(model_feature_outer_block);


    /* //////////////////////////////////////// */
    var outer_block = $('<div/>', { 'style':'width:85%; margin-left:7%', });
    $('<label>', { 'class': 'label-dmc-title', 'text': 'Device Model Window', }).appendTo(outer_block);
    model_title.appendTo(outer_block);
    model_div.appendTo(outer_block);

    model_feature_outer_block.appendTo(outer_block);
    input_feature_setting_outer_block.appendTo(outer_block);
    $('<button>', { 
      'style':'margin:1%',
      'id':'model_save',
      'class':json['model_id'],
      'text':'Save',
    }).appendTo(outer_block);

    $('<button>', { 
      'style':'margin:1%',
      'id':'model_delete',
      'text':'Delete',
    }).appendTo(outer_block);

    return outer_block;
}

function make_model_df_setting(type, json, df_category_list, df_category){
    var df_title = $('<div/>', {'class':'div-df-title',});

    $('<label>', { 
      'class':'label-wa-model',
      'style':'float:left; margin-right:30px',
      'text': 'Add/Delete DF',
    }).appendTo(df_title);

    // Type radio group
    var div_gap = $('<div>', { 'class': 'div-dfc-gap', 'id':'df_type', 'style':'float:left'});
    $('<label>', { 'class': 'labe-dfc-df-type', 'text': 'Type', 'style':'margin-right:10px'}).appendTo(div_gap);

    if (type == 'idf') {
        var idf_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'IDF', 'style':'width:50px'});
        $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id': 'IDF', 
                       'style':'margin: 5%;', 'checked':'checked'}).appendTo(idf_label);
        $('<a>', { 'style': 'color: black', 'text': 'IDF', }).appendTo(idf_label);
        idf_label.appendTo(div_gap);

        var odf_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'ODF', 'style':'width:50px'});
        $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id': 'ODF', 
                       'style': 'margin: 5%;'}).appendTo(odf_label);
        $('<a>', { 'style': 'color: black', 'text': 'ODF', }).appendTo(odf_label);
        odf_label.appendTo(div_gap);
    }
    else if (type == 'odf') {
        var idf_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'IDF', 'style':'width:50px'});
        $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id': 'IDF', 
                       'style':'margin: 5%;'}).appendTo(idf_label);
        $('<a>', { 'style': 'color: black', 'text': 'IDF', }).appendTo(idf_label);
        idf_label.appendTo(div_gap);

        var odf_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'ODF', 'style':'width:50px'});
        $('<input>', { 'type': 'radio', 'name':'dm', 'value':'1', 'id': 'ODF', 
                       'style': 'margin: 5%;', 'checked':'checked'}).appendTo(odf_label);
        $('<a>', { 'style': 'color: black', 'text': 'ODF', }).appendTo(odf_label);
        odf_label.appendTo(div_gap);
    }
    div_gap.appendTo(df_title);

    // Category select
    var category_div = $('<div>', { 'class':'category-input-div',});
    $('<label>', {  'text':'Category: ',}).appendTo(category_div);
    if (type == 'idf') {
        var category_select = $('<select>',{ 'class':'idf-category-select' });
    }
    else if (type == 'odf') {
        var category_select = $('<select>',{ 'class':'odf-category-select' });
    }
    $.each(df_category_list, function( index, value ) {
        if( df_category == value){
            $('<option>', { 'text': value, 'selected':'selected' }).appendTo(category_select);
        }else {
            $('<option>', { 'text': value }).appendTo(category_select);
        }
    });
    category_select.appendTo(category_div);
    category_div.appendTo(df_title);

    /* //////////////////////////////////////// */
    if (type == 'idf') {
        var df = $('<div/>', { 'class':'div-idf', });
        if( json[type].length > 0){
            $.each(json[type], function(index, value){
                let label = $('<label>', { 
                  'id':value[1],    // df_id
                  'text': value[0], // df_name
                  'class':'feature-margin label-model-feature',
                });

                if( check_selected(value[1]) ){ 
                    $('<input>', { 'type':'checkbox','class':'idf-input', 'checked':'checked'}).prependTo(label);
                } 
                else {
                    $('<input>', { 'type':'checkbox','class':'idf-input',}).prependTo(label);
                }

                label.appendTo(df);
                $('<br>').appendTo(df);
            });
         }
    }
    else if (type == 'odf') {
        var df = $('<div/>', { 'class':'div-odf', });
        if( json[type].length > 0){
            $.each(json[type], function(index, value){
                let label = $('<label>', { 
                  'id':value[1],    // df_id
                  'text': value[0], // df_name
                  'class':'feature-margin label-model-feature',
                });

                if( check_selected(value[1]) ){ 
                    $('<input>', { 'type':'checkbox','class':'odf-input', 'checked':'checked'}).prependTo(label);
                } 
                else {
                    $('<input>', { 'type':'checkbox','class':'odf-input',}).prependTo(label);
                }

                label.appendTo(df);
                $('<br>').appendTo(df);
            });
         }
    }

    /* ----------------------------*/
    var feature_setting_outer_block = $('<div/>', { 'id':'df_setting_block', 'style':'width:100%', });

    df_title.appendTo(feature_setting_outer_block);
    df.appendTo(feature_setting_outer_block);
    return feature_setting_outer_block;
}

function make_model_feature_management_html(df_info, df_id, df_name){
    // Title
    var div_dfc_outer = $('<div>', { 'class': 'div-dfc-outer', });
    $('<label>', { 'class': 'label-dfc-title', 'text': 'Device Feature Window', }).appendTo(div_dfc_outer);

    // Type
    div_gap = $('<div>', { 'class': 'div-dfc-gap', 'id':'df_type'});
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Type', 'style':'margin-right:10px'}).appendTo(div_gap);
    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'IDF', 'style':'width:100px'});
    if( df_info['df_type'] == 'input'){
        $('<input>', { 'type': 'radio', 'name':'df', 'value':'1', 'id':'IDF', 
                       'style':'margin: 5%;', 'checked':'checked', 'disabled':'disabled'}).appendTo(df_label);
    } else {
        $('<input>', { 'type': 'radio', 'name': 'df', 'value': '1', 'id': 'IDF',
                       'style': 'margin: 5%', 'disabled':'disabled'}).appendTo(df_label);
    }    
    $('<a>', { 'style': 'color: black', 'text': 'IDF', }).appendTo(df_label);
    df_label.appendTo(div_gap);

    var df_label = $('<label>', { 'class': 'labe-dfc-df-type', 'for': 'ODF', 'style':'width:100px'});
    if( df_info['df_type'] == 'output'){
        $('<input>', { 'type': 'radio', 'name':'df', 'value':'1', 'id':'ODF', 
                       'style': 'margin: 5%;', 'checked':'checked', 'disabled':'disabled'}).appendTo(df_label);
    } else {
        $('<input>', { 'type': 'radio', 'name':'df', 'value':'1', 'id':'ODF', 
                       'style': 'margin: 5%;', 'disabled':'disabled'}).appendTo(df_label);
    }
    $('<a>', { 'style': 'color: black', 'text': 'ODF', }).appendTo(df_label);
    df_label.appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    // Category 
    $('<label>', { 'class': 'label-dfc', 'text': 'Category', 'style':'margin-right:10px; font-weight:bold'}).appendTo(div_gap);
    $('<span>', { 'text': df_info['df_category']}).appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);


    // Name
    div_gap = $('<div>', { 'class': 'div-dfc-gap'});
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Name', }).appendTo(div_gap);
    var category_select = $('<select>', {'class':'name-select' });
    $('<option>', { 'text': df_name, 'selected':'selected'}).appendTo(category_select);

    category_select.appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);
    
    div_gap = $('<div>', { 'class': 'div-dfc-gap', });
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Number of parameters', }).appendTo(div_gap);
    $('<input>', { 'class': 'input-dfc-df-number', 'type': 'text', 'value': df_info['df_parameter'].length, 'disabled':'disabled' }).appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    var range_setting = $('<div>', { 'class': 'div-dfc-range-setting' });
    var type_column = $('<div>', { 'class': 'div-dfc-range-column-type', });
    var column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Type', }).appendTo(column_title);
    column_title.appendTo(type_column);


    //repeat
    $.each( df_info['df_parameter'], function( index, para_list ) {
        var setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 'style':'border-style:solid;border-width:1px'});
        if( df_info['accessible'] == '1'){
            var type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none; height:23px', 'disabled':'disabled'});
        } else {
            var type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none; height:23px'});
        }
        $.each( df_info['all_parameter_type'], function( index, parameter_type ) {
            if( para_list[0] == parameter_type){
                $('<option>', { 'text': parameter_type, 'selected':'selected' }).appendTo(type_selection);    
            } else{
                $('<option>', { 'text': parameter_type }).appendTo(type_selection);
            }
        });
        type_selection.appendTo(setting_list);
        setting_list.appendTo(type_column);    
        type_column.appendTo(range_setting);
    });
    

    var range_column = $('<div>', { 'class': 'div-dfc-range-column-min', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Min', }).appendTo(column_title);
    column_title.appendTo(range_column);
    setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
    //repeat
    $.each( df_info['df_parameter'], function( index, para_list ) {
        if( df_info['accessible'] == '1'){
            $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[1], 'disabled':'disabled'}).appendTo(setting_list);
        } else {
            $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[1], }).appendTo(setting_list);
        }
    });
    //end
    setting_list.appendTo(range_column);
    range_column.appendTo(range_setting);


    range_column = $('<div>', { 'class': 'div-dfc-range-column-max', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Max', }).appendTo(column_title);
    column_title.appendTo(range_column);
    setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
    //repeat
    $.each( df_info['df_parameter'], function( index, para_list ) {
        if( df_info['accessible'] == '1'){
            $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[2], 'disabled':'disabled' }).appendTo(setting_list);
        } else {
            $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[2], }).appendTo(setting_list);
        }
    });
    //end
    setting_list.appendTo(range_column);
    range_column.appendTo(range_setting);

    // Unit start
    range_column = $('<div>', { 'class': 'div-dfc-range-column-unit', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', 'style':'border-right-width:1px'});
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Unit',}).appendTo(column_title);
    column_title.appendTo(range_column);

    // repeat
    $.each( df_info['df_parameter'], function( index, para_list ) {

        setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 
                                'style':'border-right-width:1px; border-style:solid;border-width:1px;',  });
        if( df_info['accessible'] == '1'){
            type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none;height:23px', 'disabled':'disabled'});
        } else {
            type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none;height:23px'});
        }
        //$('<option>', { 'text': 'm/s', }).appendTo(type_selection);
        type_selection.appendTo(setting_list);
        setting_list.appendTo(range_column);
        refresh_unit_list(type_selection, para_list[3]);
    });
    range_column.appendTo(range_setting);
    // Unit end
 
    range_setting.appendTo(div_dfc_outer);

    if( df_info['accessible'] == '0'){
        var div_save = $('<div>', {});
        $('<input>', { 'type': 'button', 'value': 'Save', 'class': 'input-dfc-save-button', 'id':df_id}).appendTo(div_save);
        div_save.appendTo(div_dfc_outer);
    } 

    return div_dfc_outer;
}

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
    var category_select = $('<select>', {'class':'name-select' });
    $.each( df_list, function( index, value ) {
        $('<option>', { 'text': value, }).appendTo(category_select);
    });
    category_select.appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);
    
    return div_dfc_outer;
}

function make_feature_management_html(df_category, df_list, df_info){
    var div_dfc_outer = make_feature_management_html_without_detail(df_category, df_list);
    
    //parameters
    div_gap = $('<div>', { 'class': 'div-dfc-gap', });
    $('<label>', { 'class': 'label-dfc-subtitle', 'text': 'Number of parameters', }).appendTo(div_gap);
    $('<input>', { 'class': 'input-dfc-df-number', 'type': 'text', 'value': df_info['df_parameter'].length,}).appendTo(div_gap);
    div_gap.appendTo(div_dfc_outer);

    var range_setting = $('<div>', { 'class': 'div-dfc-range-setting' });
    var type_column = $('<div>', { 'class': 'div-dfc-range-column-type', });
    var column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Type', }).appendTo(column_title);
    column_title.appendTo(type_column);

    //parameter-type
    $.each( df_info['df_parameter'], function( index, para_list ) {
        var setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 'style':'border-style:solid;border-width:1px'});
        var type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none; height:23px'});
        $.each( df_info['all_parameter_type'], function( index, parameter_type ) {
            if( para_list[0] == parameter_type){
                $('<option>', { 'text': parameter_type, 'selected':'selected' }).appendTo(type_selection);    
            } else{
                $('<option>', { 'text': parameter_type }).appendTo(type_selection);
            }
        });
        type_selection.appendTo(setting_list);
        setting_list.appendTo(type_column);    
        type_column.appendTo(range_setting);
    });
    
    //parameter-min
    var range_column = $('<div>', { 'class': 'div-dfc-range-column-min', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Min', }).appendTo(column_title);
    column_title.appendTo(range_column);
    setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
    $.each( df_info['df_parameter'], function( index, para_list ) {
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[1], }).appendTo(setting_list);
    });
    setting_list.appendTo(range_column);
    range_column.appendTo(range_setting);

    //parameter-max 
    range_column = $('<div>', { 'class': 'div-dfc-range-column-max', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', });
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Max', }).appendTo(column_title);
    column_title.appendTo(range_column);
    setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', });
    $.each( df_info['df_parameter'], function( index, para_list ) {
        $('<input>', { 'type': 'text', 'class': 'dfc-range-setting', 'value': para_list[2], }).appendTo(setting_list);
    });
    setting_list.appendTo(range_column);
    range_column.appendTo(range_setting);

    //parameter-Unit
    range_column = $('<div>', { 'class': 'div-dfc-range-column-unit', });
    column_title = $('<div>', { 'class': 'div-dfc-range-column-title', 'style':'border-right-width:1px'});
    $('<label>', { 'class': 'label-dfc-range-column-subtitle', 'text': 'Unit',}).appendTo(column_title);
    column_title.appendTo(range_column);

    $.each( df_info['df_parameter'], function( index, para_list ) {

        setting_list = $('<div>', { 'class': 'div-dfc-range-setting-list', 
                                'style':'border-right-width:1px; border-style:solid;border-width:1px;',  });
        type_selection = $('<select>', { 'class': 'dfc-range-setting', 'style':'border-style:none;height:23px'});
        type_selection.appendTo(setting_list);
        setting_list.appendTo(range_column);
        refresh_unit_list(type_selection, para_list[3]);
    });
    range_column.appendTo(range_setting);
    range_setting.appendTo(div_dfc_outer);

    //button
    var div_save = $('<div>', {});
    $('<input>', { 'type': 'button', 'value': 'Save', 'class': 'input-dfc-save-button', }).appendTo(div_save);
    $('<input>', { 'type': 'button', 'value': 'Delete', 'class': 'input-dfc-delete-button', }).appendTo(div_save);
    if (df_info['df_id'] != 0) {
        $('<input>', { 'type': 'button', 'value': 'Upload', 'class': 'input-dfc-upload-button', 'df_id': df_info['df_id'] }).appendTo(div_save);
    }
    div_save.appendTo(div_dfc_outer);

    return div_dfc_outer;
}

function check_selected(df_id){

    var flag = false;
    var df_id = df_id.toString();
    $('.selected-idf').find('label').each(function( index ) {
        if( $(this).attr('id') == df_id){
            flag = true;
        }
    });

    $('.selected-odf').find('label').each(function( index ) {
        if( $(this).attr('id') == df_id){
            flag = true;
        }
    });

    return flag;
}

