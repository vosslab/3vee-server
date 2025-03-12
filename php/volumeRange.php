<?php

/*
**
**
*/

require "inc/processing.inc";

$progname = "Volume Probe Range";

// IF VALUES SUBMITTED, EVALUATE DATA
if ($_POST['process']) {
	runThreeVProgram();
} else { // Create the form page
	createForm();
}

function createForm($extra=false) {
	global $progname;
	$formAction=$_SERVER['PHP_SELF'];
	$javascript .= writeJavaPopupFunctions('threev');
	$javascript .= "
		<script>
		function lysozyme(obj) {
		  obj.pdbid.value = '2lyz';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = false;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = true;

		  obj.probe.value = '3.0';
		  return;
		}
		function ribosome(obj) {
		  obj.pdbid.value = '1jj2';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.probe.value = '6.0';
		  return;
		}
		</script>\n";

	writeTop($progname, $progname, $javascript, $extra);
	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";

	// reload set params
	$minprobe = ($_POST['minprobe']) ? $_POST['minprobe'] : '0';
	$maxprobe = ($_POST['maxprobe']) ? $_POST['maxprobe'] : '9';
	$probestep = ($_POST['probestep']) ? $_POST['probestep'] : '3';

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

	// Minimum Probe radius
	echo docpop('minprobe','Minimum probe radius:');
	echo "<br/><input type='text' name='minprobe' size='4' value='$minprobe'>";
	echo "<br/><br/>";

	// Maximum Probe radius
	echo docpop('maxprobe','Maximum probe radius:');
	echo "<br/><input type='text' name='maxprobe' size='4' value='$maxprobe'>";
	echo "<br/><br/>";


	// Probe radius step size
	echo docpop('probestep','Probe radius step size:');
	echo "<br/><input type='text' name='probestep' size='4' value='$probestep'>";
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

	// Preset examples
	echo "<tr>";
	echo "	<td colspan='2' align='center'>";
	echo "<hr/>";
	echo "PRESET EXAMPLES:";
	echo "&nbsp;<input type='button' onClick='lysozyme(this.form)'"
	." value='Lysozyme'>\n";
	echo "&nbsp;<input type='button' onClick='ribosome(this.form)'"
	." value='50S Ribosomal Subunit'>\n";
	echo "  </td>";
	echo "</tr>";

	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('runVolumeRange', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

	echo "
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>$progname</b> &ndash;
		this program calculates the volume of your
		macromolecule of interest.

		By rolling a virtual probe on the surface of
		your macromolecule a volume is calculated
	</h3></td></tr></table><br/>
	<img src='img/richards.png' alt='rolling probe'>
	";

	echo "</center>\n";
	writeBottom();
	exit(1);
}

function runThreeVProgram() {
	// get common variables
	global $PROCDIR;
	global $progname;
	$minprobe = $_POST['minprobe'];
	$maxprobe = $_POST['maxprobe'];
	$probestep = $_POST['probestep'];

	// check probe sizes
	if ($maxprobe < $minprobe) {
		createForm('<b>ERROR:</b> Minimum probe is larger than maximum probe');
		exit(1);
	}

	// write command line
	$command = $PROCDIR."py/runVolumeRange.py ";
	$command.=" --minprobe=$minprobe";
	$command.=" --maxprobe=$maxprobe";
	$command.=" --probestep=$probestep";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
