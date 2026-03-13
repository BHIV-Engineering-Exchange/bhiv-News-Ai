# Test JWT Authentication
try {
    $body = @{
        username = "demo"
        password = "demo123"
    } | ConvertTo-Json
    
    Write-Host "Testing authentication with demo credentials..."
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/login" -Method POST -Body $body -ContentType "application/json"
    
    Write-Host "✅ Authentication successful!"
    Write-Host "Token: $($response.access_token)"
    Write-Host "Token Type: $($response.token_type)"
    Write-Host "Expires In: $($response.expires_in) seconds"
    
    # Test token validation
    Write-Host "`nTesting token validation..."
    $headers = @{
        "Authorization" = "Bearer $($response.access_token)"
    }
    
    $protected_response = Invoke-RestMethod -Uri "http://localhost:8000/api/scrape" -Method POST -Headers $headers -Body '{"url":"https://example.com/news"}' -ContentType "application/json"
    Write-Host "✅ Token validation successful!"
    
} catch {
    Write-Host "❌ Authentication failed: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $responseBody = $reader.ReadToEnd()
        Write-Host "Response: $responseBody"
    }
}