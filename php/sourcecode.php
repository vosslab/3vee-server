<?php

require "inc/processing.inc";

$title = "3v Source Code";
writeTop($title,$title,'');

$sflink = "http://downloads.sourceforge.net/project/vossvolvox/vossvolvox/version%201.3/3v-1.3.tgz?use_mirror=softlayer";
$sflink = "http://sourceforge.net/projects/vossvolvox/files/";

echo "<table border='0' cellpading='3'><tr><td align='left'>\n";

echo "<ul>\n";

echo "<li><h3>github repository</h3>\n";
echo "  <table border='0' cellspacing='10'><tr><td>\n";
echo "    Just type:<br/>\n";
echo "    <pre>\n";
//echo "svn checkout svn://svn.code.sf.net/p/vossvolvox/code/ vossvolvox/\n";
echo "git clone https://github.com/vosslab/vossvolvox.git\n";
echo "    </pre>\n";
echo "  </td></tr></table>\n";


echo "<li><h3>packaged version of the source code</h3>\n";
echo "  <table border='0' cellspacing='10'><tr><td>\n";
echo "  <h4> OLD 3v: Voss Volume Voxelator, version 1.3</h4>";
echo "  <ul>\n";
echo "     <li><a href='vossvolvox-1.3.tgz'>local copy</a>\n";
echo "     <li><a href='$sflink'>sourceforge copy</a>\n";
echo "     <li>do not download this version it is old, I recommend using the code in subversion.\n";
echo "  </ul>\n";
echo "  </td></tr></table>\n";

echo "  </ul>\n";

echo "</td></tr></table>\n";

writeBottom();
exit;

?>


