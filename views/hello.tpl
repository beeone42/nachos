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
<div>First, let's <a href='{{url}}'>check your identity on the intranet...</a></div>
</body>
</html>