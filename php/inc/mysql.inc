<?php

/**
 *  Minimal mysqli wrapper based on the original Leginon mysql helper.
 */

class mysql {

	var $db_host;
	var $db_user;
	var $db_pass;
	var $db;
	var $sqldefault = array();
	var $SQL = array(
		'showcolumns' => 1,
		'where' => " WHERE 1 "
	);
	var $crlf = "\n";
	var $mysqli = null;
	var $mysqlerror;
	var $mysqlerrornb;
	var $sqlquery;

	function __construct($db_host, $db_user, $db_pass, $db) {
		$this->db_host = $db_host;
		$this->db_user = $db_user;
		$this->db_pass = $db_pass;
		$this->db = $db;
		$this->sqldefault['db_host'] = $db_host;
		$this->sqldefault['db_user'] = $db_user;
		$this->sqldefault['db_pass'] = $db_pass;
		$this->sqldefault['db'] = $db;
	}

	function mysql($db_host, $db_user, $db_pass, $db) {
		self::__construct($db_host, $db_user, $db_pass, $db);
	}

	function getDBInfo() {
		return "\n\t\thostname: " . $this->db_host . "\n\t\tdatabase: " . $this->db . "\n\t\tuser: " . $this->db_user;
	}

	function connect_db($host="") {
		$host = (empty($host)) ? $this->db_host : $host;
		$link = @mysqli_connect($host, $this->db_user, $this->db_pass, $this->db);
		if (!$link) {
			$this->mysqlerror = "Error: " . mysqli_connect_error();
			$this->mysqlerrornb = mysqli_connect_errno();
			return false;
		}
		$this->mysqli = $link;
		return $link;
	}

	function checkDBConnection($host="") {
		$resource = $this->connect_db($host);
		if ($resource instanceof mysqli) {
			$this->close_db($resource);
			return true;
		}
		return false;
	}

	function close_db($resource_link="") {
		$link = $resource_link ?: $this->mysqli;
		if ($link instanceof mysqli) {
			@mysqli_close($link);
			if ($link === $this->mysqli) {
				$this->mysqli = null;
			}
		}
	}

	function SQLTableExists($name) {
		$table_exists = false;
		$Rtables = $this->SQLQuery("SHOW TABLES");
		if ($Rtables) {
			while ($table = mysqli_fetch_array($Rtables)) {
				if ($table[0] == $name) {
					$table_exists = true;
					break;
				}
			}
		}
		return $table_exists;
	}

	function getSQLTableDefinition($table) {
		$crlf = $this->crlf;
		$backquotestr = '`';
		$schema_create = "";
		$schema_create .= "CREATE TABLE IF NOT EXISTS $table ($crlf";

		$result = $this->SQLQuery("SHOW FIELDS FROM $table");
		if (!$result) {
			die("show fields error: " . $this->mysqlerror);
		}
		while ($row = mysqli_fetch_array($result)) {
			$schema_create .= "   $backquotestr" . $row['Field'] . "$backquotestr " . $row['Type'];
			if (isset($row["Default"]) && ($row["Default"] !== "" || $row["Default"] === "0")) {
				if ($row["Type"] == 'timestamp') {
					$schema_create .= " DEFAULT " . $row['Default'];
				} else {
					$schema_create .= " DEFAULT '" . $row['Default'] . "'";
				}
			}
			if ($row["Null"] != "YES")
				$schema_create .= " NOT NULL";
			if ($row["Extra"] != "")
				$schema_create .= " " . $row['Extra'];
			$schema_create .= ",$crlf";
		}
		$schema_create = preg_replace("/," . preg_quote($crlf, '/') . "$/", "", $schema_create);
		$result = $this->SQLQuery("SHOW KEYS FROM $table");
		if (!$result)
			die($this->mysqlerror);
		while ($row = mysqli_fetch_array($result)) {
			$kname = $row['Key_name'];
			if (($kname != "PRIMARY") && ($row['Non_unique'] == 0))
				$kname = "UNIQUE|$kname";
			if (!isset($index[$kname]))
				$index[$kname] = array();
			$index[$kname][] = $row['Column_name'];
		}

		if (!empty($index)) {
			foreach ($index as $x => $columns) {
				$schema_create .= ",$crlf";
				if ($x == "PRIMARY")
					$schema_create .= "   PRIMARY KEY (" . implode($columns, ", ") . ")";
				elseif (substr($x, 0, 6) == "UNIQUE")
					$schema_create .= "   UNIQUE " . substr($x, 7) . " (" . implode($columns, ", ") . ")";
				else
					$schema_create .= "   KEY $x (" . implode($columns, ", ") . ")";
			}
		}

		$schema_create .= "$crlf);$crlf";
		return stripslashes($schema_create);
	}

	function getSQLTableContent($table, &$content, $where="1") {
		$crlf = $this->crlf;
		$local_query = "SELECT * FROM $table WHERE $where";
		$result = $this->SQLQuery($local_query);
		if (!$result)
			die($this->mysqlerror);
		while ($row = mysqli_fetch_row($result)) {
			set_time_limit(60);
			$table_list = "(";
			$num_fields = mysqli_num_fields($result);
			for ($j = 0; $j < $num_fields; $j++) {
				$field = mysqli_fetch_field_direct($result, $j);
				$table_list .= "`" . $field->name . "`, ";
			}
			$table_list = substr($table_list, 0, -2);
			$table_list .= ")";

			if (isset($this->SQL["showcolumns"]))
				$schema_insert = "INSERT INTO $table $table_list VALUES (";
			else
				$schema_insert = "INSERT INTO $table VALUES (";

			for ($j = 0; $j < $num_fields; $j++) {
				if (!isset($row[$j]))
					$schema_insert .= " NULL,";
				elseif ($row[$j] != "")
					$schema_insert .= " '" . addslashes($row[$j]) . "',";
				else
					$schema_insert .= " '',";
			}
			$schema_insert = preg_replace(",$/,", "", $schema_insert);
			$schema_insert .= ")";
			$content .= trim($schema_insert) . ";$crlf";
		}
		return true;
	}

	function setSQLHost($sqlhost) {
		if (!is_array($sqlhost))
			$sqlhost = array();
		$this->db_host = (array_key_exists('db_host', $sqlhost)) ? $sqlhost['db_host'] : $this->sqldefault['db_host'];
		$this->db_user = (array_key_exists('db_user', $sqlhost)) ? $sqlhost['db_user'] : $this->sqldefault['db_user'];
		$this->db_pass = (array_key_exists('db_pass', $sqlhost)) ? $sqlhost['db_pass'] : $this->sqldefault['db_pass'];
		$this->db = (array_key_exists('db', $sqlhost)) ? $sqlhost['db'] : $this->sqldefault['db'];
		return true;
	}

	function getSQLHost() {
		return $this->db_host;
	}

	function getError() {
		return $this->mysqlerror;
	}

	function getErrorNumber() {
		return $this->mysqlerrornb;
	}

	function getSQLQuery() {
		return $this->sqlquery;
	}

	function SQLQuery($query, $insert=false) {
		$this->sqlquery = $query;
		$link = $this->connect_db($this->db_host);
		if (!$link)
			return false;
		$result = mysqli_query($link, $query);
		if (!$result) {
			$this->mysqlerror = "Error: " . mysqli_error($link);
			$this->mysqlerrornb = mysqli_errno($link);
			$this->close_db($link);
			return false;
		}
		if ($insert) {
			$res = mysqli_insert_id($link);
			$this->close_db($link);
			return $res;
		}
		$this->close_db($link);
		return $result;
	}

	function getSQLResult($query, $fetch=MYSQLI_ASSOC) {
		$result = $this->SQLQuery($query);
		if (!$result)
			return false;
		if (!($result instanceof mysqli_result))
			return $result;
		$data = array();
		while ($row = mysqli_fetch_array($result, $fetch))
			$data[] = $row;
		return $data;
	}

	function SQLQueries($queries) {
		$link = $this->connect_db($this->db_host);
		if (!$link)
			return false;
		$q = (is_array($queries)) ? $queries : array($queries);
		foreach ($q as $v) {
			if (!mysqli_query($link, $v)) {
				die("Error: $v" . mysqli_error($link));
			}
		}
		$this->close_db($link);
		return true;
	}

	function SQLInsert($table, $data) {
		if (!$data || !$table || !is_array($data))
			return false;
		$fields = array_keys($data);
		foreach ($fields as $k => $v)
			$fields[$k] = "`" . $v . "`";
		foreach ($data as $k => $v)
			if (!is_numeric($v))
				$data[$k] = "'" . addslashes($v) . "'";
		$q = "INSERT INTO `$table` (" . implode(', ', $fields) . ") VALUES (" . implode(', ', $data) . ")";
		return $this->SQLQuery($q, true);
	}

	function array_to_sql($data) {
		if (!$data || !is_array($data))
			return false;
		$sqlformat = array();
		foreach ($data as $k => $v) {
			if (!is_numeric($v))
				$v = "'" . addslashes($v) . "'";
			$sqlformat[] = "`$k`=" . $v;
		}
		$sql = join(' AND ', $sqlformat);
		return $sql;
	}

	function array_to_select($data) {
		if (!$data || !is_array($data))
			return false;
		$sqlformat = array();
		foreach ($data as $field) {
			$sqlformat[] = "`$field`";
		}
		$sql = join(', ', $sqlformat);
		return $sql;
	}

	function SQLInsertIfNotExists($table, $data, $return_id=false) {
		if (!$sql = $this->array_to_sql($data))
			return false;
		$field = "1";
		$pKey = null;
		if ($return_id) {
			$pKey = $this->getPriKey($table);
			if ($pKey)
				$field = $pKey;
		}
		$q = "SELECT $field from `$table` WHERE $sql";
		$res = $this->SQLQuery($q);
		if ($res && mysqli_num_rows($res) > 0) {
			if ($return_id && $pKey) {
				$result = mysqli_fetch_array($res);
				return $result[$pKey];
			}
			return true;
		} else {
			$id = $this->SQLInsert($table, $data);
			if (is_bool($id) && !$id)
				return false;
			if ($return_id && $id)
				return $id;
			return true;
		}
	}

	function SQLUpdate($table, $data, $where="") {
		if (!$data || !$table || !is_array($data))
			return false;
		$wherestr = "";
		if (is_array($where)) {
			$wherestr = " WHERE ";
			foreach ($where as $k => $v)
				$whereformat[] = "`$k`='" . addslashes($v) . "'";
			$wherestr .= implode(' AND ', $whereformat);
		} else if (!empty($where)) {
			$wherestr .= $where;
		}
		foreach ($data as $k => $v) {
			if (!is_numeric($v))
				$v = "'" . addslashes($v) . "'";
			$kv[] = "`" . $k . "`=" . $v;
		}
		$q = "UPDATE `$table` SET " . implode(', ', $kv) . $wherestr;
		if (!$this->SQLQuery($q))
			return false;
		return true;
	}

	function SQLDelete($table, $where="") {
		if (!$table)
			return false;
		$wherestr = "";
		if (is_array($where)) {
			$wherestr = " WHERE ";
			foreach ($where as $k => $v)
				$whereformat[] = "`$k`='" . addslashes($v) . "'";
			$wherestr .= implode(' AND ', $whereformat);
		} else if (!empty($where)) {
			$wherestr .= $where;
		}
		$q = "DELETE FROM `$table` " . $wherestr;
		if (!$this->SQLQuery($q))
			return false;
		return true;
	}

	function SQLAlterTables($sqldef, $fieldtypes) {
		if (!is_array($fieldtypes) || !is_array($sqldef))
			return false;
		$changes = "";
		$q = array();
		foreach ($fieldtypes as $table => $fieldtype) {
			if ($this->SQLTableExists($table)) {
				$orgfieldtype = $this->getFieldTypes($table);
				foreach ($fieldtype as $f => $t) {
					if (preg_match('/^DEF_/', $f))
						continue;
					if (!isset($orgfieldtype[$f])) {
						$q[] = "ALTER TABLE `$table` ADD `$f` $t";
						$changes .= "ADD $table $f  => $t <br>";
					} else if ($orgfieldtype[$f] != $t) {
						$q[] = "ALTER TABLE `$table` CHANGE `$f` `$f` $t";
						$changes .= "CHANGE $table $f  => $t <br>";
					}
				}
			} else {
				$q[] = $sqldef[$table];
				$changes .= "CREATE $table <br>";
			}
		}
		if (!empty($q))
			$this->SQLQueries($q);
		if ($changes)
			return $changes;
		return false;
	}

	function getPriKey($table) {
		$prikey = false;
		if ($table && $this->SQLTableExists($table)) {
			$R = $this->SQLQuery("SHOW FIELDS FROM `$table`");
			while ($r = mysqli_fetch_array($R)) {
				if ($r['Key'] == 'PRI') {
					$prikey = $r['Field'];
					break;
				}
			}
		}
		return $prikey;
	}

	function getFields($table) {
		$fields = array();
		if ($table && $this->SQLTableExists($table)) {
			$R = $this->SQLQuery("SHOW FIELDS FROM `$table`");
			while ($r = mysqli_fetch_array($R))
				$fields[] = $r['Field'];
		}
		return $fields;
	}

	function getTableDescription($table) {
		$fields = array();
		if ($table && $this->SQLTableExists($table)) {
			return $this->getSQLResult("DESCRIBE `$table`");
		}
		return $fields;
	}

	function getFieldTypes($table) {
		$fields = array();
		if ($table) {
			$R = $this->SQLQuery("SHOW FIELDS FROM `$table`");
			while ($r = mysqli_fetch_array($R))
				$fields[$r['Field']] = $r['Type'];
		}
		return $fields;
	}

	function getTables() {
		$tables = array();
		$R = $this->SQLQuery("SHOW TABLES ");
		if ($R) {
			while ($row = mysqli_fetch_row($R))
				$tables[] = $row[0];
		}
		return $tables;
	}

	function isTable($table) {
		$tables = $this->getTables();
		return in_array($table, $tables);
	}

	function getId($parameters) {
		if (!$table = $parameters['table'])
			return false;
		if (!$where_fields = $parameters['where'])
			$where_fields = array();
		if (!$id = $parameters['id'])
			$id = $this->getPriKey($table);

		$acq_fields = $this->getFields($table);
		$where = array();
		foreach ($where_fields as $k => $f) {
			if (!in_array($k, $acq_fields))
				return false;
			$where[] = "`$k`='" . addslashes($f) . "'";
		}
		if (empty($where))
			return false;
		$wherestr = implode(' and ', $where);
		$q = 'select `' . $id . "` as id from `" . $table . '` where ' . $wherestr;
		$R = $this->SQLQuery($q);
		$ids = array();
		if ($R) {
			while ($r = mysqli_fetch_array($R))
				$ids[] = $r['id'];
		}

		if (count($ids) == 1)
			return $ids[0];
		else
			return $ids;
	}

	function getData($parameters) {
		if (!$table = $parameters['table'])
			return false;
		if (!$select = $this->array_to_select($parameters['field']))
			return false;
		$sql_where = "";
		if (is_array($parameters['where'])) {
			$sql_where = $this->array_to_sql($parameters['where']);
			if ($sql_where)
				$sql_where = "WHERE $sql_where";
		}
		$sql_order = $parameters['order'] ?: "";
		$sql_limit = $parameters['limit'] ?: "";
		$q = "SELECT $select from `$table` " . $sql_where . $sql_order . $sql_limit;
		return $this->getSQLResult($q);
	}

}



?>
