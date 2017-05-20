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
 
class auth_django extends dokuwiki_auth_plugin {
	var $link = null;
 
	/**
	 * Constructor.
	 *
	 * Sets additional capabilities and config strings
	 * @author    Michael Luggen <michael.luggen at rhone.ch>
	 * @author    Robert Czechowski <zgtm at zgtm.de>
	 */
	function auth_django(){
		global $conf;
		$this->cando['external'] = true;
		$this->cando['getGroups'] = true;
		$this->cando['logout'] = false;
 
		
		try {
			// Connecting, selecting database
            $this->dbh = new PDO($conf['auth']['django']['protocol']':host='.$conf['auth']['django']['server'].';dbname='.$conf['auth']['django']['db'], $conf['auth']['django']['user'], $conf['auth']['django']['password']);
        } catch (PDOException $e) {
            $this->success = false;
        }
	}
 
	
	function trustExternal($user,$pass,$sticky=false){
		global $USERINFO;
		global $conf;
		$sticky ? $sticky = true : $sticky = false; //sanity check
 
        /**
         * Just checks against the django sessionid variable, 
         * gets user info from django-database
         */
		if (isset($_COOKIE['sessionid'])) {
		
			$s_id =  $_COOKIE['sessionid'];
 
			// Look the cookie up in the db 
			$query = 'SELECT session_data FROM django_session WHERE session_key=' . $this->dbh->quote($s_id) . ' LIMIT 1;';
			$ar = $this->dbh->query($query) or die('Query failed: ' . $this->dbh->errorInfo());
			$session_data = str_replace("\n",'',$ar[0]);
 
			//decrypting the session_data
			$session_json = preg_split('/:/', base64_decode($session_data), 2)[1]
			$userid = json_decode($session_json, true)['_auth_user_id'];
 
			$query = 'SELECT username, first_name, last_name, email FROM auth_user WHERE id=' . $this->dbh->quote($userid) . ' LIMIT 1;';
 
			$user = $this->dbh->query($query) or die('Query failed: ' . $this->dbh->errorInfo());
 
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
 
		$result = $this->dbh->query($query) or die('Query failed: ' . $this->dbh->errorInfo());
		$a = 0;
		foreach ($result as $row) {
			$groups[$a] = $row[0];
			$a++;
		};
		return $groups;
	}
 
	function retrieveGroups($start=0,$limit=0){
		$query = 'SELECT auth_group.name FROM auth_group';
 
		$result = $this->dbh->query($query) or die('Query failed: ' . $this->dbh->errorInfo());
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
