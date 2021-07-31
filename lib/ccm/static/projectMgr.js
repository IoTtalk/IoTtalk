function delete_project(p_id, name) {
      var ajax_obj = $.ajax({
          url: '/delete_project',
          type:'POST',
          data: {p_id:p_id},
      }).done(function(){
            console.log (name + 'has been deleted.');
            location.reload();
        }).fail(function(result){
            console.log('Fail to delete project ' + name + '. error code:' + result);
           });
      return ajax_obj.status == 200;
}

function reset_project_password(p_id, name) {
  let pwd = prompt("Entre new password: ", '');
  while(true){
    if (!pwd && !confirm('Are you sure to use a blank password?')) {
      pwd = prompt("Entre new password: ", '');
      continue;
    }
    break;
  }
  $.ajax({
    url: '/reset_project_password',
    type: 'POST',
    data: {p_id: p_id, p_pwd: pwd},
  }).done(function(){
    alert(name + '\'s password has been reset.');
  }).fail(function(result){
    console.log('Fail to reset project "' + name + '" password. \n' + result);
  });
}

function open_project(p_name){
      var url = 'http://' + window.location.hostname + ':7788/connection#' + p_name;
      window.open(url, '_blank');
}

function ajax_restart_project(p_id){
    $.ajax({
        url: '/restart_project',
        type:'POST',
        data: {p_id:p_id},
    });
}

function ajax_turn_on_project(p_id){
      $.ajax({
          url: '/turn_on_project',
          type:'POST',
          data: {p_id:p_id},
      }).done(function(){ajax_restart_project(p_id);});
}

function ajax_turn_off_project(p_id){
      $.ajax({
          url: '/turn_off_project',
          type:'POST',
          data: {p_id:p_id},
      });
}

function ajax_turn_on_simulation(p_id){
      $.ajax({
          url: '/turn_on_simulation',
          type:'POST',
          data: {p_id:p_id},
      }).done(function(){ajax_restart_project(p_id);});
}

function ajax_turn_off_simulation(p_id){
      $.ajax({
          url: '/turn_off_simulation',
          type:'POST',
          data: {p_id:p_id},
      });
}

function turn_on(p_id, type){
    if(type == 'p'){
        ajax_turn_on_project(p_id);
        setTimeout(function(){location.reload();}, 3000);
    }
    else if (type =='s'){
        ajax_turn_on_simulation(p_id);
        setTimeout(function(){location.reload();}, 3000);
    }
}

function turn_off(p_id, type){
    if(type == 'p'){
        ajax_turn_off_project(p_id);
    }
    else if (type =='s'){
        ajax_turn_off_simulation(p_id);
    }
}

function status_fig(_status_, html_id, p_id){
    if (_status_ == 'on'){ 
        $('#'+html_id).attr('src', '/static/images/green_dot.png');	    
    }
    else{
        $('#'+html_id).attr('src', '/static/images/red_dot.png');	    
    }

    $('#'+html_id).on('click', function(e) {
        var st = $(this).attr('src');
        st = st.split('/');
        if (st[3] == 'red_dot.png') {
            turn_on(p_id, html_id[0]);
            $('#'+html_id).attr('src', '/static/images/green_dot.png');
        }
        else{
            turn_off(p_id, html_id[0]);
            $('#'+html_id).attr('src', '/static/images/red_dot.png');
        }
    });
}	  

function exception_fig(_exception_, html_id){
    if (_exception_.length > 0){
        $('#'+html_id).attr('src', '/static/images/alert.png');	    

        $('#'+html_id).on('click', function(e){
            var alert_div = $('<div>', {'id':'alert-dialog', 'title':'Exception Message'});
            $('<textarea>',{
		    'text':_exception_, 
		    'class':'form-control', 
		    'rows':"20", 
		    'style':"min-width: 630px", 
		    'disabled':'disabled'
	    }).appendTo(alert_div);
            alert_div.dialog({
               closeOnEscape: true,
               position: {my: 'top', at: 'top+150'},
               modal: true,
               resizable: false		    ,
               width: 660,
               dialogClass: '.alert-class',
            });
            $('.ui-dialog-titlebar').css('background','rgb(57, 97, 113)');
            $('.ui-dialog-title').css('color', '#FFFFFF');	
	    $('.ui-dialog-title').css('font-size', '110%');
            $('.ui-widget-header').css('border','#087CE7');		
        });
    }
}  
