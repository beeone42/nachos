<html>
<head>
<title>Guacamole: Reset password</title>
% include('style.tpl')
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
<script>

  $(function() { setTimeout(function(){

  $('form').submit(function(event){
  event.preventDefault();

  form_data = $(this).serialize();
  
  var post_url = $(this).attr("action"); //get form action url
  var form_data = $(this).serialize(); //Encode form elements for submission

  
  
  $.post( post_url, form_data, function( response ) {
  alert( response );
  window.location.replace('/');
  });
  
  });
  
  $('#sub').prop( "disabled", false );
  
  }, 1000);
  });


</script>
</head>
<body>
  <div>

    <big>{{infos['displayname']}}</big>
    <br />
    <span>
      ({{infos['campus'][0]['country']}} / {{infos['campus'][0]['city']}})
    </span><br />

    <form method="POST" action="set">
      <input name='login' id='login' type='text' value='{{infos['login']}}' disabled><br />
      <input name='password' type="password" id="password" value="" required><br />
      <input name='token' id='token' value='{{token}}' type='hidden'>
      
      <input class="buttons" type='submit' id='sub' value='Set Password' disabled>
      
      <hr />
      <a href='{{url}}'>
	<small>Token: {{token}}</small>
      </a>
      <br />

    </form>

  </div>
</body>
</html>
