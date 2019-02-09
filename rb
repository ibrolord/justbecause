 aws s3 ls --profile me2 | awk '{print $3}' | while IFS= read -r line; do aws s3 rb s3://$line --force --profile me2; done
