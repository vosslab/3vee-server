<?php

require_once "inc/mysql.inc";

define('DB_HOST', 'localhost');
define('DB_USER', 'vossman');
define('DB_PASS', '');
define('DB_NAME', 'threevdata');

class threevdata {
	var $crlf="\n";

	/*************************
	**************************
	*************************/
	function threevdata () {
		$this->mysql = new mysql(DB_HOST, DB_USER, DB_PASS, DB_NAME);
	}

	/*************************
	**************************
	*************************/
	function getMostRecentRuns ($count=1, $progname=false) {
		$q = "SELECT "
			."  run.*, path.path, name.name AS progname "
			."FROM ProgramRun AS run "
			."LEFT JOIN Path AS path "
			."  ON path.`DEF_id` = run.`REF|Path|path` ";
		$q .="LEFT JOIN ProgramName AS name "
			."  ON name.`DEF_id` = run.`REF|ProgramName|progname` ";
		$q .="WHERE "
			."  run.allowuse = 1 ";
		if($progname)
			$q .="AND "
				."  name.name = '$progname'";
		$q .="  ORDER BY run.`DEF_id` DESC "
			."LIMIT $count ";
		//echo $q."<br/><br/>\n";
		$r = $this->mysql->getSQLResult($q);
		//echo print_r($r)."<br/><br/>\n";
		return $r;
	}

	/*************************
	**************************
	*************************/
	function getJobData ($jobid) {
		$q = "SELECT "
			."  run.`DEF_id` AS runid, "
			." run.*, "
			//." name.*, "
			." path.path "
			."FROM ProgramRun AS run "
			."LEFT JOIN Path AS path "
			."  ON path.`DEF_id` = run.`REF|Path|path` ";
		//	."LEFT JOIN ProgramName AS name "
		//	."  ON name.`DEF_id` = run.`REF|ProgramName|progname` ";
		$q .="WHERE "
			."  run.jobid = '$jobid' ";
		$q .="  LIMIT 1 ";
		//echo $q."<br/><br/>\n";
		$r = $this->mysql->getSQLResult($q);
		//echo print_r($r)."<br/><br/>\n";
		return $r[0];
	}

	/*************************
	**************************
	*************************/
	function getJobParams ($jobid) {
		$jobdata = $this->getJobData($jobid);
		$runid = $jobdata['runid'];
		return $this->getRunParams($runid);
	}

	/*************************
	**************************
	*************************/
	function getRunParams ($runid) {
		$q = "SELECT "
			."  paramname.name AS name, "
			."  paramvalue.value AS value "
			."FROM ParamValue AS paramvalue "
			."LEFT JOIN ParamName AS paramname "
			."  ON paramname.`DEF_id` = paramvalue.`REF|ParamName|paramname` ";
		$q .="WHERE "
			."  paramvalue.`REF|ProgramRun|progrun` = '$runid' ";
		//echo $q."<br/><br/>\n";
		$rows = $this->mysql->getSQLResult($q);
		//echo print_r($r)."<br/><br/>\n";

		$hashed = array();
		foreach ($rows as $row) {
			$hashed[$row['name']] = $row['value'];
		}
		return $hashed;
	}
};


