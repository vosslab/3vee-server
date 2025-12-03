<?php

require "inc/processing.inc";

/****************************************
****************************************/
function JmolJavaScript($objfile, $pdbfile=false) {
	//echo "OBJ file: $objfile<br/><br/>\n";
	//echo "PDB file: $pdbfile<br/><br/>\n";
	if (!file_exists($objfile)) {
		return false;
	}

	// header
	$java .= "<!-- START Jmol Scripting -->\n";
	$java .= "<script src='js/Jmol.js' type='text/javascript'></script>\n";
	$java .= "<script type='text/javascript'>\n";

	// initialize Jmol
	$java .= "  jmolInitialize('jmol', 'JmolAppletSigned.jar');\n"; //signed applet
	//$java .= "  jmolInitialize('jmol');\n"; //unsigned applet
	//$java .= "  jmolCheckBrowser('redirect', 'hi');\n";

	// default settings
	//$java .= "  jmolDebugAlert();\n"; // annoying pop-up messages that say nothing
	$java .= "  jmolSetLogLevel(5);\n"; // show all errors
	$java .= "  jmolSetAppletColor('#ffffff');\n"; //white background

	// create window
	$java .= "  jmolApplet([640, 480]);\n";

	// zoom out
	$java .= "  jmolScriptWait('zoom 5');\n";

	// load PDB file
	if ($pdbfile)
		$java .= "  jmolScriptWait('load $pdbfile');\n"; //load test pdb file

	// load OBJ file
	$java .= "  jmolScript('isosurface obj \"$objfile\"');\n"; //load test OBJ file

	$java .= "  jmolScript('color isoSurface [80,208,80]');\n"; //load test OBJ file

	$java .= "</script>\n";
	$java .= "<!-- END Jmol Scripting -->\n";
	return $java;
};

/****************************************
****************************************/

$progname = "JmolViewer";
global $progname;
$javascript = "<script src='js/Jmol.js' type='text/javascript'></script>\n";
writeTop($progname, $progname, $javascript, false, false);

//remove weird chars for security reasons
$objfile = preg_replace("[^a-zA-Z0-9/\.]", "", $_GET['objfile']);
$pdbfile = preg_replace("[^a-zA-Z0-9/\.]", "", $_GET['pdbfile']);

if (!$objfile || !file_exists($objfile) || substr($objfile, 0, 7) != "output/") {
	echo "<font size='+3'>Object File Not Found</font><br/>";
	writeBottom();
	exit;
}


echo "<table border='0' cellpading='10' cellspacing='10'><tr><td>\n";

echo JmolJavaScript($objfile, $pdbfile);

echo "</td></tr>\n";
echo "</table>\n";

echo "</center>\n";
writeBottom();
exit;

?>
