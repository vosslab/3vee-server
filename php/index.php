
<?php
require "inc/processing.inc";

function generateTab($name, $link, $descript) {
	echo "<td width='180' align='center'>\n";
	echo "  <a href='$link.php'><img border='0' src='img/$link.png' height='100'></a>\n";
	echo "</td><td>\n";
	echo "  <h3><a href='$link.php'>$name</a></h3>\n";
	echo "    <p>\n";
	echo "      $descript";
	echo "    </p>\n";
	echo "</td>\n";
};

$title = "3v website";
$heading = $title;
$javascript = "";
writeTop($title,$heading,$javascript);

// Selection Header
echo "<table border='0' width='640'>\n";
echo "<tr><td>\n";
echo "  <h2>Volume Calculation and Extraction Procedures</h2>\n";
//echo "  <img src='img/align-smr.png' width='250'><br/>\n";
echo "  <h4>\n";
echo "    3vee is collection of program for the assessment of volumes in protein files.\n";
echo "  </h4>\n";
echo "</td></tr>\n";
echo "</table>\n";


//echo "<br/>\n";
echo "<table border='0' cellpading='10' cellspacing='10'><tr><td>";
echo "<table border='1' class='tableborder' width='640'>\n";

/*
** Functions
*/
echo "<tr>\n";
echo "<td colspan='2' align='center'><br/><h2>External Volumes</h2></td>\n";
echo "</tr><tr>\n";
generateTab("Volume Calculation", "volumeCalc", "Calculate the volume of a structure for a given probe size");
echo "</tr><tr>\n";
generateTab("Volume Range", "volumeRange", "Calculate the volume of a structure for a range probe sizes");
echo "</tr><tr>\n";
//generateTab("Fraction solvent volume Calculation", "fsvCalc", "Calculate the volume of a structure");

echo "<td colspan='2' align='center'><br/><h2>Internal Volumes</h2></td>\n";
echo "</tr><tr>\n";
generateTab("Channel Finder", "channelFinder", "Find and extract all major channels from the structure based on their size");
echo "</tr><tr>\n";
generateTab("Single Channel Extraction", "channelExtract", "Extract a particular channel with a known x,y,z coordinate");
echo "</tr><tr>\n";
generateTab("Solvent Extraction", "solventExtract", "Extract all the solvent volume from a structure");
//echo "</tr><tr>\n";
//generateTab("Cavity Extraction", "cavityExtract", "Calculate the volume of a structure");
echo "</tr><tr>\n";
generateTab("Exit Tunnel Extraction", "tunnelExtract", "Calculate the volume of the polypeptide exit tunnel from the 50S ribosomal subunit");
echo "</tr>\n";
echo "</table>\n";

echo "</td><td>\n";
showRecentRuns(false, 6);
echo "</td></tr>\n";
echo "</table>\n";

writeBottom($showproclink=False);
exit;

?>



