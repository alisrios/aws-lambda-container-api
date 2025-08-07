# Test Lambda Container
$body = '{"httpMethod":"GET","path":"/hello","queryStringParameters":null}'
$response = Invoke-WebRequest -Uri "http://localhost:9000/2015-03-31/functions/function/invocations" -Method POST -Body $body -ContentType "application/json"
Write-Output $response.Content