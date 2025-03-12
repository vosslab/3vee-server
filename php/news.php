
<?php
require "inc/processing.inc";

$title = "3v news";
$heading = $title;
$javascript = "";
writeTop($title,$heading,$javascript);

echo"<table border='0'><tr><td>\n"; echo"<pre> 

July 20, 2012 -- Added ability to download PDB file with water molecules in voxel locations 
(does not work on channel finder)

May 14, 2012 -- Provide links to download MRC files before imaging is finished

May 10, 2012 -- Several bug fixes to source code, download SVN if having problems

Dec 4, 2011 -- Hard drive filled up, cleared space

May 12, 2011 -- Fixed origin issues in MRC files for both standard and PyMOL versions (needs work)

May 5, 2011 -- Added NEWS site to report any upgrades and/or site news

April 3, 2011 -- Check links to see if they are valid before providing a link

February, 22, 2011 -- 3v paper has been published, links now appear at bottom of page

November 22, 2010 -- Added initial PyMOL support for MRC files,
                     PyMOL does not support MRC files with integers only floats

September 10, 2010 -- Increased maximum file size for PDB uploads,
                      you can now upload ribosomes.

September 10, 2010 -- added warning for non-Haloarcula ribosome exit tunnels, 
                      hope to fix in future, but this is not easy

June 18, 2010 -- More PDB upload fixes

April 8, 2010 -- Added Jmol viewer, it is very fickle

April 6, 2010 -- Allow users to find top N channels in structure by size

April 6, 2010 -- Add reduced center, may help to locate coordinates of channels

April 5, 2010 -- Added javascript popups to result page

April 5, 2010 -- Published guide to viewing volume in Chimera

April 2, 2010 -- Updated to new version of Chimera (headless) for making images

April 1, 2010 -- If biological unit does not exist download normal PDB

March 31, 2010 -- Added TAR files to download all channels in 1 click

January 25, 2010 -- Fix file uploads

January 25, 2010 -- Major bug fix, fixes infinite loop on some jobs

January 15, 2010 -- Rename AllChannel and extractChannels to channel finder

January 8, 2010 -- Added recent runs to main page

December 28, 2009 -- Added presets for each tool

November 30, 2009 -- Added email link at bottom

September 16, 2009 -- Added biological coordinates

August 26, 2009 -- Show recent runs

August 18, 2009 -- Show command line to users

August 18, 2009 -- Added new function, Volume Probe Range

August 13, 2009 -- Initial revamp of the new website format and development platform

</pre>";

echo "</td></tr></table>";

writeBottom($showproclink=False);
exit;

?>



