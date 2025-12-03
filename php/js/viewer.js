/**
 *	The Leginon software is Copyright 2003 
 *	The Scripps Research Institute, La Jolla, CA
 *	For terms of the license agreement
 *	see  http://ami.scripps.edu/software/leginon-license
 */

var autoscale=false

function popUpMap(URL) {
	window.open(URL, "map"+window.name, "left=0,top=0,height=512,width=512,toolbar=0,scrollbars=0,location=0,statusbar=0,menubar=0,resizable=1,alwaysRaised=yes")
}

function popUpW(URL) {
	window.open(URL, "deq", "left=0,top=0,height=512,width=300,toolbar=0,scrollbars=1,location=0,statusbar=0,menubar=0,resizable=1,alwaysRaised=yes")
}

function cle(val) {
  eval(val)
}
