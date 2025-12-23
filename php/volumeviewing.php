<?php

require "inc/processing.inc";

$title = "3v Volume Viewing Guide";
writeTop($title, $title, '');

echo "<div class='threev-content'>\n";

echo "  <div class='threev-section'>\n";
echo "    <h2>Volume viewing guide</h2>\n";
echo "    <p>3v produces MRC volumes and optional PDBs. These can be opened in ChimeraX, Chimera, or PyMOL. The results pages also include a Jmol link when an OBJ surface is available.</p>\n";
echo "  </div>\n";

echo "  <div class='threev-section'>\n";
echo "    <h2>Quick start (ChimeraX)</h2>\n";
echo "    <ol>\n";
echo "      <li>Download the MRC file from your results page and unzip it.</li>\n";
echo "      <li>(Optional) Download the PDB file for structure context.</li>\n";
echo "      <li>Open both in ChimeraX using <em>File &rarr; Open</em>.</li>\n";
echo "      <li>Open the Volume Viewer and adjust the threshold until the surface appears.</li>\n";
echo "      <li>Use surface smoothing and lighting to improve readability.</li>\n";
echo "    </ol>\n";
echo "    <div class='threev-note'>\n";
echo "      3v volumes are often binary (0/1). Thresholds around 0.01 are a good starting point.\n";
echo "    </div>\n";
echo "  </div>\n";

echo "  <div class='threev-section'>\n";
echo "    <h2>Tips for clean renders</h2>\n";
echo "    <ul>\n";
echo "      <li>Use a slightly higher threshold to suppress noise on the surface.</li>\n";
echo "      <li>Enable surface smoothing to reduce faceting in low-resolution maps.</li>\n";
echo "      <li>Color the volume to distinguish shell, channel, and cavity regions.</li>\n";
echo "    </ul>\n";
echo "  </div>\n";

echo "  <div class='threev-section'>\n";
echo "    <h2>In-browser viewing</h2>\n";
echo "    <p>When available, the results page includes a “View Volume in Jmol” link. This opens a Java-based viewer with the OBJ surface. It is useful for quick inspection but less capable than ChimeraX or PyMOL.</p>\n";
echo "  </div>\n";

echo "  <div class='threev-section'>\n";
echo "    <h2>Reference screenshots</h2>\n";
echo "    <div class='threev-grid'>\n";
echo "      <figure>\n";
echo "        <img src='img/volumeviewer1.png' width='428' height='276' alt='Chimera volume viewer'>\n";
echo "        <figcaption>Volume Viewer controls</figcaption>\n";
echo "      </figure>\n";
echo "      <figure>\n";
echo "        <img src='img/volumeviewer2.png' width='428' height='562' alt='Surface and mesh options'>\n";
echo "        <figcaption>Surface and mesh options</figcaption>\n";
echo "      </figure>\n";
echo "      <figure>\n";
echo "        <img src='img/pgp-struct.png' width='612' height='442' alt='Rendered example'>\n";
echo "        <figcaption>Example render</figcaption>\n";
echo "      </figure>\n";
echo "    </div>\n";
echo "  </div>\n";

echo "</div>\n";

writeBottom();
exit;

?>
