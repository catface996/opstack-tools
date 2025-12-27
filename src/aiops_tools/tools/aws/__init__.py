"""AWS cloud resource management tools.

Tools:
- aws_list_ec2_instances: List EC2 instances
- aws_describe_instance: Get EC2 instance details
- aws_list_s3_buckets: List S3 buckets
- aws_list_s3_objects: List objects in S3 bucket
- aws_describe_rds: Get RDS instance details
- aws_get_cloudwatch_metrics: Get CloudWatch metrics
"""

AWS_TOOLS = [
    "aws_list_ec2_instances",
    "aws_describe_instance",
    "aws_list_s3_buckets",
    "aws_list_s3_objects",
    "aws_describe_rds",
    "aws_get_cloudwatch_metrics",
]

__all__ = ["AWS_TOOLS"]
