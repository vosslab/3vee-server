<?php

/*
**
**
*/

$progname = "Cavity Extractor";
require "inc/processing.inc";

// IF VALUES SUBMITTED, EVALUATE DATA
if ($_POST['process']) {
	runThreeVProgram();
} else { // Create the form page
	createForm();
}

function createForm($extra=false) {
	global $progname;
	$formAction=$_SERVER['PHP_SELF'];

	$javascript = "<script src='js/viewer.js'></script>";
	$javascript .= writeJavaPopupFunctions('threev');

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";

	// reload set params
	$bigprobe = ($_POST['bigprobe']) ? $_POST['bigprobe'] : '10';
	$smallprobe = ($_POST['smallprobe']) ? $_POST['smallprobe'] : '3';

	echo "<table border='0' cellpading='10' cellspacing='10'><tr><td>";
	echo"
	<p>
	<table border='0' class='tableborder'>
	<tr>
		<td valign='top'>
		<table cellpadding='10' border='0'>
		<tr>";
	echo "<td valign='top'>";

	// First column
	echo firstColumn();
	// End column

	echo "<br/></td></tr>\n</table>\n";
	echo "</td>";
	echo "<td class='tablebg'>";
	echo "<table cellpadding='5' border='0'>";
	echo "<tr><td valign='TOP'>\n";

	// Second column

	// Big probe
	echo docpop('bprobe','Outer probe radius:');
	echo "<br/><input type='text' name='bigprobe' size='4' value='$bigprobe'>";
	echo "<br/><br/>";

	// Small probe
	echo docpop('sprobe','Inner probe radius:');
	echo "<br/><input type='text' name='smallprobe' size='4' value='$smallprobe'>";
	echo "<br/><br/>";

	// End column

	echo "<br/></td></tr>\n</table>\n";

	echo "</td></tr>";
	echo "<tr>";
	echo "	<td colspan='2' align='center'>";
	echo "	<hr>";
	echo "<input type='submit' name='process' value='Start $progname'><br />";
	echo "  </td>";
	echo "</tr>";
	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('runCavity', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>Cavity Extractor</b> &ndash;
		a cavity is a contained area within a volume such that a
		spherical probe cannot escape.

		The cavities are found by calculating the shell volume (A)
		or any related volume and then locating all the disconnected
		volumes inside
	</h3></td></tr></table><br/>
	<img src='img/solvent.png' width='675'>
	";

	echo "</center>\n";
	writeBottom();
	exit;
}

function runThreeVProgram() {
	// get variables
	global $PROCDIR;
	global $progname;
	$bigprobe = $_POST['bigprobe'];
	$smallprobe = $_POST['smallprobe'];

	// check probe sizes
	if ($bigprobe < $smallprobe) {
		createForm("<b>ERROR:</b> Small probe is larger than big probe");
		exit(1);
	}

	// write command
	$command = $PROCDIR."py/runCavity.py ";
	$command.=" --bigprobe=$bigprobe";
	$command.=" --smallprobe=$smallprobe";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
