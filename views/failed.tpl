<html>
<head>
<title>Guacamole: Redirect...</title>
% include('style.tpl')
<script>
setTimeout(function() {
    window.location.replace("{{url}}");
}, 3000);
</script>
</head>
<body>
<div>Intranet AUTH Failed... <a href='{{url}}'>Try again...</a></div>
</body>
</html>
