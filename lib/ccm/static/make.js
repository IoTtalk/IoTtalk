
function make_join_monitor_block_html(){

    var div_monitor_outer = $('<div>', { 'class': 'div-join-monitor-outer join-mointor-hidden', });

    $('<span>', { 'text':'Multiple Join Monitor'}).appendTo(div_monitor_outer);
    $('<br>').appendTo(div_monitor_outer);

    var div_log_block_outer = $('<div>', { 'class': 'div-add-function-outer', });
    var div_prog_title = $('<div>', { 'class': 'div-program-title', });
    var prog_title_label = $('<label>', { 'class':'label-join', 'style':'width:100px;float:left',
                                          'text':'Function'});
    prog_title_label.appendTo(div_prog_title);

    $('<button>', {
     'id':'join_tableorchart',
     'class':'control_button',
     'text': 'Table'
    }).appendTo(div_prog_title);

    div_prog_title.appendTo(div_log_block_outer);

    var div_intro_block = $('<div>', { 'class': 'div-intro-block', 'style':'overflow-y:scroll; padding-top:0px'});

    ///////////////////////////////////////
    // generate scrollable table
    var data_div = $('<div>', {
        //'style': 'height: 30%',
        'class': 'monitor_data_div',
    });
    //data_div.text('No data received now.');
    data_div.appendTo(div_intro_block);
    ///////////////////////////////////////

    div_intro_block.appendTo(div_log_block_outer);
    div_log_block_outer.appendTo(div_monitor_outer);
    $('<br>').appendTo(div_monitor_outer);

    //$('#management_window').empty();
    div_monitor_outer.prependTo('#management_window');
    var outer_height =  $('.div-join-monitor-outer .div-add-function-outer').height();

//return div_monitor_outer;
}

function make_idf_monitor_block_html(info, stage_list){

    /*
    info = {
      'p_df_info': [[df_name, dfo_id], ...],
      'p_dm_name': 'Smartphone',
      'do_id': do_id,
      'dm_type': 'intput'/'output',
      'simulator_mode':'Continue'/'Stop'
    }
    */

    var div_monitor_outer = $('<div>', { 'class': 'div-idf-monitor-outer', });
    //$('<span>', { 'text':'IDF Module Monitor ( '+info['p_dm_name'] +' )'}).appendTo(div_monitor_outer);
    $('<span>', { 'text':'IDF Monitor'}).appendTo(div_monitor_outer);
    $('<br>').appendTo(div_monitor_outer);

    var div_log_block_outer = $('<div>', { 'class': 'div-add-function-outer', });
    var div_prog_title = $('<div>', { 'class': 'div-program-title', });
    var prog_title_label = $('<label>', { 'class':'label-idf', 'style':'width:100px;float:left', 'name':info['na_id'],
                                          'text':'Sub-stage:'});
    prog_title_label.appendTo(div_prog_title);

    var step_select = $('<select>', {'class': 'step-select'});
    $.each( stage_list, function(index, value){
        $('<option>', { 'text':value} ).appendTo(step_select);
    });
    step_select.appendTo(div_prog_title);

    var df_select = $('<select>', {'class': 'input-df-select'});
    $.each( info['idf_info'], function( index, idf_info){
        $('<option>', { 'text': (index+1)+' '+idf_info[0], 'name':idf_info[1]}).appendTo(df_select);
    });
    df_select.appendTo(div_prog_title);

    $('<button>', {
     'id':'idf_tableorchart',
     'class':'control_button',
     'text': 'Table'
    }).appendTo(div_prog_title);

    $('<button>', {
     'id':'step-button',
     'class':'control_button input-step-button',
     'text': 'Next'
    }).appendTo(div_prog_title);

    $('<button>', {
      'class':'control_button stop_continue_button',
      'text': info['exec_button'],
    }).appendTo(div_prog_title);


    div_prog_title.appendTo(div_log_block_outer);

    var div_intro_block = $('<div>', { 'class': 'div-intro-block', 'style':'overflow-y:scroll; padding-top:0px'});

    ///////////////////////////////////////
    // generate scrollable table
    var data_div = $('<div>', {
        //'style': 'height: 30%',
        'class': 'monitor_data_div',
    });
    //data_div.text('No data received now.');
    data_div.appendTo(div_intro_block);
    ///////////////////////////////////////

    div_intro_block.appendTo(div_log_block_outer);

    div_log_block_outer.appendTo(div_monitor_outer);

    $('<br>').appendTo(div_monitor_outer);
    if( $('.div-idf-monitor-outer').length != 0){
        $('.div-idf-monitor-outer').remove();
    }
    div_monitor_outer.prependTo('#management_window');

    var outer_height =  $('.div-idf-monitor-outer .div-add-function-outer').height() - 70;
    if( info['exec_button'] == 'Continue' ){
        $('button#step-button').attr('disabled','disabled');
        $('button#step-button').css('color','rgb(187, 177, 177)');
        $('button#specific-send-button').attr('disabled','disabled');
        $('button#specific-send-button').css('color','rgb(187, 177, 177)');
    }

    //return div_monitor_outer;
}

function make_odf_monitor_block_html(info, stage_list){
    var monitor_info = info;
    var div_monitor_outer = $('<div>', { 'class': 'div-odf-monitor-outer', });  
    //$('<span>', { 'text':'ODF Module Monitor ( '+info['p_dm_name'] +' )'}).appendTo(div_monitor_outer);
    $('<span>', { 'text':'ODF Monitor'}).appendTo(div_monitor_outer);
    $('<br>').appendTo(div_monitor_outer);


    var div_log_block_outer = $('<div>', { 'class': 'div-add-function-outer', });
    var div_prog_title = $('<div>', { 'class': 'div-program-title', });
    var prog_title_label = $('<label>', { 'class':'label-idf',
                                          'style':'width:100px;float:left',
                                          'name':monitor_info['na_id'],
                                          'text':'Sub-stage:'});
    prog_title_label.appendTo(div_prog_title);

    $('<button>', {
     'id':'odf_tableorchart',
     'class':'control_button',
     'text': 'Table'
    }).appendTo(div_prog_title);

    var step_select = $('<select>', {'class': 'step-select'});
    $.each( stage_list, function(index, value){
        $('<option>', { 'text':value} ).appendTo(step_select);
    });
    step_select.appendTo(div_prog_title);


    var df_select = $('<select>', {'class': 'output-df-select'});

    $.each( info['odf_info'], function( index, odf_info){
        $('<option>', { 'text': (index+1)+' '+odf_info[0], 'name':odf_info[1]}).appendTo(df_select);
    });
    df_select.appendTo(div_prog_title);

    div_prog_title.appendTo(div_log_block_outer);

    var div_intro_block = $('<div>', { 'class': 'div-intro-block', 'style':'overflow-y:scroll; padding-top:0px' });

    ///////////////////////////////////////
    // generate scrollable table
    var data_div = $('<div>', {
        //'style': 'height: 30%',
        'class': 'monitor_data_div',
    });
    //data_div.text('No data received now.');
    data_div.appendTo(div_intro_block);
    ///////////////////////////////////////
    div_intro_block.appendTo(div_log_block_outer);

    div_log_block_outer.appendTo(div_monitor_outer);

    if( $('.div-odf-monitor-outer').length != 0){
        $('.div-odf-monitor-outer').remove();
    }
    div_monitor_outer.appendTo('#management_window');
    var outer_height =  $('.div-odf-monitor-outer .div-add-function-outer').height() - 70;

    //return div_monitor_outer;
}

function make_da_install_module_html(){

    var outer = $('<div>', { 'class':'da-module'});
    var title = $('<div/>', {'class':'da-title'});
    $('<label>', {
      'class':'label-wa-model',
      'text': 'DA Installation',
    }).appendTo(title);
    title.appendTo(outer);

    var email_div = $('<div/>', {'class':'da-email-div'});
    $('<label>', {  'text':'Send DA To Email Address: ',}).appendTo(email_div);
    $('<input>', {  'type':'text', 'id':'email-input', 'placeholder':'Please enter your email address.'}).appendTo(email_div);
    $('<button>', { 'style':'', 'id':'email-send', 'text':'send',}).appendTo(email_div);
    email_div.appendTo(outer);

    var sms_div = $('<div/>', {'class':'da-sms-div'});
    $('<label>', {  'text':'Send DA To Phone Number: ',}).appendTo(sms_div);
    $('<input>', {  'type':'text', 'id':'phone-input', 'placeholder':'Please enter your phone number.'}).appendTo(sms_div);
    $('<button>', { 'style':'', 'id':'sms-send', 'text':'send',}).appendTo(sms_div);
    sms_div.appendTo(outer);
    return outer;
}

function make_model_setting_html(json){
    var model_title = $('<div/>', { 'class':'div-wa-model-title', });
    $('<label>', {
      'class':'label-wa-feature device_model_name',
      'text': json['model_name'],
    }).appendTo(model_title);

    var idf_title = $('<div/>', {
        'class':'div-idf-title',
    });

    $('<label>', {
      'class':'label-wa-model',
      'text': 'Input Device Features',
    }).appendTo(idf_title);

    var idf = $('<div/>', { 'class':'div-idf idf_table', });


    // -------- repeat N times -------------
    if( json['idf'].length > 0){
        if (json['model_name'] == "Folder_I"){
            var file_info = ajax_get_file_info();

            $.each(json['idf'], function(index, value){
                  $('<label>', {
                    'name':value[1],    // df_id
                    'text': value[0], // df_name
                    'class':'feature-margin label-model-feature IDF',
                  }).appendTo(idf);

                  HtmlSelect = '<select class="IDF_list" id="FOLDER_I" name="' + value[0] + '">';
                  HtmlSelect = HtmlSelect + '<option>None</option>';
                  for (i=0; i<file_info.length; ++i) HtmlSelect = HtmlSelect + '<option>' + file_info[i].toString() + '</option>';
                  HtmlSelect = HtmlSelect + '<option>add new file</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(idf);
            });
        }
        else if (plural_DF_list.indexOf(json['model_name']) == -1){
            $.each(json['idf'], function(index, value){
                  $('<input>', {
                    'type':'checkbox',
                    'class':'idf-input',
                    'name': value[0],
                  }).appendTo(idf);

                  $('<label>', {
                    'name':value[1],    // df_id
                    'text': value[0]+' '+value[2]+' ', // df_name
                    'class':'feature-margin label-model-feature',
                  }).appendTo(idf);
              //comment
              var comment_wrapper = $('<div>', { 'class':'df-comment-div df-comment-hidden'});
              $('<label>', { 'class':'df-comment-label', 'text':value[2]}).appendTo(comment_wrapper);
              comment_wrapper.appendTo(idf);
              $('<br>').appendTo(idf);
            });
        }
        else{
            //Coollect and arrange all df start
            let single_df = [];
            let multiple_df = [];
            let multiple_df_num = new Array(50);
            $.each(json['idf'], function(index, value){
                if ( isNaN(value[0].substr(-1,1)) )   single_df.push(value[0]);
                else if ( multiple_df.indexOf(value[0].replace(/\d*$/, '')) == -1){
                    multiple_df.push(value[0].replace(/\d*$/, ''));
                    multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))] = value[0].replace(value[0].replace(/\d*$/, ''),'');
                }
                else if ( parseInt(multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))]) <  parseInt(value[0].replace(value[0].replace(/\d*$/, ''),''))){
                    multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))]= value[0].replace(value[0].replace(/\d*$/, ''),'');
                }
            });

            var HtmlSelect = '';
            multiple_df.forEach(MultiHtmlCode);     // generate html codes for multiple dfs
            function MultiHtmlCode(item, index){
                  $('<label>', {
                    'name':index,    // df_id
                    'text': item, // df_name
                    'class':'feature-margin label-model-feature IDF',
                    'tag':'MULTIPLE',
                  }).appendTo(idf);

                  HtmlSelect = '<select class="IDF_list" id="MULTIPLE" name="' + item + '">';
                  for (i=0; i<= multiple_df_num[index]; i=i+1) HtmlSelect = HtmlSelect + '<option>' + i.toString() + '</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(idf);
            }

            single_df.forEach(SingleHtmlCode);      // generate html codes for each single dfs
            function SingleHtmlCode(item, index){
                  $('<label>', {
                    'name':index,    // df_id
                    'text': item, // df_name
                    'class':'feature-margin label-model-feature IDF',
                    'tag':'SINGLE',
                  }).appendTo(idf);
                  $('<select class="IDF_list" id="SINGLE" name="'+ item +'"> <option>0</option> <option>1</option> </select> <br>').appendTo(idf);
            }
        } // if plural_DF end
    }  //idf if end

    var odf_title = $('<div/>', { 'class':'div-odf-title', });

    $('<label>', {
      'class':'label-wa-model',
      'text': 'Output Device Features',
    }).appendTo(odf_title);
    var odf = $('<div/>', { 'class':'div-odf odf_table', });
    // -------- repeat N times -------------

    if( json['odf'].length > 0){
        if (json['model_name'] == "Folder_O"){
            var file_info = ajax_get_file_info();

            $.each(json['odf'], function(index, value){
                  $('<label>', {
                    'name':value[1],    // df_id
                    'text': value[0], // df_name
                    'class':'feature-margin label-model-feature ODF',
                  }).appendTo(odf);

                  HtmlSelect = '<select class="ODF_list" id="FOLDER_O" name="' + value[0] + '">';
                  HtmlSelect = HtmlSelect + '<option>None</option>';
                  for (i=0; i<file_info.length; ++i) HtmlSelect = HtmlSelect + '<option>' + file_info[i].toString() + '</option>';
                  HtmlSelect = HtmlSelect + '<option>add new file</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(odf);
            });
        }
        else if (plural_DF_list.indexOf(json['model_name']) == -1){
            $.each(json['odf'], function(index, value){
                $('<input>', {
                  'type':'checkbox',
                  'class':'odf-input',
                  'name': value[0],
                }).appendTo(odf);
                $('<label>', {
                  'name':value[1],    // df_id
                  'text': value[0], // df_name
                  'class':'feature-margin label-model-feature',
                }).appendTo(odf);
                var comment_wrapper = $('<div>', { 'class':'df-comment-div df-comment-hidden'});
                $('<label>', { 'class':'df-comment-label', 'text':value[2]}).appendTo(comment_wrapper);
                comment_wrapper.appendTo(odf);
                $('<br>').appendTo(odf);
            });
        }
        else{
            //Coollect and arrange all df start
            let single_df = [];
            let multiple_df = [];
            let multiple_df_num = new Array(50);
            $.each(json['odf'], function(index, value){
                if ( isNaN(value[0].substr(-1,1)) )   single_df.push(value[0]);
                else if ( multiple_df.indexOf(value[0].replace(/\d*$/, ''))== -1){
                    multiple_df.push(value[0].replace(/\d*$/, ''));
                    multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))] = value[0].replace(value[0].replace(/\d*$/, ''),'');
                }
                else if ( parseInt(multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))]) <  parseInt(value[0].replace(value[0].replace(/\d*$/, ''),''))){
                    multiple_df_num[multiple_df.indexOf(value[0].replace(/\d*$/, ''))]= value[0].replace(value[0].replace(/\d*$/, ''),'');
                }
            });
            //Collect and arrange all df end

            var HtmlSelect = '';
            multiple_df.forEach(MultiHtmlCode);     // generate html codes for multiple dfs
            function MultiHtmlCode(item, index){
                  $('<label>', {
                    'name':index,    // df_id
                    'text': item, // df_name
                    'class':'feature-margin label-model-feature ODF',
                    'tag':'MULTIPLE',
                  }).appendTo(odf);

                  HtmlSelect = '<select class="ODF_list" id="MULTIPLE" name="' + item + '">';
                  for (i=0; i<= multiple_df_num[index]; i=i+1) HtmlSelect = HtmlSelect + '<option>' + i.toString() + '</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(odf);
            }

            single_df.forEach(SingleHtmlCode);      // generate html codes for each single dfs
            function SingleHtmlCode(item, index){
                  $('<label>', {
                    'name':index,    // df_id
                    'text': item, // df_name
                    'class':'feature-margin label-model-feature ODF',
                    'tag':'SINGLE',
                  }).appendTo(odf);
                  $('<select class="ODF_list" id="SINGLE" name="'+ item +'"> <option>0</option> <option>1</option> </select> <br>').appendTo(odf);
            }
        }
    }

    var outer_block = $('<div/>', { 'style':'width:100%', });

    model_title.appendTo(outer_block);
    idf_title.appendTo(outer_block);
    idf.appendTo(outer_block);
    odf_title.appendTo(outer_block);
    odf.appendTo(outer_block);
    $('<button>', {
      'style':'margin:1%',
      'id':'save_model',
      'text':'Save',
    }).appendTo(outer_block);

    return outer_block;
}

function make_model_feature_selector_html(json){
    var model_title = $('<div/>', { 'class':'div-wa-model-title', });
    $('<label>', {
      'class':'label-wa-feature',
      'text': json['model_name'],
      'name': json['do_id'],
    }).appendTo(model_title);

    var idf_title = $('<div/>', {
        'class':'div-idf-title',
    });

    $('<label>', {
      'class':'label-wa-model',
      'text': 'Input Device Features',
    }).appendTo(idf_title);

    var idf = $('<div/>', { 'class':'div-idf', });

    // -------- repeat N times -------------
    if( json['idf'].length > 0){
        //[0]: df name
        //[1]: df_id
        //[2]: checked or not
        //[3]: comment
        if (json['model_name'] == "Folder_I"){
            var file_info = ajax_get_file_info();

            $.each(json['idf'], function(index, value){
                  $('<label>', {
                    'name':value[1],    // df_id
                    'text': value[0], // df_name
                    'class':'feature-margin label-model-feature IDF',
                  }).appendTo(idf);

                  HtmlSelect = '<select class="IDF_list" id="FOLDER_I" name="' + value[0] + '">';
                  HtmlSelect = HtmlSelect + '<option>None</option>';
                  for (i=0; i<file_info.length; ++i) HtmlSelect = HtmlSelect + '<option>' + file_info[i].toString() + '</option>';
                  HtmlSelect = HtmlSelect + '<option>add new file</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(idf);
            });
        }
        else if (plural_DF_list.indexOf(json['model_name']) == -1){        
            $.each(json['idf'], function(index, value){
                if(value[2] == 1) $('<input>', { 'type':'checkbox','class':'idf-input','checked':'checked'}).appendTo(idf);
                else $('<input>', { 'type':'checkbox','class':'idf-input', }).appendTo(idf);

                $('<label>', {
                  'name':value[1],  // df_id
                  'text': value[0], // df_name
                  'class':'feature-margin label-model-feature',
                }).appendTo(idf);

                var comment_wrapper = $('<div>', { 'class':'df-comment-div df-comment-hidden'});
                $('<label>', { 'class':'df-comment-label', 'text':value[3]}).appendTo(comment_wrapper);
                comment_wrapper.appendTo(idf);
                $('<br>').appendTo(idf);
            });
        }
        else{
	    //Coollect and arrange all df start
	    let single_df_list={};  //single df_name:checked or not
	    let multiple_df_list={};//multiple df_name : max checked num
	    let multiple_df_max_num={}; 
		$.each(json['idf'], function(index, value){
		    if (isNaN(value[0].substr(-1,1))) single_df_list[value[0]] = value[2];
		    else if ((value[0].replace(/\d*$/, '') in multiple_df_list) == false){
			if (value[2]) multiple_df_list[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
			else multiple_df_list[value[0].replace(/\d*$/, '')] = 0;
			multiple_df_max_num[value[0].replace(/\d*$/, '')] =  value[0].replace(value[0].replace(/\d*$/, ''),'');
		    }
		    else{ 
		       if ( parseInt(multiple_df_max_num[value[0].replace(/\d*$/, '')]) < parseInt( value[0].replace(value[0].replace(/\d*$/, ''),''))){
			   multiple_df_max_num[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
		       }
		       if (value[2] && ( parseInt(multiple_df_list[value[0].replace(/\d*$/, '')]) < parseInt(value[0].replace(value[0].replace(/\d*$/, ''),'')))){
			   multiple_df_list[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
		       }
		    }
		});
	    //Collect and arrange all df end

	    var HtmlSelect = '';
	    for (var key in multiple_df_list){
		  $('<label>', {
		    //'name':'',
		    'text': key, // df_name
		    'class':'feature-margin label-model-feature IDF',
		    'tag':'MULTIPLE',
		  }).appendTo(idf);

		  HtmlSelect = '<select class="IDF_list" id="MULTIPLE" name="' + key + '">';
		  for (i=0; i<= multiple_df_max_num[key]; i=i+1){
		      if (i != multiple_df_list[key])  HtmlSelect = HtmlSelect + '<option>' + i.toString() + '</option>';
		      else  HtmlSelect = HtmlSelect + '<option selected>' + i.toString() + '</option>';
		  }

		  HtmlSelect = HtmlSelect + '</select> <br>';
		  $(HtmlSelect).appendTo(idf); 
	    }

	    for (var key in single_df_list){
		  $('<label>', {
		    //'name':'',
		    'text': key, // df_name
		    'class':'feature-margin label-model-feature IDF',
		    'tag':'SINGLE',
		  }).appendTo(idf);
		  if (single_df_list[key]) $('<select class="IDF_list" id="SINGLE" name="'+ key +'"> <option>0</option> <option selected>1</option> </select> <br>').appendTo(idf);
		  else $('<select class="IDF_list" id="SINGLE" name="'+ key +'"> <option>0</option> <option>1</option> </select> <br>').appendTo(idf);
	    } 
        } //else end
     }

    var odf_title = $('<div/>', { 'class':'div-odf-title', });

    $('<label>', {
      'class':'label-wa-model',
      'text': 'Output Device Features',
    }).appendTo(odf_title);

    var odf = $('<div/>', { 'class':'div-odf', });
    // -------- repeat N times -------------

    if( json['odf'].length > 0){
        if (json['model_name'] == "Folder_O"){
            var file_info = ajax_get_file_info();

            $.each(json['odf'], function(index, value){
                  $('<label>', {
                    'name':value[1],    // df_id
                    'text': value[0], // df_name
                    'class':'feature-margin label-model-feature ODF',
                  }).appendTo(odf);

                  HtmlSelect = '<select class="ODF_list" id="FOLDER_O" name="' + value[0] + '">';
                  HtmlSelect = HtmlSelect + '<option>None</option>';
                  for (i=0; i<file_info.length; ++i) HtmlSelect = HtmlSelect + '<option>' + file_info[i].toString() + '</option>';
                  HtmlSelect = HtmlSelect + '<option>add new file</option>';
                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(odf);
            });
        }
        else if (plural_DF_list.indexOf(json['model_name']) == -1){
            $.each(json['odf'], function(index, value){
                if(value[2] == '1') $('<input>', { 'type':'checkbox', 'class':'odf-input', 'checked':'checked'}).appendTo(odf);
                else $('<input>', { 'type':'checkbox', 'class':'odf-input', }).appendTo(odf);
    
                $('<label>', {
                  'name':value[1],    // df_id
                  'text': value[0], // df_name
                  'class':'feature-margin label-model-feature',
                }).appendTo(odf);

                var comment_wrapper = $('<div>', { 'class':'df-comment-div df-comment-hidden'});
                $('<label>', { 'class':'df-comment-label', 'text':value[3]}).appendTo(comment_wrapper);
                comment_wrapper.appendTo(odf);
                $('<br>').appendTo(odf);
            });
        }
        else{
            //Coollect and arrange all df start
            let single_df_list={};  //single df_name:checked or not
            let multiple_df_list={};//multiple df_name : max checked num
            let multiple_df_max_num={};
                $.each(json['odf'], function(index, value){
                    if (isNaN(value[0].substr(-1,1))) single_df_list[value[0]] = value[2];
                    else if ((value[0].replace(/\d*$/, '') in multiple_df_list)  == false){
                        if (value[2]) multiple_df_list[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
                        else multiple_df_list[value[0].replace(/\d*$/, '')] = 0;
                        multiple_df_max_num[value[0].replace(/\d*$/, '')] =  value[0].replace(value[0].replace(/\d*$/, ''),'');
                    }
                    else{
                       if ( parseInt(multiple_df_max_num[value[0].replace(/\d*$/, '')]) < parseInt(value[0].replace(value[0].replace(/\d*$/, ''),''))){
                           multiple_df_max_num[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
                       }
                       if (value[2] && parseInt(multiple_df_list[value[0].replace(/\d*$/, '')]) < parseInt(value[0].replace(value[0].replace(/\d*$/, ''),'')) ){
                           multiple_df_list[value[0].replace(/\d*$/, '')] = value[0].replace(value[0].replace(/\d*$/, ''),'');
                       }
                    }
                });
            //Collect and arrange all df end

            var HtmlSelect = '';
            for (var key in multiple_df_list){
                  $('<label>', {
                    //'name':'',
                    'text': key, // df_name
                    'class':'feature-margin label-model-feature ODF',
                    'tag':'MULTIPLE',
                  }).appendTo(odf);

                  HtmlSelect = '<select class="ODF_list" id="MULTIPLE" name="' + key + '">';
                  for (i=0; i<= multiple_df_max_num[key]; i=i+1){
                      if (i != multiple_df_list[key])  HtmlSelect = HtmlSelect + '<option>' + i.toString() + '</option>';
                      else  HtmlSelect = HtmlSelect + '<option selected>' + i.toString() + '</option>';
                  }

                  HtmlSelect = HtmlSelect + '</select> <br>';
                  $(HtmlSelect).appendTo(odf);
            }

            for (var key in single_df_list){
                  $('<label>', {
                    //'name':'',
                    'text': key, // df_name
                    'class':'feature-margin label-model-feature ODF',
                    'tag':'SINGLE',
                  }).appendTo(odf);
                  if (single_df_list[key]) $('<select class="ODF_list" id="SINGLE" name="'+ key +'"> <option>0</option> <option selected>1</option> </select> <br>').appendTo(odf);
                  else $('<select class="ODF_list" id="SINGLE" name="'+ key +'"> <option>0</option> <option>1</option> </select> <br>').appendTo(odf);
            }
        }
    }

    var outer_block = $('<div/>', { 'style':'width:100%', });

    model_title.appendTo(outer_block);
    idf_title.appendTo(outer_block);
    idf.appendTo(outer_block);
    odf_title.appendTo(outer_block);
    odf.appendTo(outer_block);
    $('<button>', {
      'style':'margin:1%',
      'id':'save_model',
      'text':'Save',
    }).appendTo(outer_block);

    $('<button>', {
      'style':'margin:1%',
      'id':'delete_model',
      'text':'Delete',
    }).appendTo(outer_block);

    if (json['model_name'] == 'ML_device'){	
        $('<button>', {
          'style':'margin:1%',
          'id':'advance',
          'text':'Extra Setup',
        }).appendTo(outer_block);
    }

    return outer_block;
}

function make_model_block_html(p_model_info ,type){

    // =========== crate div-catagory ================
    var div_catagory = $('<div/>', {
        'class':'div-inline div-catagory-border div-catagory',
    });

    $('<img>', {
      //'src':'/static/images/'+dm_type+'.png',
      'src':'/static/images/setting.png',
      'name':p_model_info[type+'_do_id'],
      'style':'cursor:pointer; width:100%;',
      'class':'setting_obj',
    }).appendTo(div_catagory);

    var div_device = $('<div/>', {
        'class':'div-inline div-device-border div-device',
    });
    if ( p_model_info['p_dm_name'][2] == 0){
        $('<input>', {
          'type': 'text',
          'class':'label-device',
          'style':'cursor:pointer;color:blue',
          'readonly': 'readonly',
          'value': p_model_info['p_dm_name'][0],
          'name': p_model_info['p_dm_name'][1],
        }).appendTo(div_device);
    }
    else{
        $('<input>', {
          'type': 'text',
          'class':'label-device',
          'style':'cursor:pointer;',
          'readonly': 'readonly',
          'value': p_model_info['p_dm_name'][0],
          'name': p_model_info['p_dm_name'][1],
        }).appendTo(div_device);
    }

    var div_catagory_device = $('<div/>', {
        'class':'div-catagory-device',
    });

    div_catagory.appendTo(div_catagory_device);
    div_device.appendTo(div_catagory_device);

    // =========== create div-feature ================

    var div_obstacle = $('<div/>', {
        'class':'div-obstacle',
    });

    var div_features = $('<div/>', {
        'class':'div-features',
    });

    div_obstacle.appendTo(div_features);

    ///////// 可能多次
    $.each(p_model_info['p_'+type[0]+'df_list'], function(index, value){
        var div_feature = $('<div/>', {
            'class':'feature_obj div-border',
            'name': value[1],
        });

        $('<label>', {
          'class':'label-feature',
          'style':'cursor:pointer',
          'text': value[0],
        }).appendTo(div_feature);

        if( type == 'in'){
            $('<img>', {
              'src':value[2],
              'class':'img-'+type+'put-feature',
              'style':'cursor:pointer',
            }).appendTo(div_feature);
        }else {
            $('<img>', {
              'src':value[2],
              'class':'img-'+type+'put-feature',
              'style':'cursor:pointer; float:left',
            }).appendTo(div_feature);
        }
        div_feature.appendTo(div_features);
    });
    ///////////

    /* =========== create in-device ================ */
    var device = $('<div/>', {
        'class':'div-outer div-border device-obj',
        'name': type+'_device',
    });

    div_catagory_device.appendTo(device);
    div_features.appendTo(device);
    return device;

}

function make_single_odf_block_html(f_info){

    //===
    div_odf_column_title = $('<div>',{ 'class':'df-module-title', 'style':'background-color:#BEBEBE', });

    $('<label>',{ 'class':'label-odf', 'text': f_info['df_module_title']+' (ODF)'}).appendTo(div_odf_column_title);

    div_odf_tab_title = $('<div>',{ 'class':'div-odf-first-tab-title' });
    div_odf_alias_name = $('<label>',{ 'class':'label-odf', 'text':f_info['alias_name'], 'name':f_info['df_id']})
    $('<span>', { 'class':'glyphicon glyphicon-pencil'}).appendTo(div_odf_alias_name);
    div_odf_alias_name.appendTo(div_odf_tab_title);

    div_odf_column_content = $('<div>',{ 'class':'div-odf-column-content' });

    for(i=1;i<=f_info['df_info'].length;i++){
        div_odf_tab_content = $('<div>',{ 'class':'div-odf-item-content' });
        $('<label>',{ 'class':'label-odf', 'text':'y'+i.toString()}).appendTo(div_odf_tab_content);
        div_odf_tab_content.appendTo(div_odf_column_content);
    }


    div_odf_column_left = $('<div>',{ 'class':'div-odf-column-left' });
    div_odf_column_title.appendTo(div_odf_column_left);
    div_odf_tab_title.appendTo(div_odf_column_left);
    div_odf_column_content.appendTo(div_odf_column_left);
    //===


    // make div_odf_column_content start

    div_odf_column_content = $('<div>',{ 'class':'div-odf-column-content' });

    for(i=0;i<f_info['df_info'].length;i++){
        select = $('<select>',{ 'class':'label-odf-function'});

        for(j=0;j<f_info['df_mapping_function'].length;j++){

            if( f_info['df_info'][i][1] == f_info['df_mapping_function'][j][1]){
                $('<option>',{  'text':f_info['df_mapping_function'][j][0],
                                'name':f_info['df_mapping_function'][j][1],
                                'selected':'selected',
                }).appendTo(select);
            } else if( f_info['df_mapping_function'][j][0] == 'add new function'){
                $('<option>',{  'text':f_info['df_mapping_function'][j][0],
                                'name':'add_function',//f_info['odf_mapping_function'][j][1],
                                'style':'color:red',
                }).appendTo(select);
            }
            else {
                $('<option>',{  'text':f_info['df_mapping_function'][j][0],
                                'name':f_info['df_mapping_function'][j][1],
                }).appendTo(select);
            }
        }

        div_odf_tab_content_left = $('<div>',{ 'class':'div-odf-tab-content-left' });
        select.appendTo(div_odf_tab_content_left);

        div_odf_tab_content_right = $('<div>',{ 'class':'div-odf-tab-content-right' });
        div_odf_tab_normal_left = $('<div>',{ 'class':'div-odf-tab-normal-left' });
        $('<input>',{ 'class':'label-odf', 'type':'text', 'value':f_info['df_info'][i][2]}).appendTo(div_odf_tab_normal_left);
        div_odf_tab_normal_left.appendTo(div_odf_tab_content_right);

        div_odf_tab_normal_right = $('<div>',{ 'class':'div-odf-tab-normal-right' });
        $('<input>',{ 'class':'label-odf', 'type':'text', 'value':f_info['df_info'][i][3]}).appendTo(div_odf_tab_normal_right);
        div_odf_tab_normal_right.appendTo(div_odf_tab_content_right);


        div_odf_tab_content = $('<div>',{ 'class':'div-odf-tab-content' });
        div_odf_tab_content_left.appendTo(div_odf_tab_content);
        div_odf_tab_content_right.appendTo(div_odf_tab_content);
        div_odf_tab_content.appendTo(div_odf_column_content);
    }


    // make div_odf_column_content end

    // make div_odf_tab_title start

    div_odf_tab_title_left = $('<div>',{ 'class':'div-odf-tab-title-left'});
    label = $('<label>',{ 'for':'odf_function', 'class':'label-odf'});
    $('<a>',{ 'text':' Function', 'style':'color:black'}).appendTo(label);
    label.appendTo(div_odf_tab_title_left);

    div_odf_tab_title_right = $('<div>',{ 'class':'div-odf-tab-title-right'});

    // make div_odf_tab_title Min
    odf_tab_title_min = $('<div/>', { 'class': 'div-odf-tab-title-min'});
    label = $('<label>',{ 'for':'odf_min', 'class':'label-odf'});
    $('<a>',{ 'text':' Min', 'style':'color:black'}).appendTo(label);
    label.appendTo(odf_tab_title_min);

    // make div_odf_tab_title Max
    odf_tab_title_max = $('<div/>', { 'class': 'div-odf-tab-title-max'});
    label = $('<label>',{ 'for':'odf_max', 'class':'label-odf'});
    $('<a>',{ 'text':' Max', 'style':'color:black'}).appendTo(label);
    label.appendTo(odf_tab_title_max);

    div_odf_tab_title = $('<div>',{ 'class':'div-odf-tab-title' });
    div_odf_tab_title_left.appendTo(div_odf_tab_title);
    odf_tab_title_min.appendTo(div_odf_tab_title_right);
    odf_tab_title_max.appendTo(div_odf_tab_title_right);
    div_odf_tab_title_right.appendTo(div_odf_tab_title);

    // make div_odf_tab_title end

    div_odf_column_title = $('<div>',{ 'class':'df-module-title', 'style':'background-color:#BEBEBE', });
    odf_column_title_label = $('<div>',{ 'class':'label-odf', 'style':'height:37px', 'text':''});

    $('<button>', { 'class':'odf_setting_save single_save_button','text': 'Save',}).appendTo(odf_column_title_label);
    odf_column_title_label.appendTo(div_odf_column_title);

    // make div_odf_column_title end

    div_odf_column_right = $('<div>',{ 'class':'div-odf-column-right' });
    div_odf_column_title.appendTo(div_odf_column_right);
    div_odf_tab_title.appendTo(div_odf_column_right);
    div_odf_column_content.appendTo(div_odf_column_right);

    //////////////

    var odf_num = f_info['df_info'].length;
    div_odf_outer = $('<div>',{ 'class':'div-odf-outer', 'height':35*(2+odf_num)+3*2.5+1, });
    div_odf_column_left.appendTo(div_odf_outer);
    div_odf_column_right.appendTo(div_odf_outer);

    return div_odf_outer;
}


function make_single_idf_block_html(f_info){

    // div-idf-outer
    var idf_num = f_info['df_info'].length;
    var idf_outer = $('<div/>', {
        'class': 'div-idf-outer',
        'height': 35*(2+idf_num)+3*2.5,
    });
    
    //div-idf-column-left
    var idf_column_left = $('<div/>', {
        'class': 'div-idf-column-left',
    });

    //df-module-title
    var idf_column_title = $('<div/>', {
        'class': 'df-module-title',
    });
    idf_column_title_label = $('<label>', {
      'class':'label-idf',
      'text': f_info['df_module_title']+' (IDF)', //'Garmin Ring',
    });

    idf_column_title_label.appendTo(idf_column_title);

    idf_column_title.appendTo(idf_column_left);

    //div-idf-tab-title left + right
    var idf_tab_title = $('<div/>', {
        'class': 'div-idf-tab-title',
    });

    var idf_tab_title_left = $('<div/>', {
        'class': 'div-idf-tab-title-left',
    });
    var idf_tab_alias_name = $('<label>', {
        'class': 'label-idf',
        'text': f_info['alias_name'],//'Gravity',
        'name': f_info['df_id'],
    });
    $('<span>', { 'class':'glyphicon glyphicon-pencil'}).appendTo(idf_tab_alias_name);
    idf_tab_alias_name.appendTo(idf_tab_title_left);

    var idf_tab_title_right = $('<div/>', {
        'class': 'div-idf-tab-title-right',
    });
    $('<label>', {
        'class': 'label-idf',
        'text': 'Type',
    }).appendTo(idf_tab_title_right);

    idf_tab_title_left.appendTo(idf_tab_title);
    idf_tab_title_right.appendTo(idf_tab_title);
    idf_tab_title.appendTo(idf_column_left);

    //div-idf-column-content div-idf-tab-content left + right

    var idf_column_content = $('<div/>', {
        'class': 'div-idf-column-content',
        'height': idf_num*35,
    });

    // repeat N times
    var i;
    for(i=0;i<f_info['df_info'].length;i++){

        var idf_tab_content = $('<div/>', {
            'class': 'div-idf-tab-content',
        });

        var idf_tab_content_left = $('<div/>', {
            'class': 'div-idf-tab-content-left',
        });

        $('<label>', {
            'class': 'label-idf',
            'text': 'x'+(i+1).toString(),
        }).appendTo(idf_tab_content_left);

        var idf_tab_content_right = $('<div/>', {
            'class': 'div-idf-tab-content-right',
        });

        var type_selection = $('<select/>', {
          'class':'label-idf',
        });

        if( f_info['df_info'][i][0] == 'variant' ){
            $('<option/>', { 'text': 'variant', 'selected':'selected', }).appendTo(type_selection);
            $('<option/>', { 'text': 'sample', }).appendTo(type_selection);
        } else {
            $('<option/>', { 'text': 'variant', }).appendTo(type_selection);
            $('<option/>', { 'text': 'sample', 'selected':'selected', }).appendTo(type_selection);
        }

        type_selection.appendTo(idf_tab_content_right);
        idf_tab_content_left.appendTo(idf_tab_content);
        idf_tab_content_right.appendTo(idf_tab_content);
        idf_tab_content.appendTo(idf_column_content);
    }
    // End repeat N times

    idf_column_content.appendTo(idf_column_left);
    idf_column_left.appendTo(idf_outer);

// div-idf-column-right
    var idf_column_right = $('<div/>', {
        'class': 'div-idf-column-right',
    });

    // df-module-title
    var idf_column_title = $('<div/>', {
        'class': 'df-module-title',
        'style':'background-color:#BEBEBE',
    });
    idf_column_title_label = $('<div>', {
        'class': 'label-idf',
        'style': 'height:37px',
    });
    $('<button>', { 'class':'idf_setting_save single_save_button','text': 'Save',}).appendTo(idf_column_title_label);
    idf_column_title_label.appendTo(idf_column_title);

    idf_column_title.appendTo(idf_column_right);

    var idf_tab_title = $('<div/>', {
        'class': 'div-idf-tab-title',
    });

    // div-idf-tab-title min
    var idf_tab_title_min = $('<div/>', {
        'class': 'div-idf-tab-title-min',
    });

    var min_label = $('<label>', {
        'for': 'idf_min',
        'class': 'label-idf',
    });

    $('<a>', {
        'text': ' Min',
        'style': 'color: #000000',
    }).appendTo(min_label);

    min_label.appendTo(idf_tab_title_min);

    // div-idf-tab-title max
    var idf_tab_title_max = $('<div/>', {
        'class': 'div-idf-tab-title-max',
    });

    var max_label = $('<label>', {
        'for': 'idf_max',
        'class': 'label-idf',
    });

    $('<a>', {
        'text': ' Max',
        'style': 'color: #000000',
    }).appendTo(max_label);

    max_label.appendTo(idf_tab_title_max);

    // function_label.appendTo(idf_tab_title_function);
    idf_tab_title_min.appendTo(idf_tab_title);
    idf_tab_title_max.appendTo(idf_tab_title);
    idf_tab_title.appendTo(idf_column_right);

    // div-idf-column-content normalization + function normalizations
    var idf_column_content = $('<div/>', {
        'class': 'div-idf-column-content',
    });

    // Repeat N times
    for(i=0;i<f_info['df_info'].length;i++){
        var idf_tab_content_normalization = $('<div/>', {
            'class': 'div-idf-tab-content-normalization',
        });

        var idf_tab_normal_left = $('<div/>', {
            'class': 'div-idf-tab-normal-left',
        });
        $('<input>', {
            'type': 'text',
            'class': 'label-idf',
            'value': f_info['df_info'][i][2],//'11',
        }).appendTo(idf_tab_normal_left);

        var idf_tab_normal_right =$('<div/>', {
            'class': 'div-idf-tab-normal-right',
        });
        $('<input>', {
            'type': 'text',
            'class': 'label-idf',
            'value': f_info['df_info'][i][3],//'20',
        }).appendTo(idf_tab_normal_right);

        idf_tab_normal_left.appendTo(idf_tab_content_normalization);
        idf_tab_normal_right.appendTo(idf_tab_content_normalization);
        idf_tab_content_normalization.appendTo(idf_column_content);
    }
    // End repeat N times
    idf_column_content.appendTo(idf_column_right);
    idf_column_right.appendTo(idf_outer);
    
    return idf_outer;
}

function make_odf_module_html(info){

    var table = $('<table>', { 'class':'odf-module'});

    var title = $('<tr>', { 'class':'df-module-title'});
    $('<td>', { 'style':'border-right-style:hidden; width:33%', 'text':info['odf_module_title']+' (ODF)'}).appendTo(title);

    var odf_module_delete = $('<td>', {'colspan':'2'});
    $('<button>', {'class':'module-delete-button', 'text':'Delete'}).appendTo(odf_module_delete);
    odf_module_delete.appendTo(title);
    title.appendTo(table);

    var subtitle = $('<tr>');
    $('<td>', { 'colspan':'2', 'text':info['odf_alias_name'], 'class':'odf-module-name', 'name':info['odfo_id']}).appendTo(subtitle);
    //remove $('<td>', { 'colspan':'4', 'text':'Function'}).appendTo(subtitle);

    subtitle.appendTo(table);

    //remove for(i = 0; i < info['odf_info'].length; i++){
    //     var parameter = $('<tr>');
    //     $('<td>', { 'colspan':'2', 'text':'y'+(i+1)}).appendTo(parameter);

    //     var odf_module_func = $('<td>', { 'colspan':'4', 'class':'odf-module-func'});
    //     var func_select = $('<select>', {'class':'odf-module-select'});

    //     $.each(info['odf_mapping_function'], function(index, value){
    //         if( value[1] == info['odf_info'][i]){
    //             $('<option>', {'name':value[1], 'text':value[0], 'selected':'selected'}).appendTo(func_select);
    //         } else {
    //             $('<option>', {'name':value[1], 'text':value[0]}).appendTo(func_select);
    //         }
    //     });
    //     func_select.appendTo(odf_module_func);
    //     odf_module_func.appendTo(parameter);

    //     parameter.appendTo(table);
    // }

    return table;
}

function make_join_module_html(info){

    var table = $('<table>', { 'class':'join-module'});

    var title = $('<tr>', { 'class':'join-module-title'});
    $('<td>', { 'style':'width:33%', 'colspan':'2', 'text':'Input'}).appendTo(title);
    $('<td>', { 'style':'width:33%', 'colspan':'2', 'text':'IDF (Line)'}).appendTo(title);
    $('<td>', { 'style':'width:33%', 'colspan':'2', 'text':'Join Function'}).appendTo(title);
    title.appendTo(table);

    for(i = 0; i < info['join_index'].length; i++){
        var parameter = $('<tr>');
        $('<td>', { 'colspan':'2', 'text':'z'+(i+1)}).appendTo(parameter);

        var join_module_line = $('<td>', {'colspan':'2', 'class':'join-module-line'});
        var line_select = $('<select>', {'class':'join-module-select'});
        for(j = 1; j <= info['join_index'].length; j++){
            if( j == info['join_index'][i]){
                $('<option>', { 'text':j, 'selected':'selected'}).appendTo(line_select);
            } else {
                $('<option>', { 'text':j }).appendTo(line_select);
            }
        }
        line_select.appendTo(join_module_line);
        join_module_line.appendTo(parameter);

        if( i == 0){
            var join_module_func = $('<td>', {'colspan':'2', 'rowspan':info['join_index'].length, 'class':'join-module-func'});
            var func_select = $('<select>', {'class':'join-module-select'});

            $.each(info['join_function'], function(index, value){
                if( value[1] == info['join_fn_id']){
                    $('<option>', {'name':value[1], 'text':value[0], 'selected':'selected'}).appendTo(func_select);
                } else {
                    $('<option>', {'name':value[1], 'text':value[0]}).appendTo(func_select);
                }
            });

            func_select.appendTo(join_module_func);
            join_module_func.appendTo(parameter);
            parameter.appendTo(table);
        }
        parameter.appendTo(table);
    }

    return table;
}


function make_idf_module_html( info, num){
    var table = $('<table>', { 'class':'idf-module'});

    var title = $('<tr>', { 'class':'df-module-title'});
    $('<td>', { 'style':'border-right-style:hidden; width:33%','text': info['all_idf_module_title'][num]+' (IDF)'}).appendTo(title);

    var idf_module_delete = $('<td>', {'colspan':'2'});
    $('<button>', {'class':'module-delete-button', 'text':'Delete'}).appendTo(idf_module_delete);
    idf_module_delete.appendTo(title);
    title.appendTo(table);

    var subtitle = $('<tr>');
    $('<td>', { 'colspan':'2', 'text': info['all_idf_alias_name'][num], 'name':info['all_idfo_id'][num], 'class':'idf-module-name'}).appendTo(subtitle);

    //remove $('<td>', { 'style':'width:33%', 'text':'Type'}).appendTo(subtitle);
    //remove $('<td>', { 'style':'width:33%', 'text':'Function'}).appendTo(subtitle);
    subtitle.appendTo(table);

    //remove for(i = 0; i < info['all_idf_info'][num].length; i++){
    //     var parameter = $('<tr>');
    //     $('<td>', { 'text':'x'+(i+1)}).appendTo(parameter);
    //     var idf_module_type = $('<td>', {'class':'idf-module-type'});
    //     var type_select = $('<select>', {'class':'idf-module-select'});
    //     if( info['all_idf_info'][num][i] == 'sample'){
    //         $('<option>', { 'text':'sample', 'selected':'selected'}).appendTo(type_select);
    //         $('<option>', { 'text':'variant'}).appendTo(type_select);
    //     } else {
    //         $('<option>', { 'text':'sample'}).appendTo(type_select);
    //         $('<option>', { 'text':'variant', 'selected':'selected'}).appendTo(type_select);
    //     }
    //     type_select.appendTo(idf_module_type);
    //     idf_module_type.appendTo(parameter);

    //     //remove if( i == 0){ // IDF function 只要一個
    //     //     var idf_module_func = $('<td>', { 'colspan':'4', 'rowspan': info['all_idf_info'][num].length, 'class':'idf-module-func'});
    //     //     var func_select = $('<select>', {'class':'idf-module-select'});

    //     //     $.each(info['all_idf_mapping_function'][num], function(index, value){
    //     //         if( value[1] == info['all_idf_fn_id'][num]){
    //     //             $('<option>', {'name':value[1], 'text':value[0], 'selected':'selected'}).appendTo(func_select);
    //     //         } else {
    //     //             $('<option>', {'name':value[1], 'text':value[0]}).appendTo(func_select);
    //     //         }
    //     //     });
    //     //     func_select.appendTo(idf_module_func);
    //     //     idf_module_func.appendTo(parameter);
    //     // }
    //     parameter.appendTo(table);
    // }
    return table;
}

//remove function make_add_function_block_html(fn_info, df_id, df_type){
//     var div_add_function_outer = $('<div>', { 'class': 'div-add-function-outer', });

//     var div_prog_title = $('<div>', { 'class': 'div-program-title', });
//     prog_title_label = $('<label>', { 'class':'label-idf', 'text':'Function Management', 'name':df_id}).appendTo(div_prog_title);
//     $('<button>', { 'id':'function_cancel', 'class':'function_cancel close_button','text': 'Close',}).appendTo(prog_title_label);
//     prog_title_label.appendTo(div_prog_title);

//     div_prog_title.appendTo(div_add_function_outer);

//     var div_exist_block_left = $('<div>', { 'class': 'div-intro-block-left', });
//     div_exist_block_left.append("Global Function List:<br/> ");
//     var select_block = $('<select>', { 'class':'other_function_select',}).attr('size','4');
//     for( var i=0; i<fn_info['other_list'].length; i++){
//         $('<option>', { 'text': fn_info['other_list'][i][0], 'name':fn_info['other_list'][i][1], }).appendTo(select_block);
//     }
//     select_block.appendTo(div_exist_block_left);
//     div_exist_block_left.appendTo(div_add_function_outer);


//     var div_exist_block_middle = $('<div>', { 'class': 'div-intro-block-middle', });

//     var div_intro_block_side = $('<div>', { 'class': 'div-intro-block-middle-side',});
//     div_intro_block_side.appendTo(div_exist_block_middle);

//     var div_intro_block_content = $('<div>', { 'class': 'div-intro-block-middle-content',});
//     $('<input>', { 'type':'button', 'id':'add_function', 'value':'>>>', 'class':'function_edit', }).appendTo(div_intro_block_content);
//     $('<input>', { 'type':'button', 'id':'remove_function', 'value':'<<<', 'class':'function_edit', }).appendTo(div_intro_block_content);
//     div_intro_block_content.appendTo(div_exist_block_middle);

//     var div_intro_block_side2 = $('<div>', { 'class': 'div-intro-block-middle-side',});
//     div_intro_block_side2.appendTo(div_exist_block_middle);

//     div_exist_block_middle.appendTo(div_add_function_outer);


//     var div_exist_block_right = $('<div>', { 'class': 'div-intro-block-right', 'name':df_type});
//     div_exist_block_right.append(fn_info['df_name']+" Function List:<br/> ");
//     var select_block = $('<select>', { 'class':'exist_function_select', }).attr('size','4');
//     for( var i=0; i<fn_info['quick_list'].length; i++){
//         if( fn_info['quick_list'][i][0] == 'add new function'){            // is plus
//             $('<option>', { 'text': fn_info['quick_list'][i][0], 'name':fn_info['quick_list'][i][1], 'style':'color:red'}).appendTo(select_block);
//         } else if( fn_info['quick_list'][i][2] == '0'){     // is draft
//             $('<option>', { 'text': fn_info['quick_list'][i][0], 'name':fn_info['quick_list'][i][1], 'style':'color:green;font-weight:bold'}).appendTo(select_block);
//         } else {
//             $('<option>', { 'text': fn_info['quick_list'][i][0], 'name':fn_info['quick_list'][i][1], }).appendTo(select_block);
//         }
//     }
//     select_block.appendTo(div_exist_block_right);

//     div_exist_block_right.appendTo(div_add_function_outer);


//     $('<hr>',{'style':'margin:10px; width:100%', 'size':'4'}).appendTo(div_add_function_outer);

//     return div_add_function_outer;
// }

function make_log_block_html(log_data){
    var div_log_block_outer = $('<div>', { 'class': 'div-add-function-outer', });

    var div_prog_title = $('<div>', { 'class': 'div-program-title', });
    var prog_title_label = $('<label>', { 'class':'label-idf', 'text':'Log Monitor'}).appendTo(div_prog_title);
    prog_title_label.appendTo(div_prog_title);

    div_prog_title.appendTo(div_log_block_outer);

    var div_intro_block = $('<div>', { 'class': 'div-intro-block', });
    $('<br>').appendTo(div_intro_block);
    $('<br>').appendTo(div_intro_block);
    $('<textarea>', {
        'class':'input-program-block',
        'style':'min-height:80%',
        'text': log_data, }).appendTo(div_intro_block);

    div_intro_block.appendTo(div_log_block_outer);

    return div_log_block_outer;
}

//remove function make_edit_function_block_html(function_name, function_content){
//     var div_intro_block = $('<div>', { 'class': 'div-intro-block', });
//     div_intro_block.append("Selected Function: ");
//     $('<input>', { 'name': '0', 'class':'function_name', 'style':'margin:5px', 'type':'text', 'value':function_name }).appendTo(div_intro_block);
//     $('<br>').appendTo(div_intro_block);

//     div_intro_block.append("Version: ");
//     var select_block = $('<select>', { 'class': 'select-dmc-df', });
//     select_block.appendTo(div_intro_block);
//     $('<input>', { 'type':'button', 'id':'delete_function', 'value':'Delete', 'class':'function_edit', }).appendTo(div_intro_block);
//     $('<input>', { 'type':'button', 'id':'function_add', 'value':'Save', 'class':'function_edit', }).appendTo(div_intro_block);
//     $('<br>').appendTo(div_intro_block);

//     div_intro_block.append("Include non-DF arguments ");
//     // <input> name:1 表示需要新增版本 name:0 表示不用新增版本
//     $('<input>', { 'type':'checkbox', 'id':'is_switch', 'style':'margin:5px', 'name':'1'}).appendTo(div_intro_block);
//     $('<textarea>', {
//         'class':'input-argument-block disable-flag',
//         'text':'',
//     }).appendTo(div_intro_block);
//     $('<br>').appendTo(div_intro_block);

//     if( function_content == ""){
//         function_content = "def run():\n\n    return";
//     }

//     $('<textarea>', {
//         'class':'input-program-block',
//         'text':function_content, }).appendTo(div_intro_block);
//     window['input-program-block'] = function_content;
//     if( window.myCodeMirror )
//         window.myCodeMirror.getDoc().setValue(function_content);

//     return div_intro_block;

// }

