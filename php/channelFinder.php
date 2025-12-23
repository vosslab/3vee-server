<?php

/*
**
**
*/

$progname = "Channel Finder";
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

	$javascript = "<script src='js/viewer.js'></script>\n";
	$javascript .= writeJavaPopupFunctions('threev');
	$javascript .= "
		<script>
		function exit_tunnel(obj) {
		  obj.pdbid.value = '1jj2';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '8.0';
		  obj.smallprobe.value = '3.4';
		  obj.minvolume.value = '1000';
		  obj.minpercent.value = '';
		  obj.numchan.value = '';
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
		  obj.minvolume.value = '2000';
		  obj.minpercent.value = '';
		  obj.numchan.value = '';
		  return;
		}
		function mechchan(obj) {
		  obj.pdbid.value = '2oar';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = false;
		  obj.gridres[1].checked = true;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '13.0';
		  obj.smallprobe.value = '2.0';
		  obj.minvolume.value = '4000';
		  obj.minpercent.value = '';
		  obj.numchan.value = '';
		  return;
		}
		function ferritin(obj) {
		  obj.pdbid.value = '1lb3';
		  obj.biounit.checked = true;
		  obj.hetero.checked = false;
		  obj.gridres[0].checked = true;
		  obj.gridres[1].checked = false;
		  obj.gridres[2].checked = false;
		  obj.gridres[3].checked = false;

		  obj.bigprobe.value = '40.0';
		  obj.smallprobe.value = '3.0';
		  obj.minvolume.value = '20000';
		  obj.minpercent.value = '';
		  obj.numchan.value = '';
		  return;
		}
		</script>\n";

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";
	echo csrf_field();

	// reload set params
	$bigprobe = ($_POST['bigprobe']) ? $_POST['bigprobe'] : '10';
	$smallprobe = ($_POST['smallprobe']) ? $_POST['smallprobe'] : '3';
	$minvolume = ($_POST['minvolume']) ? $_POST['minvolume'] : '';
	$minpercent = ($_POST['minpercent']) ? $_POST['minpercent'] : '';
	$numchan = ($_POST['numchan']) ? $_POST['numchan'] : '2';

	echo "<table border='0' cellpading='10' cellspacing='10'><tr><td>\n";
	echo"
	<p>
	<table border='0' class='tableborder'>
	<tr>
		<td valign='top'>
		<table cellpadding='10' border='0'>
		<tr>\n";
	echo "<td valign='top'>\n";

	// First column
	echo firstColumn();
	// End column

	echo "<br/></td></tr>\n</table>\n";
	echo "</td>\n";
	echo "<td class='tablebg'>\n";
	echo "<table cellpadding='5' border='0'>\n";
	echo "<tr><td valign='TOP'>\n";

	// Second column

	// Big probe
	echo docpop('bprobe','Outer probe radius:');
	echo "<br/><input type='text' name='bigprobe' size='4' value='$bigprobe'>\n";
	echo "<br/><br/>\n";

	// Small probe
	echo docpop('sprobe','Inner probe radius:');
	echo "<br/><input type='text' name='smallprobe' size='4' value='$smallprobe'>\n";
	echo "<br/><br/>\n";


	// Channel filtering
	echo "<table style='border:solid; border-width:2px; border-color:#949088;' cellspacing='10'><tr><td>\n";

	echo "<b>Choose one of the following options:</b>\n";

	echo "</td></tr><tr><td>\n";

	echo docpop('minvolume','Minimum accessible volume of a channel:');
	echo "<br/><input type='text' name='minvolume' size='4' value='$minvolume'> &Aring;<sup>3</sup>\n";

	echo "</td></tr><tr><td>\n";

	echo docpop('minpercent','Minimum percentage of total volume:');
	echo "<br/><input type='text' name='minpercent' size='4' value='$minpercent'> %";

	echo "</td></tr><tr><td>\n";

	echo docpop('numchan','Get the N largest channels:');
	echo "<br/><input type='text' name='numchan' size='4' value='$numchan'> channels";

	echo "</td></tr></table>\n";

	// End column

	echo "<br/></td></tr>\n</table>\n";

	echo "</td></tr>\n";
	echo "<tr>\n";
	echo "	<td colspan='2' align='center'>\n";
	echo "	<hr>\n";
	echo "<input type='submit' name='process' value='Start $progname'><br />\n";
	echo "  </td>\n";
	echo "</tr>\n";

	// Preset examples
	echo "<tr>\n";
	echo "	<td colspan='2' align='center'>\n";
	echo "<hr/>\n";
	echo "PRESET EXAMPLES:";

	echo "&nbsp;<input type='button' onClick='pgp(this.form)'"
	." value='P-glycoprotein pocket'>\n";
	echo "&nbsp;<input type='button' onClick='mechchan(this.form)'"
	." value='Mechanosensitive channel'>\n";
	echo "<br/>\n";
	echo "&nbsp;<input type='button' onClick='ferritin(this.form)'"
	." value='Ferritin internal chamber'>\n";
	echo "&nbsp;<input type='button' onClick='exit_tunnel(this.form)'"
	." value='50S Ribosomal Subunit'>\n";
	echo "  </td>\n";
	echo "</tr>\n";

	echo "</table>\n";
	echo "</form>\n";

	echo "</td><td>\n";
	showRecentRuns('runChannelFinder', 3);
	echo "</td></tr>\n";
	echo "</table>\n";


	echo "
	<br/><br/>
	<table border='0' width='640'><tr><td align='left'><h3>
		<b>$progname</b> &ndash;
		possible the most useful program here. The channel finder
		can pull interesting channels out from a structure. For example,
		the exit tunnel from the ribosome, the internal cavity of GroEL
		and many others.

		Channel finder works by calculating the shell volume (A) and
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
	$bigprobe = post_float_value('bigprobe', 6.0);
	$smallprobe = post_float_value('smallprobe', 2.0);
	$minvolume = post_int_value('minvolume', 0);
	$minpercent = post_float_value('minpercent', 0);
	$numchan = post_int_value('numchan', 0);

	// check probe sizes
	if ($bigprobe < $smallprobe) {
		createForm('<b>ERROR:</b> Small probe is larger than big probe');
		exit(1);
	}

	// check for some input
	if (!$minvolume && !$minpercent && !$numchan) {
		createForm('<b>ERROR:</b> Please enter one of min volume, min percent or number of channels');
		exit(1);
	}

	// write command
	$command = $PROCDIR."py/runChannelFinder.py ";
	$command.=" --bigprobe=".escapeshellarg($bigprobe);
	$command.=" --smallprobe=".escapeshellarg($smallprobe);
	if($numchan)
		$command.=" --numchan=".escapeshellarg($numchan);
	else if($minvolume)
		$command.=" --minvolume=".escapeshellarg($minvolume);
	else if($minpercent)
		$command.=" --minpercent=".escapeshellarg($minpercent);

	$error = launchJob($command, $progname);
	if ($error)
		createForm("<b>ERROR:</b> $error");
	exit(1);
}
?>
