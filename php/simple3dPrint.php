<?php

/*
**
**
*/

require "inc/processing.inc";

$progname = "Simple 3d Printer Prep";

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
	$javascript .= print3dJavaFunctions();
	$javascript .= "
		<script type=\"text/javascript\">
		function lysozyme_solvent(obj) {
		  obj.pdbid.value = '2lyz';
		  obj.biounit.checked = false;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.probe.value = '3.0';
		  return;
		</script>\n";
			
	writeTop($progname, $progname, $javascript, $extra);
	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";

	// reload set params
	$probe = ($_POST['probe']) ? $_POST['probe'] : '3';

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
	echo firstColumn($print3d=true);
	// End column

	echo "<br/></td></tr>\n</table>\n";
	echo "</td>";
	echo "<td class='tablebg'>";
	echo "<table cellpadding='5' border='0'>";
	echo "<tr><td valign='TOP'>\n";

	// Second column

	// Probe radius
	echo docpop('probe','Probe radius:');
	echo "<br/><input type='text' name='probe' size='4' value='$probe'>";
	echo "<br/><br/>";

	echo print3dColumn();

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
	echo "&nbsp;<input type='button' onClick='lysozyme_solvent(this.form)'"
	." value='Lysozyme - Solvent Excluded'>\n";
	echo "  </td>";
	echo "</tr>";

	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('simple3dPrint', 3);
	echo "</td></tr>\n";
	echo "</table>\n";


	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>$progname</b> &ndash;
		this program calculates the volume of your
		macromolecule of interest.

		By rolling a virtual probe on the surface of
		your macromolecule a volume is calculated
	</h3></td></tr></table><br/>
	<a href='img/grid_vs_probe.jpg'>
	<img src='img/grid_vs_probe_sm.jpg' width=526 height=451 alt='grid resolution and probe size'><br/>
	difference between grid size and probe size</a>
	";

	echo "</center>\n";
	writeBottom();
	exit(1);
}

function runThreeVProgram() {
	// get common variables
	global $PROCDIR;
	global $progname;
	$probe = $_POST['probe'];

	// write command line
	$command = $PROCDIR."py/simple3dPrint.py ";
	$command.=" --probe=$probe";

	$error = launchJob($command, $progname, $print3d=true);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
