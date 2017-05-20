<?php
/**
 * django auth backend
 *
 * Uses external trust mechanism to check against a django session id
 * Needs to run python3 to extract user from session data
 *
 * @author    Andreas Gohr <andi@splitbrain.org>
 * @author    Michael Luggen <michael.luggen at unifr.ch>
 * @author    Robert Czechowski <zgtm at zgtm.de>
 */
 
define('DOKU_AUTH', dirname(__FILE__));
define('AUTH_USERFILE',DOKU_CONF.'users.auth.php');

class auth_plugin_authdjango extends DokuWiki_Auth_Plugin  {

	var $dbh = null; // db handle

	/**
	 * Constructor.
	 *
	 * Sets additional capabilities and config strings
	 * @author    Michael Luggen <michael.luggen at rhone.ch>
	 * @author    Robert Czechowski <zgtm at zgtm.de>
	 */
	function auth_plugin_authdjango(){
		global $conf;
		global $config_cascade;
		global $dbh;

		$this->cando['external'] = true;
		$this->cando['getGroups'] = true;
		$this->cando['logout'] = false;
 

		try {
			// Connecting, selecting database
            $this->dbh = new PDO($conf['auth']['django']['protocol'] . ':host=' . $conf['auth']['django']['server'] . ';dbname=' . $conf['auth']['django']['db'], $conf['auth']['django']['user'], $conf['auth']['django']['password']);
        } catch (PDOException $e) {
            msg("Kann nicht zur Datenbank verbinden!", -1);
            $this->success = false;
        }
        $this->success = true;
	}
 
	
	function trustExternal($user,$pass,$sticky=false){
		global $USERINFO;
		global $conf;
		global $dbh;

		$sticky ? $sticky = true : $sticky = false; //sanity check

        /**
         * Just checks against the django sessionid variable,
         * gets user info from django-database
         */
		if (isset($_COOKIE['sessionid'])) {

			$s_id =  $_COOKIE['sessionid'];

			// Look the cookie up in the db
			$query = 'SELECT session_data FROM django_session WHERE session_key=' . $this->dbh->quote($s_id) . ' LIMIT 1;';
			$result = $this->dbh->query($query) or die('Query failed1: ' . $this->dbh->errorInfo());
			$ar = $result->fetch(PDO::FETCH_ASSOC);
			$session_data = $ar['session_data'];

			//decrypting the session_data
			$session_json = preg_split('/:/', base64_decode($session_data), 2)[1];
			$userid = json_decode($session_json, true)['_auth_user_id'];
            //die("" . $userid);
			$query2 = 'SELECT username, first_name, last_name, email FROM auth_user WHERE id=' . $this->dbh->quote($userid) . ' LIMIT 1;';

			$result2 = $this->dbh->query($query2) or die('Query failed2: ' . $this->dbh->errorInfo());
            $user = $result2->fetch(PDO::FETCH_ASSOC);

			$username =  $user['username'];
			$userfullname = $user['first_name'] . " " . $user['last_name'];
			$useremail = $user['email'];

			// okay we're logged in - set the globals
			$groups = $this->_getUserGroups($username);

			$USERINFO['name'] = $userfullname;
			$USERINFO['pass'] = '';
			$USERINFO['mail'] = $useremail;
			$groups[0] = 'user';
			$USERINFO['grps'] = $groups;

			$_SERVER['REMOTE_USER'] = $username;

			$_SESSION[DOKU_COOKIE]['auth']['user'] = $username;
			$_SESSION[DOKU_COOKIE]['auth']['info'] = $USERINFO;

			return true;
		}
		return false;
	}

	function _getUserGroups($user){
		$query = 'SELECT auth_group.name FROM auth_user, auth_user_groups, auth_group where auth_user.username = ' . $this->dbh->quote($user) . ' AND auth_user.id = auth_user_groups.user_id AND auth_user_groups.group_id = auth_group.id;';

		$result = $this->dbh->query($query) or die('Query failed3: ' . $this->dbh->errorInfo());
		$a = 0;
		foreach ($result as $row) {
			$groups[$a] = $row[0];
			$a++;
		};
		return $groups;
	}

	function retrieveGroups($start=0,$limit=0){
		$query = 'SELECT auth_group.name FROM auth_group';

		$result = $this->dbh->query($query) or die('Query failed4: ' . $this->dbh->errorInfo());
		$a = 0;
		foreach ($result as $row) {
			$groups[$a] = $row[0];
			$a++;
		};
		return $groups;
	}

	function __destruct() {
		$this->dbh = null;
	}
}
