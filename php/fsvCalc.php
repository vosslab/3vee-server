<?php

/*
**
**
*/

$progname = "Fraction Solvent Volume Calculator";
require "inc/processing.inc";

// IF VALUES SUBMITTED, EVALUATE DATA
if ($_POST['process']) {
	runThreeVProgram();
} else { // Create the form page
	createForm();
}

function createForm($extra=false, $title='Fraction Solvent Volume Calculator', $heading='Fraction Solvent Volume Calculator') {
	global $progname;
	$formAction=$_SERVER['PHP_SELF'];
	writeTop($progname, $progname, $javascript, $extra);
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
	echo "<input type='submit' name='process' value='Start FSV Calc'><br />";
	echo "  </td>";
	echo "</tr>";
	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('runFSVCalc', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>Fraction Solvent Volume (FSV) Calculator</b> &ndash;
		this program calculates the percentage of solvent contained inside your
		macromolecule of interest.

		The Fraction Solvent Volume value is calculated by taking the
		reduced solvent volume (D) divided by the shell volume (A).

		It was found that
		large RNA structures on average have an FSV of greater than 30%,
		smaller RNAs have an FSV of 9.2%,
		single domain proteins have an FSV of 3.8 &plusmn; 3.4%,
		and multi-domain proteins have an FSV of 14.0 &plusmn; 4.7%.
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
	$command = $PROCDIR."py/runFSVCalc.py ";
	$command.=" --bigprobe=$bigprobe";
	$command.=" --smallprobe=$smallprobe";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
