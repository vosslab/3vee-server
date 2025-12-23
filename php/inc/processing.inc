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

if (session_status() === PHP_SESSION_NONE) {
	session_start();
}
if (!isset($_SESSION['csrf_token'])) {
	$_SESSION['csrf_token'] = bin2hex(random_bytes(32));
}
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
	$posted_token = isset($_POST['csrf_token']) ? $_POST['csrf_token'] : '';
	if (!$posted_token || !hash_equals($_SESSION['csrf_token'], $posted_token)) {
		http_response_code(400);
		echo "Invalid request token.";
		exit;
	}
}

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
function post_value($key, $default = '') {
	return array_key_exists($key, $_POST) ? $_POST[$key] : $default;
}

/*************************************/
function csrf_field() {
	$token = isset($_SESSION['csrf_token']) ? $_SESSION['csrf_token'] : '';
	$escaped = htmlspecialchars($token, ENT_QUOTES, 'UTF-8');
	return "<input type='hidden' name='csrf_token' value='".$escaped."'>\n";
}

/*************************************/
function sanitize_choice($value, $allowed, $default) {
	return in_array($value, $allowed, true) ? $value : $default;
}

/*************************************/
function sanitize_float($value, $default) {
	if ($value === '' || $value === null) {
		return $default;
	}
	if (filter_var($value, FILTER_VALIDATE_FLOAT) === false) {
		return $default;
	}
	$float_value = floatval($value);
	if (!is_finite($float_value)) {
		return $default;
	}
	return $float_value;
}

/*************************************/
function sanitize_int($value, $default) {
	if ($value === '' || $value === null) {
		return $default;
	}
	if (filter_var($value, FILTER_VALIDATE_INT) === false) {
		return $default;
	}
	return intval($value);
}

/*************************************/
function sanitize_pdbid($value) {
	$value = strtoupper(trim($value));
	if (preg_match('/^[A-Z0-9]{4}$/', $value)) {
		return $value;
	}
	return '';
}

/*************************************/
function sanitize_flag($value) {
	return ($value === 'on' || $value === 'true' || $value === '1') ? 'on' : '';
}

/*************************************/
function sanitize_jobid($value) {
	$value = strtolower(trim($value));
	if (strlen($value) === 14
		&& preg_match('/^[0-9]{4}\\.[a-z]{3}[0-9]{2}\\.[a-f0-9]{3}$/', $value)) {
		return $value;
	}
	return '';
}

/*************************************/
function validate_pdb_upload($file, $max_bytes = 30000000) {
	if (!is_array($file)) {
		return "Upload is missing.";
	}
	if (!isset($file['error']) || $file['error'] !== UPLOAD_ERR_OK) {
		return "Upload failed.";
	}
	if (!isset($file['tmp_name']) || !is_uploaded_file($file['tmp_name'])) {
		return "Upload did not complete.";
	}
	if (!isset($file['size']) || $file['size'] <= 0) {
		return "Upload is empty.";
	}
	if ($file['size'] > $max_bytes) {
		return "Upload is too large.";
	}
	$name = isset($file['name']) ? $file['name'] : '';
	if (!preg_match('/\\.pdb$/i', $name)) {
		return "Only .pdb files are accepted.";
	}
	if (function_exists('finfo_open')) {
		$finfo = finfo_open(FILEINFO_MIME_TYPE);
		if ($finfo) {
			$mime = finfo_file($finfo, $file['tmp_name']);
			finfo_close($finfo);
			$allowed = array('text/plain', 'application/octet-stream', 'chemical/x-pdb');
			if ($mime && !in_array($mime, $allowed, true)) {
				return "Unsupported file type.";
			}
		}
	}
	return '';
}

/*************************************/
function post_choice($key, $allowed, $default) {
	return sanitize_choice(post_value($key, $default), $allowed, $default);
}

/*************************************/
function post_float_value($key, $default) {
	return sanitize_float(post_value($key, $default), $default);
}

/*************************************/
function post_float_optional($key) {
	$raw = post_value($key, '');
	if ($raw === '' || $raw === null) {
		return null;
	}
	if (filter_var($raw, FILTER_VALIDATE_FLOAT) === false) {
		return null;
	}
	$float_value = floatval($raw);
	if (!is_finite($float_value)) {
		return null;
	}
	return $float_value;
}

/*************************************/
function post_int_value($key, $default) {
	return sanitize_int(post_value($key, $default), $default);
}

/*************************************/
function post_flag_value($key, $default = '') {
	return sanitize_flag(post_value($key, $default));
}

/*************************************/
function post_pdbid() {
	return sanitize_pdbid(post_value('pdbid'));
}

/*************************************/
function post_jobid() {
	return sanitize_jobid(post_value('jobid'));
}

/*************************************/
function get_jobid() {
	return sanitize_jobid(isset($_GET['jobid']) ? $_GET['jobid'] : '');
}

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
			$pngdir = $rundata['path'];
			if ($pngdir && substr($pngdir, 0, 1) != '/') {
				$pngdir = $GLOBALS['PROCDIR'].$pngdir;
			}
			$pngfiles = glob($pngdir."/*.png");
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
				$pngurl = preg_replace('#^.*?/output/#', '/output/', $pngfile);
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
	echo "<link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'>\n";
	echo "<script type='text/javascript' src='js/lvmenu.js'></script>\n";
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
	echo "<div class='threev-header'>\n";
	echo "  <div class='threev-header-inner'>\n";
	echo "    <div class='threev-brand'>\n";
	echo "      <a class='threev-logo' href='index.php'>3V</a>\n";
	echo "      <div class='threev-brand-text'>\n";
	echo "        <div class='threev-title'>Voss Volume Voxelator</div>\n";
	echo "        <div class='threev-subtitle'>Cavity, channel, and cleft analysis</div>\n";
	echo "      </div>\n";
	echo "    </div>\n";
	if ($heading) {
		echo "    <div class='threev-page-title'>$heading</div>\n";
	}
	echo "  </div>\n";
	echo "</div>\n";
	$nav_items = array(
		array('href' => 'index.php', 'label' => 'Home'),
		array('href' => 'volumeCalc.php', 'label' => 'Volume'),
		array('href' => 'channelFinder.php', 'label' => 'Channel Finder'),
		array('href' => 'simple3dPrint.php', 'label' => '3D Print'),
		array('href' => 'sourcecode.php', 'label' => 'Source'),
		array('href' => 'glossary.php', 'label' => 'Help'),
	);
	$current_page = basename($_SERVER['PHP_SELF']);
	echo "<div class='threev-nav'>\n";
	echo "  <div class='threev-nav-inner'>\n";
	echo "    <ul class='threev-menu'>\n";
	foreach ($nav_items as $item) {
		$active = ($current_page === $item['href']) ? " class='active'" : '';
		echo "      <li$active><a href='".$item['href']."'>".$item['label']."</a></li>\n";
	}
	echo "    </ul>\n";
	echo "  </div>\n";
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
	echo "<div class='threev-footer'>\n";
	echo "  <div class='threev-footer-inner'>\n";
	echo "    <div class='threev-footer-block'>\n";
	echo "      <div class='threev-footer-title'>Resources</div>\n";
	echo "      <a href='index.php'>Home</a>\n";
	echo "      <a href='sourcecode.php'>Source code</a>\n";
	echo "      <a href='glossary.php'>Help</a>\n";
	echo "      <a href='news.php'>News</a>\n";
	echo "      <a href='volumeviewing.php'>Volume viewing</a>\n";
	echo "    </div>\n";
	echo "    <div class='threev-footer-block'>\n";
	echo "      <div class='threev-footer-title'>Social</div>\n";
	echo "      <a href='https://www.youtube.com/neilvosslab'>\n";
	echo "        <i class='fa-brands fa-youtube'></i> YouTube\n";
	echo "      </a>\n";
	echo "      <a href='https://github.com/vosslab'>\n";
	echo "        <i class='fa-brands fa-github'></i> GitHub\n";
	echo "      </a>\n";
	echo "      <a href='https://bsky.app/profile/neilvosslab.bsky.social'>\n";
	echo "        <i class='fa-brands fa-bluesky'></i> Bluesky\n";
	echo "      </a>\n";
	echo "      <a href='https://fb.me/neilvosslab'>\n";
	echo "        <i class='fa-brands fa-facebook'></i> Facebook\n";
	echo "      </a>\n";
	echo "      <a href='https://www.linkedin.com/in/vosslab'>\n";
	echo "        <i class='fa-brands fa-linkedin'></i> LinkedIn\n";
	echo "      </a>\n";
	echo "    </div>\n";
	echo "    <div class='threev-footer-block span-two'>\n";
	echo "      <div class='threev-footer-title'>Citation</div>\n";
	echo "      <div class='threev-footer-citation'>\n";
	echo "        <a href='http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2896178/'>\n";
	echo "          3V: cavity, channel and cleft volume calculator\n";
	echo "        </a>\n";
	echo "        <div>Nucleic Acids Res. 2010; 38(Web Server issue): W555-W562</div>\n";
	echo "        <div>Neil R. Voss and Mark Gerstein</div>\n";
	echo "      </div>\n";
	echo "    </div>\n";
	echo "    <div class='threev-footer-block'>\n";
	echo "      <div class='threev-footer-title'>Support</div>\n";
	echo "      <a href='bitcoin:bc1qdexkqwzyet93ret40akqmms2jv99wvsgzdshu8?message=support%20qti_package_maker'>\n";
	echo "        <i class='fa-brands fa-bitcoin'></i> Bitcoin\n";
	echo "      </a>\n";
	echo "      <a href='dash:XdDmwBVecEy9yyXKeD7hScLp7oN8rd4XNV?message=support%20qti_package_maker'>\n";
	echo "        <span class='threev-icon'>D</span> Dash\n";
	echo "      </a>\n";
	echo "      <a href='https://www.patreon.com/vosslab'>\n";
	echo "        <i class='fa-brands fa-patreon'></i> Patreon\n";
	echo "      </a>\n";
	echo "      <a href='https://paypal.me/vosslab'>\n";
	echo "        <i class='fa-brands fa-paypal'></i> PayPal\n";
	echo "      </a>\n";
	echo "    </div>\n";
	echo "  </div>\n";
	echo "</div>\n";
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
	$html .= "<span style='color:#990000; font-size:larger;'>$msg</span>\n";
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

	$pdbid = post_value('pdbid');
	$html .= docpop('pdbid','Enter PDB ID to process:<br/>');
	$html .= "	<input type='text' name='pdbid' size='4' value='$pdbid'/>&nbsp;\n";
	$html .= "</td></tr></table>\n";
	$html .= "<br/>\n";

	// Biological unit
	$biounit = (post_value('biounit')=='off') ? '' : 'CHECKED';
	$html .= "<input type='checkbox' name='biounit' $biounit />\n";
	$html .= docpop('biounit','Use biological unit?');
	$html .= "<br/><br/>\n";

	// Hetero atoms
	$hetero = (post_value('hetero')=='on') ? 'CHECKED' : '';
	$html .= "<input type='checkbox' name='hetero' $hetero />\n";
	$html .= docpop('hetero','Use hetero atoms?');
	$html .= "<br/><br/>\n";

	// Grid resolution
	$gridres = post_value('gridres', 'low');
	$html .= docpop('gridres','Grid resolution:<br/>');
	$html .= "	<input type='radio' name='gridres' value='crude' ";
	if ($gridres == 'crude')
		$html .=  " checked ";
	$html .= "/>crude\n";
	$html .= "	<input type='radio' name='gridres' value='low' ";
	if ($gridres == 'low')
		$html .=  " checked ";
	$html .= "/>low\n";
	$html .= "	<input type='radio' name='gridres' value='medium' ";
	if ($gridres == 'medium')
		$html .=  " checked ";
	$html .= "/>medium\n";
	$html .= "	<input type='radio' name='gridres' value='high' ";
	if ($gridres == 'high')
		$html .=  " checked ";
	$html .= "/>high\n";
	$html .= "<br/><br/>\n";

	if ($print3d == false) {
		// PyMOL compatibility
		$pymol = (post_value('pymol')=='on') ? 'CHECKED' : '';
		$html .= "<input type='checkbox' name='pymol' $pymol />\n";
		$html .= docpop('pymol','PyMOL compatible');
		$html .= "<br/>\n";

		// Water PDB
		$waterpdb = (post_value('waterpdb')=='on') ? 'CHECKED' : '';
		$html .= "<input type='checkbox' name='waterpdb' $waterpdb />\n";
		$html .= docpop('waterpdb','Create Water PDB');
		$html .= "<br/>\n";


	}
	// Allow use
	$allowuse = (post_value('allowuse')=='off') ? '' : 'CHECKED';
	$html .= "<input type='checkbox' name='allowuse' $allowuse />\n";
	$html .= docpop('allowuse','Share your results');
	$html .= "<br/>\n";

	// Return
	return $html;
};

/*************************************/
function print3dColumn($print3d=false) {
	$html = "";
	$flatMethod = post_value('flatMethod', 'trim');
	// Flat Surface Method
	$html .= docpop('flatmethod','Flat Surface Method:<br/>');
	$html .= "	<input type='radio' name='flatMethod' value='trim' ";
	if ($flatMethod == 'trim')
		$html .=  " checked ";
	$html .= "/>trim\n";
	$html .= "	<input type='radio' name='flatMethod' value='bisect' ";
	if ($flatMethod == 'bisect')
		$html .=  " checked ";
	$html .= "/>bisect\n";
	$html .= "	<input type='radio' name='flatMethod' value='none' ";
	if ($flatMethod == 'none')
		$html .=  " checked ";
	$html .= "/>none\n";
	$html .= "<br/><br/>\n";

	// Flat Surface Axis
	$flatAxis = post_value('flataxis', 'auto');
	$html .= docpop('flataxis','Flat Surface Axis:<br/>');
	$html .= "	<input type='radio' name='flataxis' value='auto' ";
	if ($flatAxis == 'auto')
		$html .=  " checked ";
	$html .= "/>auto\n";
	$html .= "	<input type='radio' name='flataxis' value='x' ";
	if ($flatAxis == 'x')
		$html .=  " checked ";
	$html .= "/>x\n";
	$html .= "	<input type='radio' name='flataxis' value='y' ";
	if ($flatAxis == 'y')
		$html .=  " checked ";
	$html .= "/>y\n";
	$html .= "	<input type='radio' name='flataxis' value='z' ";
	if ($flatAxis == 'z')
		$html .=  " checked ";
	$html .= "/>z\n";
	$html .= "<br/><br/>\n";

	// Flat Surface Percent
	$trimChoice = post_value('trimpercentchoice', 'auto');
	$html .= docpop('trimpercent','Trim Percent:<br/>');
	$html .= "	<input type='radio' name='trimpercentchoice' value='auto' onChange='customTrimPercent(this.form, true)'";
	if ($trimChoice == 'auto')
		$html .=  " checked ";
	$html .= "/>auto\n";
	$html .= "	<input type='radio' name='trimpercentchoice' value='custom' onChange='customTrimPercent(this.form, false)'";
	if ($trimChoice == 'custom')
		$html .=  " checked ";
	$html .= "/>custom\n";
	$trimpercent = post_value('trimpercent', '');
	if ($trimpercent === '')
		$html .= "<br/>Percent: <input type='text' name='trimpercent' size='4' disabled> (0..100)";
	else
		$html .= "<br/>Percent: <input type='text' name='trimpercent' size='4' value='"
			.$trimpercent."' disabled> (0..100)";
	$html .= "<br/><br/>\n";
	return $html;
};
	

/*************************************/
function launchJob($command, $progname, $print3d=false) {
	// get common variables
	global $PROCDIR;
	$hostip = $_SERVER['REMOTE_ADDR'];
	if (!filter_var($hostip, FILTER_VALIDATE_IP)) {
		$hostip = '';
	}
	$jobid = getJobId();
	$pdbid = post_pdbid();
	$hetero = post_flag_value('hetero');
	$biounit = post_flag_value('biounit');
	$gridres = post_choice('gridres', array('crude', 'low', 'medium', 'high'), 'low');
	$allowuse = post_flag_value('allowuse', 'on');
	$flatmethod = post_choice('flatMethod', array('trim', 'bisect', 'none'), 'trim');
	$flataxis = post_choice('flataxis', array('auto', 'x', 'y', 'z'), 'auto');
	$trimpercent_raw = post_float_optional('trimpercent');
	$pymol = post_flag_value('pymol');
	$waterpdb = post_flag_value('waterpdb');
	$uploadName = isset($_FILES['uploadpdb']['name']) ? $_FILES['uploadpdb']['name'] : '';

	$datestamp = substr($jobid, 0, 7);
	$jobdir = preg_replace("/\./", "/", $jobid);
	exec("mkdir -p ".$PROCDIR."output/$jobdir");
	//mkdir($PROCDIR."output/$jobdir");

	// make sure pdb id was selected
	if (!$pdbid && !$uploadName) {
		return ('No pdbid selected');
		exit;
	} elseif ($uploadName) {
		$uploaddir = $PROCDIR."output/uploads/";
		$uploadfile = $uploaddir . $jobid . ".pdb";
		$upload_error = validate_pdb_upload($_FILES['uploadpdb']);
		if ($upload_error) {
			return $upload_error;
		}
		#echo $_FILES['uploadpdb']['tmp_name']."<br/>";
		$tmpname = isset($_FILES['uploadpdb']['tmp_name']) ? $_FILES['uploadpdb']['tmp_name'] : '';
		if (!$tmpname || !move_uploaded_file($tmpname, $uploadfile)) {
			print_r($_FILES['uploadpdb']);
			return ('file did not upload properly (hard drive full?) '.$tmpname);
			exit;
		}
	}

	// finish write command line
	if ($uploadName)
		$command.=" --pdbfile=".escapeshellarg($uploadfile);
	elseif ($pdbid)
		$command.=" --pdbid=".escapeshellarg($pdbid);
	if ($biounit=='on')
		$command.=" --biounit";
	if ($hetero=='on')
		$command.=" --hetero";

	if ($allowuse=='on')
		$command.=" --allowuse";
	$command.=" --gridres=".escapeshellarg($gridres);
	
	if (!$print3d) {	
		if ($pymol=='on')
			$command.=" --pymol";
		if ($waterpdb=='on')
			$command.=" --waterpdb";
	}	
	if ($print3d) {
		$command.=" --flatmethod=".escapeshellarg($flatmethod);
		if ($flataxis)
			$command.=" --flataxis=".escapeshellarg($flataxis);
		if ($trimpercent_raw !== null) {
			$trimpercent = $trimpercent_raw / 100.0;
			$command.= " --trimpercent=".escapeshellarg($trimpercent);
		}
	}
	
	$command.=" --hostip=".escapeshellarg($hostip);
	$command.=" --jobid=".escapeshellarg($jobid);
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
