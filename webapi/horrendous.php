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

$arguments = json_decode($data, true);

$username = $arguments['username'];
$query = str_replace('?', $username, $config['ldap_query']);

if (!empty($arguments['scanned'])) {
    date_default_timezone_set('UTC');
    file_put_contents("$userdir/$username", date('r'));
    $output = 'cannot scan in yet';
} else {
    $results_id = ldap_search($ldap_connection, $query, 'uid=*');
    $results = ldap_get_entries($ldap_connection, $results_id);
    $output = array();
    if (count($results) > 0) {
        $username = $results[0]['uid'][0];
        $output['username'] = $username;
        $output['fullname'] = $results[0]['cn'][0] . ' ' . $results[0]['sn'][0];
        $groups_id = ldap_search($ldap_connection, 'ou=groups,o=sr', "memberUid=$username");
        $groups_res = ldap_get_entries($ldap_connection, $groups_id);
        $org = 'Guest';
        $media = false;
        for ($i = 0; $i < $groups_res['count']; ++$i) {
            $group = $groups_res[$i];
            $name = $group['cn'][0];
            if ($name == 'mentors') {
                $org = 'Staff';
                $media = true;
                break;
            } else if ($name == 'media-consent-2012') {
                $media = true;
            } else if (preg_match('/team\\d+/', $name)) {
                $number = (int)substr($name, 4);
                $org = $config['teams'][$number];
            }
        }
        $output['organisation'] = $org;
        $output['media_consent'] = $media;
    } else {
        $output['fullname'] = $username;
    }
    $output['checked_in'] = file_exists("$userdir/$username");
}

$output = json_encode($output, JSON_FORCE_OBJECT);

header('Content-type: application/json');
header('Content-length: ' . strlen($output));

echo $output;

