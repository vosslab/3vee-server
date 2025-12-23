
<?php

/*************************
**************************
*************************/
function tail_file($file, $lines) {
	if (!$handle = fopen($file, "r")) {
		return "";
	}
	$linecounter = $lines;
	$pos = -2;
	$beginning = false;
	$text = array();
	while ($linecounter > 0) {
		$t = " ";
		while ($t != "\n") {
			if(fseek($handle, $pos, SEEK_END) == -1) {
				$beginning = true; 
				break; 
			}
			$t = fgetc($handle);
			$pos --;
		}
		$linecounter --;
		if ($beginning) {
			rewind($handle);
		}
		$text[$lines-$linecounter-1] = fgets($handle);
		if ($beginning) break;
	}
	fclose ($handle);
	$linearray = array_reverse($text);
	$cleanlines = "";
	foreach ($linearray as $line) {
		$line = trim($line);
		if (strlen($line) > 130)
			$line = substr($line,0,100)." ... ".substr($line, -25);
		$cleanlines .= $line."\n";
	}
	return $cleanlines;
};

/*************************
**************************
*************************/
function streamToArray($stream) {
  // turns a stream into an array of arrays
  $lines=explode("\n", $stream);
  foreach($lines as $line) {
    if (!$line=trim($line))
      continue;
    $fields=explode(" ",$line);
    $row=array();
    foreach($fields as $f) {
      if (!trim($f))
	continue;
      $row[]=$f;
    }
    $rows[]=$row;
  }
  return $rows;
}

/*************************
**************************
*************************/
function checkLogFile($logfile, $tail) {
	if (!file_exists($logfile)) {
		return array();
	}
	$r = tail_file($logfile, $tail);
	return streamToArray($r);
}

/*************************
**************************
*************************/
function convertAnsiCodeToHtml($matches) {
	global $ANSI_SPAN_OPEN;
	$codes = explode(';', $matches[1]);
	$reset = in_array('0', $codes, true);
	$color = null;
	foreach ($codes as $code) {
		switch ($code) {
			case '30':
				$color = 'black';
				break;
			case '31':
				$color = 'red';
				break;
			case '32':
				$color = 'green';
				break;
			case '33':
				$color = 'yellow';
				break;
			case '34':
				$color = 'blue';
				break;
			case '35':
				$color = 'magenta';
				break;
			case '36':
				$color = 'cyan';
				break;
			case '37':
				$color = 'white';
				break;
		}
	}
	$output = '';
	if ($reset && $ANSI_SPAN_OPEN) {
		$output .= "</span>";
		$ANSI_SPAN_OPEN = false;
	}
	if ($color) {
		if ($ANSI_SPAN_OPEN) {
			$output .= "</span>";
			$ANSI_SPAN_OPEN = false;
		}
		$output .= "<span class='ansi-color' style='color:$color'>";
		$ANSI_SPAN_OPEN = true;
	}
	return $output;
};

function convertToColors($j) {
	global $ANSI_SPAN_OPEN;
	$ANSI_SPAN_OPEN = false;
	$line = "";
	$linelen = 0;
	foreach ($j as $i) {
		$i = trim($i);
		$i = preg_replace_callback("/\033\[([0-9;]+)m/", "convertAnsiCodeToHtml", $i);
		$line .= "$i ";
		$linelen = $linelen + strlen($i) + 1;
		if ($linelen > 100) {
			$linelen = 0;
			$line .= "\n";
		}
	}
	if ($ANSI_SPAN_OPEN) {
		$line .= "</span>";
		$ANSI_SPAN_OPEN = false;
	}
	return $line;
};

/*************************
**************************
*************************/
function writeJobTable($jobid) {
	require_once "inc/threevdata.inc";
	$threevdata = new threevdata();
	$jobdata = $threevdata->getJobData($jobid);
	if (!is_array($jobdata))
		$jobdata = array();
	$jobparams = $threevdata->getJobParams($jobid);
	//echo print_r($jobparams);

	echo "<table class='resultstable'>\n";
	echo "	<tr><td colspan='3' align='center'><h3>Run Information</h3></td></tr>\n";

	// pdb id
	$pdbid = $jobparams['pdbid'];
	if($pdbid && $pdbid != "None") {
		echo "	<tr><td>".docpop('pdbid','PDB id:')."</td> <td align='right'>"
			."<a href='http://www.rcsb.org/pdb/explore/explore.do?structureId=$pdbid'>"
			.$jobparams['pdbid']
			."&nbsp;<img border='0' src='img/external.png'>"
			."</a></td></tr>\n";
	}

	// biounit
	$biounit = !empty($jobdata['biounit'])
		? "<span style='color:#229922;'>yes</span>"
		: "<span style='color:#992222;'>no</span>";
	echo "	<tr><td>".docpop('biounit','biological unit:')."</td> <td align='right'>$biounit</td></tr>\n";

	// hetero
	$hetero = !empty($jobdata['hetero'])
		? "<span style='color:#229922;'>yes</span>"
		: "<span style='color:#992222;'>no</span>";
	echo "	<tr><td>".docpop('hetero','use hetero atoms:')."</td> <td align='right'>$hetero</td></tr>\n";

	// allow use
	$allowuse = !empty($jobdata['allowuse'])
		? "<span style='color:#229922;'>yes</span>"
		: "<span style='color:#992222;'>no</span>";
	echo "	<tr><td>".docpop('allowuse','allow public display:')."</td> <td align='right'>$allowuse</td></tr>\n";

	echo "	<tr><td>".docpop('gridres','grid resolution:')."</td> <td align='right'>".$jobparams['gridres']."</td></tr>\n";

		echo "	<tr><td colspan='3'></td></tr>\n";	
	$badkeys = array('gridsize', 'allowuse', 'hetero', 'jobid', 
		'biounit', 'hostip', 'rundir', 'gridres', 'pdbid', 'coord_list');
	foreach ($jobparams as $k=>$v) {
		if (in_array($k, $badkeys))
			continue;
		if (!$v || $v == "None")
			continue;
		echo "	<tr><td>".docpop($k,$k.':')."</td> <td align='right'>$v</td></tr>\n";	
	}

	// path
	//echo "	<tr><td>path:</td> <td align='right'>".$jobparams['rundir']."</td></tr>\n";

	echo "</table><hr/><hr/><br/>\n";
};

/*************************
**************************
*************************/
function showResults($jobid, $showrunlog) {
	global $PROCDIR;
	$formAction=$_SERVER['PHP_SELF']."?jobid=$jobid";
	if($showrunlog)
		$formAction.="&showrunlog=1";
	$title = "3v Results for JobId ".$jobid;
	$heading = "3v Results for JobId <i>'".$jobid."'</i>";
	$jobdir = preg_replace("/\./", "/", $jobid);

	$javascript = "<script src='js/viewer.js'></script>";
	$javascript .= writeJavaPopupFunctions('threev');
	writeTop($title,$heading,$javascript);
	writeJobTable($jobid);
	echo "<h4><a href='$formAction&showrunlog=1'>Show running log</a></h4>\n";
	$resultsfile = $PROCDIR."output/$jobdir/results-".$jobid.".html";
	include($resultsfile);
	echo "<h4><a href='$formAction&showrunlog=1'>Show running log</a></h4>\n";
};

/*************************
**************************
*************************/
function runningLog($jobid, $showrunlog) {
	global $PROCDIR;
	$formAction=$_SERVER['PHP_SELF']."?jobid=$jobid";
	if($showrunlog)
		$formAction.="&showrunlog=1";
	$title = "3v Running Log for JobId ".$jobid;
	$heading = "3v Running Log for JobId <i>'".$jobid."'</i>";
	$jobdir = preg_replace("/\./", "/", $jobid);
	$runningfile = $PROCDIR."output/$jobdir/runlog-".$jobid.".html";
	$resultsfile = $PROCDIR."output/$jobdir/results-".$jobid.".html";

	$javascript  = "<meta http-equiv='refresh' content='30' />\n";
	$javascript .= "<script language='javascript'>\n<!--\n";
	$javascript .= "var URL 'viewResults.php?jobid=$jobid'\n";
	$javascript .= "var speed 2000\n";
	$javascript .= "function reload() {\nlocation = URL\n}\n";
	$javascript .= "setTimeout('reload()', speed);\n";
	$javascript .= "//-->\n</script>\n";
	writeTop($title,$heading,$javascript);

	echo "<style type='text/css'>\n";
	echo "li.Check {\nlist-style-image: url('img/icon-check.png')\n}\n";
	echo "li.Star {\nlist-style-image: url('img/icon-bluestar.png')\n}\n";
	echo "li.Cross {\nlist-style-image: url('img/icon-cross.png')\n}\n";
	echo ".terminal-shell { background-color: #000022; }\n";
	echo ".terminal-output { color: #ffffff; font-size: 0.9em; margin: 0; }\n";
	echo "</style>\n";
	echo "<h2>Program is still running, progress is shown below</h2>";
	if (file_exists($resultsfile) && filesize($resultsfile) > 1)
		echo "<h4><a href='$formAction&showrunlog=0'>Show unfinished results</a></h4>\n";

	echo "<table><tr><td align='left'><h4><ul>\n";
	include($runningfile);
	echo "</ul></h4></td></tr></table>\n";
	echo "<h4>hit reload to refresh this page</h4>\n";

	$logfile = $PROCDIR."output/$jobdir/shell-$jobid.log";
	$tail = isset($_POST['tail']) && $_POST['tail'] !== '' ? (int)$_POST['tail'] : 20;
	$loginfo = checkLogFile($logfile, $tail);
	if ($loginfo) {
		echo "<br/><hr width='50%'/>\n";
		echo "<table border='0' width='750' cellpadding='3'>\n";
		echo "<tr><td align='center' valign='top'>\n";
		echo "<h2>Log file display</h2>\n";
		echo "<form name='jobform' method='post' action='$formAction'>\n";
		echo csrf_field();
		echo "Show last <input type='text' name='tail' size='4' value='$tail'> lines of log file&nbsp;\n";
		echo "<input type='submit' name='checkjob' value='Update Status'><br />\n";
		//echo basename($logfile)."</td></tr>\n";
		echo "<tr><td>\n";
		echo "	<table class='tablebg' border='5' width='750' cellpadding='0'>\n";
		echo "	<tr><td>\n";
		echo "		<pre>Terminal display</pre>\n";
		echo "	</td></tr>\n";
	echo "	<tr><td class='terminal-shell'>\n";
	echo "		<pre class='terminal-output'>\n";
	foreach ($loginfo as $l) {
		$colored = convertToColors($l);
		echo "$colored\n";
	}
	echo "		</pre>\n";
		echo "	</td></tr></table>\n";
		echo "</td></tr></table>\n";
		echo "</form>\n";
	}
};


/*************************
**************************
*************************/
function preLog($jobid) {
	require_once "inc/threevdata.inc";
	global $PROCDIR;
	$formAction=$_SERVER['PHP_SELF']."?jobid=$jobid";
	$title = "3v Preparing for JobId ".$jobid;
	$heading = "3v Preparing for JobId <i>'".$jobid."'</i>";
	$jobdir = preg_replace("/\./", "/", $jobid);

	$javascript  = "<meta http-equiv='refresh' content='5' />\n";
	writeTop($title,$heading,$javascript);
	echo "<table><tr align='left'><td>\n";
	echo "<h2>Job Id, '<i>$jobid</i>' was not found or has not started yet</h2>";
	echo "<h4>Sometime it can take a few seconds to start</h4> ";
	echo "<h4>Check these log files and email Neil "
		."&lt;<i>vossman77 [at] Yahoo! [dot] com</i>&gt;, if there is a problem</h4>";
	echo "<ul>\n";
	if (file_exists($PROCDIR."output/$jobdir/shell-$jobid.log"))
		echo "  <li>Shell log: <span style='font-size:smaller;'><a href='output/$jobdir/shell-$jobid.log'>"
			.$PROCDIR."output/$jobdir/shell-$jobid.log</a></span>\n";
	if (file_exists($PROCDIR."output/$jobdir/runlog-$jobid.html"))
		echo "  <li>Running log: <span style='font-size:smaller;'><a href='output/$jobdir/runlog-$jobid.html'>"
			.$PROCDIR."output/$jobdir/runlog-$jobid.html</a></span>\n";
	if (file_exists($PROCDIR."output/$jobdir/results-$jobid.html"))
		echo "  <li>Results html: <span style='font-size:smaller;'><a href='output/$jobdir/results-$jobid.html'>"
			.$PROCDIR."output/$jobdir/results-$jobid.html</a></span>\n";
	echo "</ul>\n";
	echo "</td></tr></table>\n";
}

/*************************
**************************
*************************/
global $PROCDIR;
require_once "inc/processing.inc";

$jobid = get_jobid();
//$datestamp = substr($jobid, 0, 7);
$jobdir = preg_replace("/\./", "/", $jobid);
$runningfile = $PROCDIR."output/$jobdir/runlog-".$jobid.".html";
$resultsfile = $PROCDIR."output/$jobdir/results-".$jobid.".html";
$showrunlog = isset($_GET['showrunlog']) ? (int)$_GET['showrunlog'] : 0;

if (!$jobid) {
	preLog($jobid);
} elseif (file_exists($resultsfile) && filesize($resultsfile) > 10 && $showrunlog!=1) {
	showResults($jobid, $showrunlog);
} elseif (file_exists($runningfile)) {
	runningLog($jobid, $showrunlog);
} else {
	preLog($jobid);
}

writeBottom();
exit;

?>
