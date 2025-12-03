<html><head><title>PHP Example</title></head>
<body>
You are using <?php echo $_SERVER['HTTP_USER_AGENT']; ?><br/>
and coming from <?php echo $_SERVER['REMOTE_ADDR']; ?><br/>

<?php echo getcwd()."<BR/>"; ?>
<?php 
 $cmd = "`sleep 5; echo '".$_SERVER['REMOTE_ADDR']."' >> neil2.txt` > /dev/null 2>&1 &";
 $cmd = "sleep 5 > /dev/null 2>&1 &";
 system($cmd);
 //popen($cmd);
 //passthru($cmd);
 echo $cmd."<BR/>"; 
 //$cmd2 = "`sleep 5; nslookup ".$_SERVER['REMOTE_ADDR']." >> neil2.txt` > /dev/null 2>&1 &";
 //exec($cmd2); 
 //passthru($cmd2); 
 //popen($cmd2, 'w'); 
 //echo $cmd2."<BR/>"; 
 //shell_exec("./test.py"); 
?>

</body></html>

