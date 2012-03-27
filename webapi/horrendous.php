<?php

$config = parse_ini_file('config.ini');

$data = $HTTP_RAW_POST_DATA;
$key = file_get_contents($config['key']);

$ldap_connection = ldap_connect($config['ldap_host'],
                                isset($config['ldap_port']) ?
                                    $config['ldap_port'] :
                                    389);
ldap_bind($ldap_connection, $config['ldap_rdn'], $config['ldap_pw']);

$iv = substr($data, 0, 16);
$data = substr($data, 16);

$decrypted = mcrypt_decrypt(MCRYPT_RIJDAEL_256, $key, $data,
                            MCRYPT_MODE_CBC, $iv);

$arguments = json_decode($decrypted);

$username = $arguments['username'];
$query = str_replace('?', $username, $config['ldap_query']);

if (!empty($arguments['scanned'])) {
    $output = 'cannot scan in yet';
} else {
    $results_id = ldap_search($ldap_connection, $query, 'uid=*');
    $results = ldap_get_entries($ldap_connection, $results_id);
    $output = array('username'  => $results[0]['uid'][0],
                    'fullname'  => $results[0]['cn'][0] . ' ' .
                                   $results[0]['sn'][0],
                    'media_consent' => true,
                    'checked_in' => false);
}

$output = json_encode($output);

header('Content-type: application/json');
header('Content-length: ' . strlen($output));

echo json_encode($output);

