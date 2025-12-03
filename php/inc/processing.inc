<?php

/**
 *	The Leginon software is Copyright 2006 
 *	The Scripps Research Institute, La Jolla, CA
 *	For terms of the license agreement see
 *	@licence http://ami.scripps.edu/software/leginon-license
 */
/**
 *	Query definition to access all leginon data 
 *	
 */

require_once "inc/threevdata.inc";

$PROCDIR = "/var/www/html/3vee/";
$PYTHONDIR = $PROCDIR."py/";

/*************************************/
// add commas to an int
function commafy($input) {
   if(strlen($input)<=3) { 
		return $input;
   }
   $length=substr($input,0,strlen($input)-3);
   $formatted_input = commafy($length).",".substr($input,-3);
   return $formatted_input;
};

/*************************************/
// write popup function 'a href'
function docpop($key,$text) {
	return "	<a href='#".$key."' id='l".$key."' onMouseOver='popLayer(\"".$key."\",\"l".$key."\")'"
		." onMouseOut='hideLayer()'>\n"
		."		$text</a>\n";
};

/*************************************/
// write popup function 'a href'
function showRecentRuns($progname=false, $count=3) {
	$threevdata = new threevdata();
	$recentruns = $threevdata->getMostRecentRuns($count*3, $progname);
	//print_r($recentruns);
	if($recentruns) {
		echo "<br/>\n";
		echo "<table border='0' class='tableborder'>\n";
		echo "<tr><td>\n";
		echo "  <h3>Recent runs</h3>\n";
		echo "</td></tr><tr><td align='center'>\n";
		$runcount = 0;
		foreach($recentruns as $rundata) {
			//print_r($rundata);
			$runid = $rundata['DEF_id'];
			$runparams = $threevdata->getRunParams($runid);
			//print_r($runparams);
			//print $rundata['path'];
			$pngfiles = glob($rundata['path']."/*.png");
			if (!$pngfiles)
				continue;
			$runcount++;
			if ($runcount > $count)
				break;
			echo "  <hr/>\n";
			$jobid = $rundata['jobid'];
			$pdbid = $runparams['pdbid'];
			//echo $rundata['path']."/*.png";
			shuffle($pngfiles);
			$pngcount = 0;
			foreach ($pngfiles as $pngfile) {
				$pngcount ++;
				if ($pngcount > 3)
					break;
				$pngurl = ereg_replace('.*output/', 'output/', $pngfile);
				echo "<a href='$pngurl'>\n";
				echo "  <img src='$pngurl' height='80'>\n";
				echo "</a>\n";
			}
			echo "<br/>";
			echo "  Job id: <a href='viewResults.php?jobid=$jobid'>$jobid</a>\n";
			if ($pdbid && $pdbid != "None")
				echo "  PDB id: <a href='http://www.rcsb.org/pdb/explore/explore.do?structureId=$pdbid'>$pdbid</a>\n";
			echo "  &nbsp;<img border='0' src='img/external.png'><br/>\n";
			if(!$progname) {
				$runprogname = $rundata['progname'];
				echo "  Program: $runprogname<br/>\n";
			}
			//echo "<br/>\n";
		}
		if ($runcount < 1)
			echo "no runs found\n";
		echo "</td></tr></table>\n";
	} else {
		//echo "No recent runs";
	}
};

/*************************************/
function writeTop($title, $heading=false, $javascript=false, $extra=false, $popup=true) {
	if ($popup)
		$javascript .= writeJavaPopupFunctions('threev');

	global $_GET;
  	echo "<html>\n";
	echo "<head>\n";
	echo "<title>$title</title>\n";
	echo "<link rel='stylesheet' type='text/css' href='css/viewer.css'> \n";
	//echo "<link rel='stylesheet' type='text/css' href='css/view.css'> \n";
	echo "<link rel='stylesheet' type='text/css' href='css/proc.css'> \n";
	echo "$javascript\n";
	// google analytics
	echo "
<script type='text/javascript'>

  var _gaq = _gaq || [];
  _gaq.push(['_setAccount', 'UA-21593629-1']);
  _gaq.push(['_trackPageview']);

  (function() {
    var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
    ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
    var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
  })();

</script>
";
	echo "</head>\n";
	echo "<body onload='initmenu()'>\n";
	echo "<center>\n";
	echo "<!-- header -->\n";
	echo "<div id='apheader'>\n";
	echo "  <div class='aptopbar'></div>\n";
	echo "  <table border='0' cellpadding='5' cellspacing='5' >\n";
	echo "    <tr><td valign='middle' align='center'>\n";
	echo "       <a href='index.php'><img src='img/topbarbackgrnd.png' border='0' height='51'></a>\n";
   echo "    </td><td valign='middle' align='center'>\n";
	echo "       <b><font size='+2'>$heading</font></b>\n";
   echo "    </td></tr>\n";
	echo "  </table>\n";
	echo "  <div class='aptopbar'></div>\n";
	echo "</div>\n";
	// for help popup documentation
	$helpdiv = "
	<div id='dhelp'
		style='position: absolute; 
        	background-color: #fff2d7;
        	color: black;
        	border: 1px solid gray;
        	visibility: hidden;
        	text-align: left;
        	z-index:+4'
    		onmouseover='overdiv=1;'
    		onmouseout='overdiv=0;'>
	</div>\n";
	if ($popup)
		echo $helpdiv;

	// write out errors, if any came up:
	if ($extra) {
		echo makeErrorMsg($extra);
	}

};

/*************************************/
function writeBottom($showproclink=True){
	//global $_GET;
	echo "<br/>\n";
	echo "<div id='apheader'>\n";
	echo "  <div class='aptopbar'></div>\n";
	echo "</div><br/>\n";
	echo "
	<table cellspacing='15' cellpading='5'><tr><td>

	<font size='+1'>Citation:</font> <br/>
   <i><a href='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2896178/'>
      '3V: cavity, channel and cleft volume calculator and extractor'</a></i> (free text)<br/>
		Nucleic Acids Res. 2010 July 1; 38(Web Server issue): W555–W562<br/>
      by Neil R. Voss and Mark Gerstein
	
	</td></tr><tr><td>

	<font size='+1'><a href='sourcecode.php'>Download source code</a></font>

	</td></tr><tr><td>

	<font size='+1'><a href='glossary.php'>Help</a></font>

	</td></tr><tr><td>

	<font size='+1'><a href='news.php'>Site news and updates</a></font>

	</td></tr><tr><td>

	<font size='-1'>
		If you find this useful or want more functionality 
		please contact Neil &lt;vossman77 [at] yahoo.com&gt;</font>

	</td></tr></table>
	";
/*
	</td></tr><tr><td>

	<h4>References:</h4>
		<ol><font size=-1>
			<li>NR Voss, M Gerstein, TA Steitz, PB Moore.<BR>
			<i>'The geometry of the ribosomal polypeptide exit tunnel.'</I><BR>
			J Mol Biol. v360 (4): 2006, pp. 893-906.<BR>
			<a href='voss-jmb2006.pdf'>download pdf</a>
			&nbsp;&nbsp;&nbsp;
			Pubmed ID: <A HREF='http://www.ncbi.nlm.nih.gov/entrez/query.fcgi?"
			."cmd=Retrieve&db=PubMed&list_uids=16784753&otool=yalelib&dopt=Abstract'>16784753</A>

			<li>NR Voss<BR>
			<i>'Geometric Studies of RNA and Ribosomes, and Ribosome 
			Crystallization'</i><br/>
			PhD dissertation, Yale University, 2007<br/>
			<a href='voss-thesis.pdf'>download pdf</a>
		</font></ol>
*/

	echo "<center><table border='0' cellpadding='0' cellspacing='0'>\n";
	echo "<tr>\n";
	echo "<td valign='center'>\n";
	echo "<a href='index.php' class='header'>\n";
	echo "<img border='0' src='img/leftendButton.gif'>\n";
	echo "</a>\n";
	echo "</td>\n";
	echo "<td align='center' valign='center' background='img/middleButton.gif'>\n";
	echo "<a href='index.php' class='header'><font size='-2'> back to main page </font></a>\n";
	echo "</td>\n";
	echo "<td valign='top'>\n";
	echo "<img border='0' src='img/rightendButton.gif'>\n";
	echo "</td>\n";
	echo "</tr>\n";
	echo "</table></center>\n";

	echo "</center>\n";
	echo "</body>\n";
	echo "</html>\n";
};



/*************************************/
function pleaseWaitJava() {
	$java = "<script type=\"text/javascript\" >\n";
	$java.= "function pleasewait() {\n";
	$java.= "	pleasewaitScreen=$('pleasewaitScreen');\n";
	$java.= "	pleasewaitScreen.style.visibility='visible';\n";
	$java.= "}\n"; 
	$java.= "</script>\n";
	return $java;
};

/*************************************/
function writeJavaPopupFunctions ($help) {
	$javafunc = "
  <style type='text/css'>
	input { border-style: solid; border-color: #9dae9b; }
	select { border-style: solid; border-color: #9dae9b; }

		span.info {
			width: 100px;
		}
  </style>\n";

	//next three lines are required for pop up help
	$javafunc .= "
  <script type='text/javascript' src='js/help.js'></script>
  <script type='text/javascript' src='js/draglayer.js'></script>
  <script type='text/javascript' src='js/prototype.js'></script>\n";
	$javafunc .= "
  <script type='text/javascript'>

	overdiv='0'
	var ie = (document.all)? true:false

// create the popups 
	function popLayer(a, id) {
		dhelp=$('dhelp')
		helpstr=eval('help.$help.'+a)
		if(!helpstr){helpstr='<font color=red>Missing help info</font>'}

		desc = '<div style=\'position: relative; width: 300px; padding: 1em\'>'+helpstr+'</div>'
		dhelp.innerHTML=desc;

		if (o=$(id)) {
			wh = ie ? window.document.body.clientHeight : window.innerHeight
			ww = ie ? window.document.body.clientWidth : window.innerWidth
			wwo = ie ? window.document.body.scrollLeft : window.pageXOffset

			oleft=getAbsLeft(o)
			otop=getAbsTop(o)
			if (ww+wwo-oleft<350)
				oleft -= 300
			dhelp.style.left = oleft+ 'px'
			dhelp.style.bottom= wh-otop+20 + 'px'
		}

		dhelp.style.visibility='visible'
	}

	function hideLayer(){
		dhelp=$('dhelp')
		if (overdiv == '0') {
			dhelp.innerHTML=''
			dhelp.style.visibility='hidden';
		}
	}



</script>\n";
	return $javafunc;
};

/*************************************/
function print3dJavaFunctions() {
	$javafunc = "<script type=\"text/javascript\" >\n
	function customTrimPercent(obj, option) {
		if (option == true) {
			obj.trimpercent.disabled = true;
		} else {
			obj.trimpercent.disabled = false;
		}
		return;
	}
	</script>";
	return $javafunc;
};


/*************************************/
function openRoundBorder() {
	$text = "<div id='roundbox'>\n";
	$text .= "<b class='xtop'><b class='xb1'></b><b class='xb2'></b><b class='xb3'></b><b class='xb4'></b></b>\n";
	$text .= "<div class='roundboxcontent'>\n";
	$text .= "<p>\n";
	return ($text);
};

/*************************************/
function closeRoundBorder() {
	$text = "</p>\n";
	$text .= "</div><!--/roundboxcontent-->\n";
	$text .= "<b class='xbottom'><b class='xb4'></b><b class='xb3'></b><b class='xb2'></b><b class='xb1'></b></b>\n";
	$text .= "</div><!--/roundbox-->\n";
	return ($text);
};

/*************************************/
function randomString($length) {
	$s = md5(time());
	$i = 32-$length;
	$randstring = substr($s,rand(0,$i),$length);
	return $randstring;
};

/*************************************/
function getJobId() {
	date_default_timezone_set('America/Los_Angeles');
	$today = getdate();
	/*
	Array
	(	[seconds] => 40
		[minutes] => 58
		[hours]   => 21
		[mday]    => 17
		[wday]    => 2
		[mon]     => 6
		[year]    => 2003
		[yday]    => 167
		[weekday] => Tuesday
		[month]   => June
		[0]       => 1055901520
	)
	*/
	$jobid = $today['year']."."
		.strtolower(substr($today['month'],0,3))
		.sprintf("%02u", $today['mday']);
	/*	."d"
		.sprintf("%02u", $today['hours'])."h"
		.sprintf("%02u", $today['minutes'])."m"
		.sprintf("%02u", $today['seconds'])."s";
	*/
	$jobid .= ".".randomString(3);
	return $jobid;
};

/*************************************/
function makeErrorMsg($msg) {
	$html = "";
	$html .= "<font color='#990000' size='+2'>$msg</font>\n";
	$html .= "<hr/>\n";
	$html .= "<br/><br/>\n";
	return $html;
};

/*************************************/
function firstColumn($print3d=false) {
	$html = "\n";

	// Input file
	$html .= "<b>Input structure:</b><br/>\n";
	$html .= "<table border='0' cellspacing='5'><tr><td>\n";

	$html .= docpop('upload','Upload PDB file to process:<br/>');
	$html .= "	<input type='hidden' name='MAX_FILE_SIZE' value='30000000' />\n";
	$html .= "	<input type='file' name='uploadpdb' size='25' maxlength='250'/><br/>\n";
	$html .= "</td></tr><tr><td>\n";

	$pdbid = ($_POST['pdbid']) ? $_POST['pdbid'] : '';
	$html .= docpop('pdbid','Enter PDB ID to process:<br/>');
	$html .= "	<input type='text' name='pdbid' size='4' value='$pdbid'/>&nbsp;\n";
	$html .= "</td></tr></table>\n";
	$html .= "<br/>\n";

	// Biological unit
	$biounit = ($_POST['biounit']=='off') ? '' : 'CHECKED';
	$html .= "<input type='checkbox' name='biounit' $biounit />\n";
	$html .= docpop('biounit','Use biological unit?');
	$html .= "<br/><br/>\n";

	// Hetero atoms
	$hetero = ($_POST['hetero']=='on') ? 'CHECKED' : '';
	$html .= "<input type='checkbox' name='hetero' $hetero />\n";
	$html .= docpop('hetero','Use hetero atoms?');
	$html .= "<br/><br/>\n";

	// Grid resolution
	$html .= docpop('gridres','Grid resolution:<br/>');
	$html .= "	<input type='radio' name='gridres' value='crude' ";
	if ($_POST['gridres'] == 'crude')
		$html .=  " checked ";
	$html .= "/>crude\n";
	$html .= "	<input type='radio' name='gridres' value='low' ";
	if (!$_POST['gridres'] || $_POST['gridres'] == 'low')
		$html .=  " checked ";
	$html .= "/>low\n";
	$html .= "	<input type='radio' name='gridres' value='medium' ";
	if ($_POST['gridres'] == 'medium')
		$html .=  " checked ";
	$html .= "/>medium\n";
	$html .= "	<input type='radio' name='gridres' value='high' ";
	if ($_POST['gridres'] == 'high')
		$html .=  " checked ";
	$html .= "/>high\n";
	$html .= "<br/><br/>\n";

	if ($print3d == false) {
		// PyMOL compatibility
		$pymol = ($_POST['pymol']=='on') ? 'CHECKED' : '';
		$html .= "<input type='checkbox' name='pymol' $pymol />\n";
		$html .= docpop('pymol','PyMOL compatible');
		$html .= "<br/>\n";

		// Water PDB
		$waterpdb = ($_POST['waterpdb']=='on') ? 'CHECKED' : '';
		$html .= "<input type='checkbox' name='waterpdb' $waterpdb />\n";
		$html .= docpop('waterpdb','Create Water PDB');
		$html .= "<br/>\n";


	}
	// Allow use
	$allowuse = ($_POST['allowuse']=='off') ? '' : 'CHECKED';
	$html .= "<input type='checkbox' name='allowuse' $allowuse />\n";
	$html .= docpop('allowuse','Share your results');
	$html .= "<br/>\n";

	// Return
	return $html;
};

/*************************************/
function print3dColumn($print3d=false) {
	// Flat Surface Method
	$html .= docpop('flatmethod','Flat Surface Method:<br/>');
	$html .= "	<input type='radio' name='flatMethod' value='trim' ";
	if (!$_POST['flatMethod'] || $_POST['flatMethod'] == 'trim')
		$html .=  " checked ";
	$html .= "/>trim\n";
	$html .= "	<input type='radio' name='flatMethod' value='bisect' ";
	if ($_POST['flatMethod'] == 'bisect')
		$html .=  " checked ";
	$html .= "/>bisect\n";
	$html .= "	<input type='radio' name='flatMethod' value='none' ";
	if ($_POST['flatMethod'] == 'none')
		$html .=  " checked ";
	$html .= "/>none\n";
	$html .= "<br/><br/>\n";

	// Flat Surface Axis
	$html .= docpop('flataxis','Flat Surface Axis:<br/>');
	$html .= "	<input type='radio' name='flataxis' value='auto' ";
	if (!$_POST['flataxis'] || $_POST['flataxis'] == 'auto')
		$html .=  " checked ";
	$html .= "/>auto\n";
	$html .= "	<input type='radio' name='flataxis' value='x' ";
	if ($_POST['flataxis'] == 'x')
		$html .=  " checked ";
	$html .= "/>x\n";
	$html .= "	<input type='radio' name='flataxis' value='y' ";
	if ($_POST['flataxis'] == 'y')
		$html .=  " checked ";
	$html .= "/>y\n";
	$html .= "	<input type='radio' name='flataxis' value='z' ";
	if ($_POST['flataxis'] == 'z')
		$html .=  " checked ";
	$html .= "/>z\n";
	$html .= "<br/><br/>\n";

	// Flat Surface Percent
	$html .= docpop('trimpercent','Trim Percent:<br/>');
	$html .= "	<input type='radio' name='trimpercentchoice' value='auto' onChange='customTrimPercent(this.form, true)'";
	if (!$_POST['trimpercentchoice'] || $_POST['trimpercentchoice'] == 'auto')
		$html .=  " checked ";
	$html .= "/>auto\n";
	$html .= "	<input type='radio' name='trimpercentchoice' value='custom' onChange='customTrimPercent(this.form, false)'";
	if ($_POST['trimpercentchoice'] == 'custom')
		$html .=  " checked ";
	$html .= "/>custom\n";
	$trimpercent = ($_POST['trimpercent']) ? $_POST['trimpercent'] : '';
	if (!$_POST['trimpercent'])
		$html .= "<br/>Percent: <input type='text' name='trimpercent' size='4' disabled> (0..100)";
	else
		$html .= "<br/>Percent: <input type='text' name='trimpercent' size='4' value='"
			.$_POST['trimpercent']."' disabled> (0..100)";
	$html .= "<br/><br/>\n";
	return $html;
};
	

/*************************************/
function launchJob($command, $progname, $print3d=false) {
	// get common variables
	global $PROCDIR;
	$hostip = $_SERVER['REMOTE_ADDR'];
	$jobid = getJobId();
	$pdbid=$_POST['pdbid'];
	$hetero=$_POST['hetero'];
	$biounit=$_POST['biounit'];
	$gridres = $_POST['gridres'];
	$allowuse = $_POST['allowuse'];
	$flatmethod = $_POST['flatMethod'];
	$flataxis = $_POST['flataxis'];
	$trimpercent = $_POST['trimpercent'];
	$pymol = $_POST['pymol'];
	$waterpdb = $_POST['waterpdb'];

	$datestamp = substr($jobid, 0, 7);
	$jobdir = preg_replace("/\./", "/", $jobid);
	exec("mkdir -p ".$PROCDIR."output/$jobdir");
	//mkdir($PROCDIR."output/$jobdir");

	// make sure pdb id was selected
	if (!$pdbid && !$_FILES['uploadpdb']['name']) {
		return ('No pdbid selected');
		exit;
	} elseif ($_FILES['uploadpdb']['name']) {
		$uploaddir = $PROCDIR."output/uploads/";
		$uploadfile = $uploaddir . $jobid . ".pdb";
		#echo $_FILES['uploadpdb']['tmp_name']."<br/>";
		if (!move_uploaded_file($_FILES['uploadpdb']['tmp_name'], $uploadfile)) {
			print_r($_FILES['uploadpdb']);
			return ('file did not upload properly (hard drive full?) '.$_FILES['uploadpdb']['tmp_name']);
			exit;
		}
	}

	// finish write command line
	if ($_FILES['uploadpdb']['name'])
		$command.=" --pdbfile=$uploadfile";
	elseif ($pdbid)
		$command.=" --pdbid=$pdbid";
	if ($biounit=='on')
		$command.=" --biounit";
	if ($hetero=='on')
		$command.=" --hetero";

	if ($allowuse=='on')
		$command.=" --allowuse";
	$command.=" --gridres=$gridres";
	
	if (!$print3d) {	
		if ($pymol=='on')
			$command.=" --pymol";
		if ($waterpdb=='on')
			$command.=" --waterpdb";
	}	
	if ($print3d) {
		$command.=" --flatmethod=$flatmethod";
		if ($flataxis)
			$command.=" --flataxis=$flataxis";
		if ($trimpercent) {
			$trimpercent = floatval($trimpercent)/100.0;
			$command.= " --trimpercent=$trimpercent";
		}
	}
	
	$command.=" --hostip=$hostip";
	$command.=" --jobid=$jobid";
	$command.=" > ".$PROCDIR."output/$jobdir/shell-$jobid.log 2>&1 &";

	$header = "";
	$header .= "<meta http-equiv='refresh' content='1;url=viewResults.php?jobid=".$jobid."'>";
	writeTop($progname,$progname,$header);

	echo "<table width='80%' border='1'>\n";

	echo "<tr><td colspan='2' align='center'>\n";
	echo "  <h3>";
	echo "  You can view the progress of your command and see the results at:";
	echo "  <br/><br/>\n";
	echo "  <a href='viewResults.php?jobid=".$jobid."'>";
	echo "  viewResults.php?jobid=".$jobid."</a><br/>";
	echo "  </h3>";
	echo "</td></tr>\n";

	echo "<tr><td colspan='2'>\n";
	echo "  <h3>This page is for debugging purpose only</h3><br/>\n";
	echo "  <b>$progname Command:</b>\n";
	echo "  <br/><br/>\n";
	echo "  <font size='-1'>$command</font>\n";
	echo "  <br/><br/>\n";
	echo "<ul>\n";
	if (file_exists($PROCDIR."output/$jobdir/shell-$jobid.log"))
		echo "  <li>Shell log: <font size='-1'><a href='output/$jobdir/shell-$jobid.log'>"
			.$PROCDIR."output/$jobdir/shell-$jobid.log</a></font>\n";
	if (file_exists($PROCDIR."output/$jobdir/runlog-$jobid.html"))
		echo "  <li>Running log: <font size='-1'><a href='output/$jobdir/runlog-$jobid.html'>"
			.$PROCDIR."output/$jobdir/runlog-$jobid.html</a></font>\n";
	echo "  <li>Results html: <font size='-1'><a href='output/$jobdir/results-$jobid.html'>"
		.$PROCDIR."output/$jobdir/results-$jobid.html</a></font>\n";
	echo "</ul>\n";
	echo "</td></tr>\n";

	echo "</table>\n";

	// for this to work apache should have the same group as you
	// .chimera and sinedon.cfg need to go into /var/www/

	// see http://www.php.net/manual/en/ref.exec.php
	exec($command);
	//system($command);
	//shell_exec($command);
	//popen($command);
	//passthru($command);

	writeBottom();
};

?>
