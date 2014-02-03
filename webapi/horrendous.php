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

$matched = substr($data, 0, strlen($key)) == $key;
if (!$matched) {
    deny('Nope.');
}
$data = substr($data, strlen($key));

$arguments = json_decode($data, true);

$username = $arguments['username'];

if (!empty($arguments['scanned'])) {
    date_default_timezone_set('UTC');
    file_put_contents("$userdir/$username", date('r'));
    $output = 'cannot scan in yet';
} else {
    $output['checked_in'] = file_exists("$userdir/$username");
}

$output = json_encode($output, JSON_FORCE_OBJECT);

header('Content-type: application/json');
header('Content-length: ' . strlen($output));

echo $output;

