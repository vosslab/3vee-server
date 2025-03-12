<?php

/*
**
**
*/

$progname = "Tunnel Extractor";
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
	$_POST['pdbid'] = '1jj2';
	$_POST['gridres'] = 'medium';

	$javascript = "<script src='js/viewer.js'></script>";
	$javascript .= writeJavaPopupFunctions('threev');

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";

	// reload set params
	$bigprobe = ($_POST['bigprobe']) ? $_POST['bigprobe'] : '8';
	$smallprobe = ($_POST['smallprobe']) ? $_POST['smallprobe'] : '3.4';

	echo "<table width='480' border='1'><tr><td>\n";
	echo "WARNING: At this time, the exit tunnel extractor only works on
		the Haloarcula marismortui structures of the ribosome. This is because
		each ribosome structure uses its own coordinate system. In my thesis, I
		calculated the transformation matrices for the different ribosome
		structures, but as of yet it is not implemented in this program.\n";
	echo "</td></tr></table>\n";

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
	showRecentRuns('runTunnel', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>$progname</b> &ndash;
		this program is a special program for extract the exit tunnel
		from the <i>H.marismortui</i> ribosome structure: PDB 1jj2.

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
		createForm('<b>ERROR:</b> Small probe is larger than big probe');
		exit(1);
	}

	// write command
	$command = $PROCDIR."py/runTunnel.py ";
	$command.=" --bigprobe=$bigprobe";
	$command.=" --smallprobe=$smallprobe";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
