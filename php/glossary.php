<?php

require "inc/processing.inc";

$title = "3v Glossary";
writeTop($title,$title,'');
global $PROCDIR;


echo "<table border='0' cellpading='3'><tr><td align='left'>\n";

/*********************************/
/*********************************/
echo "<br/>";
echo "<h1>External Volumes</h1>";
echo "<hr/>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
/********** FIGURE ***************/
echo "<table border='0' width='600' cellspacing='5'>\n";
echo "<tr><td align='center' colspan='8'>\n";
echo "<h4>Series of lysozyme excluded volumes at difference probe sizes</h4>\n";
echo "<font size='-2'>Click on images for a larger version</font>\n";

echo "</td></tr><tr><td align='center'>\n";

echo "<a href='img/lysozyme-00.0.mrc.2.png'>\n";
echo "  <img border='0' width='128' height='128' src='img/lysozyme-00.0.mrc.2.png'>\n";
echo "</a><font size='-2'>Probe 0.0 &Aring; (VDW)</font>\n";
echo "</td><td align='center'>\n";
echo "<a href='img/lysozyme-01.0.mrc.2.png'>\n";
echo "  <img border='0' width='128' height='128' src='img/lysozyme-01.0.mrc.2.png'>\n";
echo "</a><font size='-2'>Probe 1.0 &Aring;</font>\n";
echo "</td><td align='center'>\n";
echo "<a href='img/lysozyme-02.0.mrc.2.png'>\n";
echo "  <img border='0' width='128' height='128' src='img/lysozyme-02.0.mrc.2.png'>\n";
echo "</a><font size='-2'>Probe 2.0 &Aring;</font>\n";
echo "</td><td align='center'>\n";
echo "<a href='img/lysozyme-04.0.mrc.2.png'>\n";
echo "  <img border='0' width='128' height='128' src='img/lysozyme-04.0.mrc.2.png'>\n";
echo "</a><font size='-2'>Probe 4.0 &Aring;</font>\n";
echo "</td><td align='center'>\n";
echo "<a href='img/lysozyme-08.0.mrc.2.png'>\n";
echo "  <img border='0' width='128' height='128' src='img/lysozyme-08.0.mrc.2.png'>\n";
echo "</a><font size='-2'>Probe 8.0 &Aring;</font>\n";
echo "</td><td align='center'>\n";

echo "</td></tr></table>\n";
echo "<hr/>";

echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Van der Waals (VDW) volume</h3>";
echo "<h5>
The van der Waals (VDW) surface is the surface defined as the surface 
created when each atom is represented by a sphere with a radius equal
to the van der Waals (VDW) radius of that atom. The van der Waals (VDW) 
surface for a molecule is the union of all the individual van der Waals
spheres.

The van der Waals volume of a molecule is the total volume occupied by its atoms. It is computed assuming each atom is a sphere having its non-bonded van der Waals radius, and counting volumes where van der Waals spheres overlap only once.

<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Solvent-accessible volume</h3>";
echo "<h5>
The solvent accessible surface is the surface defined as the VDW surface 
plus a probe radius.

The solvent-accessible volume of a macromolecule corresponds to the volume inside the accessible surface defined for it by the rolling probe method using a 1.5 &Aring; radius probe (Richards, 1977). However it is not computed that way. Instead, every atom in the structure is treated as a sphere the radius of which is the sum of its non-bonded van der Waals radius plus 1.5 &Aring;, the radius of a water molecule. The solvent-accessible volume is the sum of the volume of all such spheres with regions where spheres overlap counted only once (Lee & Richards, 1971). 

<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Solvent-excluded volume</h3>";
echo "<h5>
The solvent-excluded volume of a macromolecule is the volume inside the excluded surface of that macromolecule determined using a spherical probe of 1.5 &Aring;.

<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Shell volume</h3>";
echo "<h5>
The 'shell' of a macromolecule is the limiting surface used to distinguish the interior of the macromolecule from its exterior. The shell volume is the volume inside that surface.
<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Convex hull volume</h3>";
echo "<h5>
The convex hull of any object is the smallest convex surface that entirely surrounds the set of van der Waals (VDW) spheres for macromolecules. The convex hull volume of an object is the volume inside its convex hull. The convex hull volume is equivalent to the infinite-excluded volume, <i>i.e.</i>, the excluded surface of that macromolecule determined using a spherical probe of infinite radius or two-dimensional plane.
<h5>";
echo "</td></tr><tr><td align='left'>\n";


/*********************************/
/*********************************/
echo "<hr/>";
echo "<h1>Internal Volumes</h1>";
echo "<hr/>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
/********** FIGURE ***************/
echo "<table border='0' width='600' cellspacing='5'>\n";
echo "<tr><td align='center'>\n";
echo "<h4>Slice through Lysozyme</h4>\n";
echo "<font size='-2'>Click on image for a larger version</font>\n";
echo "</td><td align='center'>\n";
echo "<h4>Slice through 50S Ribosomal subunit</h4>\n";
echo "<font size='-2'>Click on image for a larger version</font>\n";

echo "</td></tr><tr><td align='center'>\n";

echo "<a href='img/lysozyme_layers.png'>\n";
echo "  <img border='0' width='245' height='260' src='img/lysozyme_layers.png'>\n";
echo "</a>\n";
echo "</td><td align='center'>\n";
echo "<a href='img/ribosome_layers.png'>\n";
echo "  <img border='0' width='240' height='306' src='img/ribosome_layers.png'>\n";
echo "</a>\n";

echo "</td></tr><tr><td colspan='3'>\n";
echo "<h4>
<b>LEGEND:</b> Inside the van der Waals surface (dark blue) 
and the solvent excluded surface (light blue), there are two
type of solvent: cavities (light green) and channels (light red).
The outer most surface (dark red line) is defined by the shell volume.
The difference between channels and cavities is that channels are connected
to the outside surface and cavities are self-contained units.
</h4>
\n";

echo "</td></tr></table>\n";
echo "<hr/>";

echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Empty volume</h3>";
echo "<h5>
The empty volume of a macromolecule is the difference between its solvent-excluded volume and its van der Waals volume. It corresponds to the sum of the small volumes in between the atoms that are not accessible to a solvent molecule. The empty volume corresponds to the light blue area in the Figures (above).
<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Solvent volume</h3>";
echo "<h5>
The solvent volume of a macromolecule is the difference between its shell volume and its solvent-excluded volume. This corresponds to all points inside the shell volume large enough to accommodate a solvent molecule that do not overlap with the solvent-excluded volume. The solvent volume corresponds to both the light red and green areas in the Figures (above).
<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Cavity volume</h3>";
echo "<h5>
The cavity volume of a macromolecule is the sum of the volumes inside its shell that are large enough to accommodate a spherical probe, but are not connected to the macromolecule's shell by at least one passage traversable by the probe. The cavity volume corresponds to the light green areas in the Figures (above).
<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "<h3>Channel volume</h3>";
echo "<h5>
The channel volume is equal to the solvent volume minus the cavity volume. The channel volume corresponds to the light red areas in the Figures (above).
<h5>";
echo "</td></tr><tr><td align='left'>\n";

/*********************************/
echo "</td></tr></table>\n";

writeBottom();
exit;

?>


