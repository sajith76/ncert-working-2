
$body = @{
    student_id = "student123"
    class_level = 10
    subject = "Chemistry"
    chapter_number = 1
    topic_id = "all"
    num_questions = 5
    auto_generate = $true
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/api/test/start-v2" -Method POST -Body $body -ContentType "application/json" | ConvertTo-Json -Depth 5
