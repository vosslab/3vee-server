<?php

/*
**
**
*/

$progname = "Channel Extractor";
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
		function exit_tunnel(obj) {
		  obj.pdbid.value = '1jj2';
		  obj.biounit.checked = false;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = false;
		  obj.gridres[1].checked = true;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '9.0';
		  obj.smallprobe.value = '3.4';
		  obj.x.value = '56';
		  obj.y.value = '140';
		  obj.z.value = '74';
		  return;
		}
		function chaperon(obj) {
		  obj.pdbid.value = '1a6d';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '40.0';
		  obj.smallprobe.value = '5.0';
		  obj.x.value = '0';
		  obj.y.value = '0';
		  obj.z.value = '0';
		  return;
		}
		function groel(obj) {
		  obj.pdbid.value = '1pcq';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '35.0';
		  obj.smallprobe.value = '6.0';
		  obj.x.value = '80';
		  obj.y.value = '-50';
		  obj.z.value = '-15';
		  return;
		}
		function pgp(obj) {
		  obj.pdbid.value = '3g5u';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = false;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = true;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '9.0';
		  obj.smallprobe.value = '3.5';
		  obj.x.value = '24';
		  obj.y.value = '68';
		  obj.z.value = '16';
		  return;
		}
		</script>\n";

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";

	// reload set params
	$bigprobe = ($_POST['bigprobe']) ? $_POST['bigprobe'] : '10';
	$smallprobe = ($_POST['smallprobe']) ? $_POST['smallprobe'] : '3';
	$x = ($_POST['x']) ? $_POST['x'] : '0';
	$y = ($_POST['y']) ? $_POST['y'] : '0';
	$z = ($_POST['z']) ? $_POST['z'] : '0';

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

	echo docpop('coordinate','X,Y,Z coordinate in solvent:');
	echo "<br/><input type='text' name='x' size='4' value='$x'>";
	echo "<input type='text' name='y' size='4' value='$y'>";
	echo "<input type='text' name='z' size='4' value='$z'>";
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
	echo "&nbsp;<input type='button' onClick='exit_tunnel(this.form)'"
	." value='Ribosome Exit Tunnel'>\n";
	echo "&nbsp;<input type='button' onClick='chaperon(this.form)'"
	." value='Chaperonin Internal Chamber'><br/>\n";
	echo "&nbsp;<input type='button' onClick='groel(this.form)'"
	." value='GroEL/ES Internal Chamber'>\n";
	echo "&nbsp;<input type='button' onClick='pgp(this.form)'"
	." value='P-glycoprotein pocket'>\n";
	echo "  </td>";
	echo "</tr>";

	echo "</table>";
	echo "</form>";

	echo "</td><td>\n";
	showRecentRuns('runChannel', 3);
	echo "</td></tr>\n";
	echo "</table>\n";

	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>$progname</b> &ndash;
		possible the most useful program here. The channel extractor
		can pull interesting channels out from a structure. For example,
		the exit tunnel from the ribosome, the internal cavity of GroEL
		and many others.

		Channel extractor works by calculating the shell volume (A) and
		then subtracts the solvent-excluded volume (B) from the shell volume
		(A) the resulting volume is the solvent volume (C). Next it only takes
		the solvent volume that is connected to a point specified by you.
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
	$x = (float) $_POST['x'];
	$y = (float) $_POST['y'];
	$z = (float) $_POST['z'];

	// check probe sizes
	if ($bigprobe < $smallprobe) {
		createForm('<b>ERROR:</b> Small probe is larger than big probe');
		exit(1);
	}

	// write command
	$command = $PROCDIR."py/runChannel.py ";
	$command.=" --bigprobe=$bigprobe";
	$command.=" --smallprobe=$smallprobe";
	$command.=" --coord=$x,$y,$z";

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
