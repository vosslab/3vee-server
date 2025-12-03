/**
 * help key : value defined in javascript object notation
 */

var help = {
	'threev' : {
		'upload' : 'Click browse and select a PDB file on your computer to upload.',
		'pdbid'  : 'Enter a PDB id and the program will download the structure from the Protein Data Bank and then process it.',
		'hetero' : 'Include non-protein and non-RNA atoms in the volume calculations, <i>e.g.</i> water and salt atoms.',
		'biounit' : 'The biological molecule (also called a biological unit) is the macromolecule that has been shown to be or is believed to be functional. For example, the functional hemoglobin molecule has 4 chains. In each of the examples of hemoglobin mentioned above, the biological unit remains the same -- 4 chains comprising one molecule of hemoglobin.',
		'allowuse' : 'Allow us to use your results on a report page showing all interesting results, and in turn publishing these results as part of a survey of different proteins paper.',
		'gridres' : 'The volumes are calculated on a three dimension grid, the grid resolution specifies the step size of the grid (or voxels). Crude = 2.0 &Aring;ngstrom voxels, Low = 1.0 &Aring;, Medium = 0.75 &Aring; and High = 0.5 &Aring;.',

		'probe'  : 'Radius of a virtual ball that is rolled along the macromolecule.',
		'sprobe' : 'Radius of a virtual ball that is needs to fit inside of the channel or cavity.',
		'bprobe' : 'Radius of a virtual ball that rolls on the outside of the protein, but does not fit inside.',
		'smallprobe' : 'Radius of a virtual ball that is needs to fit inside of the channel or cavity.',
		'bigprobe' : 'Radius of a virtual ball that rolls on the outside of the protein, but does not fit inside.',
		'maxprobe' : 'Maximum radius of a virtual ball that for a range or probe sizes.',
		'minprobe' : 'Minimum radius of a virtual ball that for a range or probe sizes.',
		'probestep' : 'Radial stepsize for a range or probe sizes: min, min+step, min+step*2, ..., max-step, max.',
		'coord' : 'x,y,z coordinate contained in channel.',

		'minvolume' : 'The minimum accessible volume a channel or cavity needs to have in order to be extracted. The is not the moecular or excluded volume. The accessible volume is significantly less than the excluded volume.',
		'minpercent' : 'The minimum percent volume, in terms of the big probe volume, a channel or cavity needs to have in order to be extracted.',
		'numchan' : 'Extract the N largest channel from the structure independent of their volume.',

		'effrad'  : 'Effective radius, the radius of a sphere that has the same surface area to volume ratio as the object in question. R_eff = 3*V/A.',
		'voxel'  : 'The size of the three dimensional grid point. A voxel is short for a volume element, similar to a pixel short for a picture element.',
		'volume'  : 'The total volume of the object, in cubic Angstroms. This is determined by counting the occupied voxels.',
		'surfarea'  : 'The surface area of the object, in square Angstroms. This is determined by counting the different types of surface voxels and multiplying by weighting factor, see Voss et al., 2006.',
		'sphericity'  : 'Sphericity is a measure of how much the volume resembles a sphere. A perfect sphere has a sphericity of 1.0, a cube has a sphericity of 0.81. Sphericity is determined from the volume and surface area of an object. &Psi; = (36&pi;V<sup>2</sup>)<sup>1/3</sup>/A.',
		'com'  : 'The center of mass is defined as the average position of all the occupied voxels. This is not necessarily located inside the volume.',
		'reducedcenter'  : 'The reduced center is the center of mass of the reduced volume. The CoM is less prone to large extermities of the channel. The reduced volume is obtained by iteratively removing all voxels on the surface until only the core voxels remain. For a channel, you can use the center of mass as input for the Single Channel Extract.',
		'pymol' : 'By default the MRC/CCP4 file contain integers, but pymol requires floats, so this converts the data to floats',
		'waterpdb' : 'Create a PDB file with a water molecule at each voxel location',
		'flatmethod' : 'Method to create flat surface for 3D printing. Trim: cut off large surface, Bisect: cut model in half',
	}
}
