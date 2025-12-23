<?php

require "inc/processing.inc";

$title = "3v Source Code";
writeTop($title,$title,'');

$vossvolvox_repo = "https://github.com/vosslab/vossvolvox";
$threev_repo = "https://github.com/vosslab/3vee-server";

echo "<table border='0' cellpading='3'><tr><td align='left'>\n";

echo "<ul>\n";
echo "<li><h3>source code repositories</h3>\n";
echo "  <table border='0' cellspacing='10'><tr><td>\n";
echo "  <h4>Vossvolvox (C++ CLI processing)</h4>";
echo "  <ul>\n";
echo "     <li><a href='$vossvolvox_repo'>GitHub repository</a>\n";
echo "  </ul>\n";
echo "  <pre>\n";
echo "git clone $vossvolvox_repo\n";
echo "  </pre>\n";
echo "  <h4>3vee-server (web UI + Podman container)</h4>";
echo "  <ul>\n";
echo "     <li><a href='$threev_repo'>GitHub repository</a>\n";
echo "  </ul>\n";
echo "  <pre>\n";
echo "git clone $threev_repo\n";
echo "  </pre>\n";
echo "  <h4>Archive snapshot</h4>";
echo "  <ul>\n";
echo "     <li><a href='vossvolvox-1.3.tgz'>local copy</a>\n";
echo "  </ul>\n";
echo "  </td></tr></table>\n";
echo "  </ul>\n";

echo "</td></tr></table>\n";

writeBottom();
exit;

?>

