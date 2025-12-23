<?php

/*
***************************************
***************************************
***************************************
*************************************** 
*/

require "inc/processing.inc";

// IF VALUES SUBMITTED, EVALUATE DATA
if (!$_POST['process']) {
	selectStructure();
} elseif ($_POST['process']=="Choose a Structure") { // Create the form page
	selectProcess();
} else {
	selectStructure();
}

/*
****************************************
****************************************
****************************************
**************************************** 
*/

function getPDBInfo($pdbfile) {
	echo "PDB file: $pdbfile<br/>\n";
	$numatoms = 0;
	$numhetero = 0;
	$minmax = array(1000,1000,1000,-1000,-1000,-1000);
	$handle = fopen($pdbfile, "r");
	while (!feof($handle)) {
		$line = fgets($handle);
		$prefix = substr($line, 0, 6);
		if ($prefix == "ATOM  ")
			$numatoms++;
		elseif ($prefix == "HETATM")
			$numhetero++;
		if ($prefix == "ATOM  " || $prefix == "HETATM") {
			$x = (int) substr($line, 30, 4);
			$y = (int) substr($line, 38, 4);
			$z = (int) substr($line, 46, 4);
			//echo "$x, $y, $z<br/>\n";
			if ($x < $minmax[0]) $minmax[0]=$x;
			if ($y < $minmax[1]) $minmax[1]=$y;
			if ($z < $minmax[2]) $minmax[2]=$z;
			if ($x > $minmax[3]) $minmax[3]=$x;
			if ($y > $minmax[4]) $minmax[4]=$y;
			if ($z > $minmax[5]) $minmax[5]=$z;
		}
		//echo $buffer;
	}
	$volume = ($minmax[3]-$minmax[0])*($minmax[4]-$minmax[1])*($minmax[5]-$minmax[2]);
	echo "Num atoms: $numatoms<br/>\n";
	echo "Num hetero: $numhetero<br/>\n";
	echo "Min/Max: ".print_r($minmax)."<br/>\n";
	echo "Box volume: $volume &Aring;<sup>3</sup><br/>\n";
	$pdbstr = "Num atoms:";
	return $pdbstr;
}

/*
****************************************
****************************************
****************************************
**************************************** 
*/
function selectStructure($extra=false) {
	// setup a jobid
	$jobid = getJobId();
	$formAction=$_SERVER['PHP_SELF']."?jobid=$jobid";

	$progname = "Choose a Structure";
	$javascript = "<script src='js/viewer.js'></script>";
	$javascript .= writeJavaPopupFunctions('threev');	

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo "<font color='red'>$extra</font>\n<hr>\n";
	}
  
	$helpdiv = "
	<div id='dhelp'
		style='position:absolute; 
		background-color:FFFFDD;
		color:black;
		border: 1px solid black;
		visibility:hidden;
		z-index:+1'
		onmouseover='overdiv=1;'
		onmouseout='overdiv=0;'>
	</div>\n";
	echo $helpdiv;

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";
	echo csrf_field();
	echo "<input type='hidden' name='jobid' value='$jobid'/>&nbsp;";

	// reload set params
	$pdbid = ($_POST['pdbid']) ? $_POST['pdbid'] : '';

	echo"
	<p>
	<table border='0' class='tableborder'>
	<tr>
		<td valign='top'>
		<table cellpadding='10' border='0'>
		<tr>";
	echo "<td valign='top'>";

	// First column

	// Input file
	echo "<b>Input structure:</b><br/>";
	echo docpop('upload','Upload PDB file to process<br/>');
	echo "<input type='hidden' name='MAX_FILE_SIZE' value='30000000' />";
	echo "<input type='file' name='uploadpdb' size='30' maxlength='250'/></br>";
	echo docpop('pdbid','Enter PDB ID to process<br/>');
	echo "<input type='text' name='pdbid' size='4' value='$pdbid'/>&nbsp;";
	echo "<br/><br/>";

	// Hetero atoms
	echo "<input type='checkbox' name='hetero' $hetero/>";
	echo docpop('hetero','Use hetero atoms?');
	echo "<br/><br/>";

	// Biological coordiantes
	echo "<input type='checkbox' name='biological' $biological/>";
	echo docpop('biological','Biological coordiantes?');

	echo "<br/>";

	// End input

	echo "</td></tr>\n</table>\n";

	echo "</td></tr>";
	echo "<tr>";
	echo "	<td colspan='2' align='center'>";
	echo "	<hr>";
	echo "<input type='submit' name='process' value='$progname'><br />";
	echo "  </td>";
	echo "</tr>";
	echo "</table>";
	echo "</form>";

	echo "</center>\n";
	writeBottom();
	exit;
}

/*
****************************************
****************************************
****************************************
**************************************** 
*/
function selectProcess($extra=false) {
	global $PROCDIR;
	$progname = "Cavity Extractor";
	$pdbid  = post_pdbid();
	$hetero = post_flag_value('hetero');
	$hostip = $_SERVER['REMOTE_ADDR'];
	if (!filter_var($hostip, FILTER_VALIDATE_IP)) {
		$hostip = '';
	}
	$jobid  = post_jobid();
	$uploaddir = $PROCDIR.'output/uploads/';
	$formAction=$_SERVER['PHP_SELF']."?jobid=$jobid";

	// make sure pdb id was selected
	if (!$pdbid && !$_FILES['uploadpdb']['name']) { 
		selectStructure('<b>ERROR:</b> No pdbid selected');
		exit;
	} elseif ($_FILES['uploadpdb']['name']) {
		$upload_error = validate_pdb_upload($_FILES['uploadpdb']);
		if ($upload_error) {
			selectStructure('<b>ERROR:</b> '.$upload_error);
			exit;
		}
		$uploadfile = $uploaddir . $jobid . ".pdb";
		if (!move_uploaded_file($_FILES['uploadpdb']['tmp_name'], $uploadfile)) {
			selectStructure('<b>ERROR:</b> Possible file upload attack!');
			exit;
		}
		echo $uploadfile;
		$pdbfile = $uploadfile;
	} elseif ($pdbid) {
		$uploadfile = $uploaddir . $jobid . ".pdb.gz";
		$pdburl =  "https://files.rcsb.org/download/".$pdbid.".pdb.gz";
		$command = "wget ".escapeshellarg($pdburl)." -O ".escapeshellarg($uploadfile);
		$command.=" > ".escapeshellarg("/var/www/html/3vee/output/running/shell-$jobid.log")." 2>&1";
 		$command.=" ;";
		//echo $command."<br/>\n";
		system($command);
		$command2 =" gunzip -v ".escapeshellarg($uploadfile)." > ".escapeshellarg("/var/www/html/3vee/output/running/shell-$jobid.log")." 2>&1";
		//echo $command2."<br/>\n";
		system($command2);
		$pdbfile = $uploaddir . $jobid . ".pdb";
	}
	getPDBInfo($pdbfile);

	$progname = "Choose Methods";
	$javascript = "<script src='js/viewer.js'></script>";
	$javascript .= writeJavaPopupFunctions('threev');	

	writeTop($progname,$progname,$javascript);
	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

	echo "<form name='threevform' method='post' action='$formAction' enctype='multipart/form-data'>\n";
	echo csrf_field();
	echo "<input type='hidden' name='jobid' value='$jobid'/>&nbsp;";

	// SHOW Structure information
	echo "<table border='0' width='640'><tr><td align='left'><h3>
		<b>Structure information</b> &ndash;\n";
	if ($pdbid) {
		echo "PDB id: $pdbid\n";
	} else {
		echo "File: ".basename($_FILES['uploadpdb']['name'])."\n";
	}
	echo "</h3></td></tr></table><br/>";

	echo"
	<p>
	<table border='0' class='tableborder'>
	<tr>
		<td valign='top' colspan='3'>";

	// Start input area
	echo "
		<table cellpadding='10' border='0'>
		<tr>";
	echo "<td valign='top'>";

	// First column

	// Grid resolution
	echo "<b>Grid resolution:</b>";
	echo "<input type='radio' name='gridres' value='crude'/>crude";
	echo "<input type='radio' name='gridres' value='low' checked/>low";
	echo "<input type='radio' name='gridres' value='medium'/>medium";
	echo "<input type='radio' name='gridres' value='high'/>high";
	echo "<br/><br/>";

	// End column

	echo "<br/></td></tr>\n</table>\n";
	echo "</td>";
	echo "<td class='tablebg'>";
	echo "<table cellpadding='5' border='0'>";
	echo "<tr><td valign='TOP'>\n";

	// Second column

	// Big probe
	echo docpop('probe','Outer probe radius:');
	echo "<br/><input type='text' name='bigprobe' size='4' value='$bigprobe'>";
	echo "<br/><br/>";

	// Small probe
	echo docpop('probe','Inner probe radius:');
	echo "<br/><input type='text' name='smallprobe' size='4' value='$smallprobe'>";
	echo "<br/><br/>";

	// End column

	echo "<br/></td></tr>\n</table>\n";

	echo "</td></tr>";
	echo "<tr colspan='2'>";
	echo "	<td align='center'>";
	echo "	<hr>";
	echo "<input type='submit' name='process' value='$progname'><br />";
	echo "  </td>";
	echo "</tr>";
	echo "</table>";
	echo "</form>";

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

?>
