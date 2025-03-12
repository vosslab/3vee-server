<?php

/*
**
**
*/

$progname = "Solvent Extractor";
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
	$javascript .= "
		<script>
		function ribosome(obj) {
		  obj.pdbid.value = '1jj2';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '8.0';
		  obj.smallprobe.value = '3.4';
		  return;
		}
		function lysozyme(obj) {
		  obj.pdbid.value = '2lyz';
		  obj.biounit.checked = false;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = false;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = true;

		  obj.bigprobe.value = '6.0';
		  obj.smallprobe.value = '1.5';
		  return;
		}
		</script>\n";

	writeTop($progname,$progname,$javascript,$extra);


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
	echo "<input type='submit' name='process' value='Start Solvent Extract'><br />";
	echo "  </td>";
	echo "</tr>";

	// Preset examples
	echo "<tr>";
	echo "	<td colspan='2' align='center'>";
	echo "<hr/>";
	echo "PRESET EXAMPLES:";
	echo "&nbsp;<input type='button' onClick='ribosome(this.form)'"
	." value='50S Ribosomal Subunit'>\n";
	echo "&nbsp;<input type='button' onClick='lysozyme(this.form)'"
	." value='Lysozyme'>\n";
	echo "  </td>";
	echo "</tr>";

	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('runSolvent', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

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
	$command = $PROCDIR."py/runSolvent.py ";
	$command.=" --bigprobe=$bigprobe";
	$command.=" --smallprobe=$smallprobe";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
