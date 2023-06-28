aws ecr get-login-password --region <aws_region> | docker login --username aws --password-stdin <amazon_user_id>.dkr.ecr.<aws_region>.amazonaws.com<amazon_user_id>

docker pull <amazon_user_id>.dkr.ecr.<aws_region>.amazonaws.com/<ecr_repo_name>:latest

docker run <amazon_user_id>.dkr.ecr.<aws_region>.amazonaws.com/<ecr_repo_name>:latest

docker system prune -a -f