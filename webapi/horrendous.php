<?php

function deny($message) {
    header("HTTP/1.1 418 $message");
    header('Content-type: text/plain');
    header('Content-length: ' . (strlen($message)) + 1);
    echo "$message\n";
    exit();
}

$config = parse_ini_file('config.ini');

$data = $HTTP_RAW_POST_DATA;
if (!$data) {
    deny('No data.');
}
$key = file_get_contents($config['key']);
$userdir = $config['users_dir'];

$ldap_connection = ldap_connect($config['ldap_host'],
                                isset($config['ldap_port']) ?
                                    $config['ldap_port'] :
                                    389);
ldap_bind($ldap_connection, $config['ldap_rdn'], $config['ldap_pw']);

$matched = substr($data, 0, strlen($key)) == $key;
if (!$matched) {
    deny('Nope.');
}
$data = substr($data, strlen($key));

$arguments = json_decode($data);

$username = $arguments['username'];
$query = str_replace('?', $username, $config['ldap_query']);

if (!empty($arguments['scanned'])) {
    date_default_timezone_set('UTC');
    file_put_contents("$user_dir/$username", date('r'));
    $output = 'cannot scan in yet';
} else {
    $results_id = ldap_search($ldap_connection, $query, 'uid=*');
    $results = ldap_get_entries($ldap_connection, $results_id);
    $output = array();
    if (count($results) > 0) {
        $username = $results[0]['uid'][0];
        $outputs['username'] = $username;
        $outputs['fullname'] = $results[0]['cn'][0] . ' ' . $results[0]['sn'][0];
    } else {
        $outputs['fullname'] = $username;
    }
    $outputs['checked_in'] = file_exists("$user_dir/$username");
}

$output = json_encode($output, JSON_FORCE_OBJECT);

header('Content-type: application/json');
header('Content-length: ' . strlen($output));

echo $output;

