"""Get CloudWatch metrics for AWS resources."""

from datetime import datetime, timedelta, timezone

TOOL_DEFINITION = {
    "name": "aws_get_cloudwatch_metrics",
    "display_name": "Get CloudWatch Metrics",
    "description": "Retrieve CloudWatch metrics for AWS resources. Supports common metrics for EC2, RDS, and other services.",
    "tags": ["aws", "cloudwatch", "metrics", "monitoring"],
    "input_schema": {
        "type": "object",
        "properties": {
            "region": {"type": "string"},
            "namespace": {
                "type": "string",
                "description": "CloudWatch namespace (e.g., AWS/EC2, AWS/RDS)",
            },
            "metric_name": {
                "type": "string",
                "description": "Metric name (e.g., CPUUtilization, DatabaseConnections)",
            },
            "dimensions": {
                "type": "array",
                "description": "Dimensions to filter metrics",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "value": {"type": "string"},
                    },
                },
            },
            "period": {
                "type": "integer",
                "description": "Period in seconds for data points",
                "default": 300,
            },
            "statistic": {
                "type": "string",
                "enum": ["Average", "Sum", "Minimum", "Maximum", "SampleCount"],
                "default": "Average",
            },
            "start_time": {
                "type": "string",
                "description": "Start time (ISO 8601 or relative like '-1h')",
            },
            "end_time": {
                "type": "string",
                "description": "End time (ISO 8601 or 'now')",
            },
            "aws_access_key_id": {"type": "string"},
            "aws_secret_access_key": {"type": "string"},
        },
        "required": ["region", "namespace", "metric_name", "dimensions"],
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "success": {"type": "boolean"},
            "data": {
                "type": "object",
                "properties": {
                    "namespace": {"type": "string"},
                    "metric_name": {"type": "string"},
                    "datapoints": {"type": "array"},
                    "period": {"type": "integer"},
                    "statistic": {"type": "string"},
                },
            },
        },
    },
}


def _get_boto_session(input_data: dict):
    """Get boto3 session with credentials from input or environment."""
    import boto3

    if input_data.get("aws_access_key_id") and input_data.get("aws_secret_access_key"):
        return boto3.Session(
            aws_access_key_id=input_data["aws_access_key_id"],
            aws_secret_access_key=input_data["aws_secret_access_key"],
            region_name=input_data.get("region"),
        )
    return boto3.Session(region_name=input_data.get("region"))


def _parse_time(time_str: str | None, default_delta: timedelta = None) -> datetime:
    """Parse time string to datetime.

    Supports:
    - ISO 8601 format
    - 'now'
    - Relative times like '-1h', '-30m', '-1d'
    """
    if not time_str:
        if default_delta:
            return datetime.now(timezone.utc) + default_delta
        return datetime.now(timezone.utc)

    if time_str == "now":
        return datetime.now(timezone.utc)

    if time_str.startswith("-"):
        # Relative time
        value = int(time_str[1:-1])
        unit = time_str[-1]
        if unit == "h":
            return datetime.now(timezone.utc) - timedelta(hours=value)
        elif unit == "m":
            return datetime.now(timezone.utc) - timedelta(minutes=value)
        elif unit == "d":
            return datetime.now(timezone.utc) - timedelta(days=value)

    # Try ISO format
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def main(input_data: dict) -> dict:
    """Get CloudWatch metrics.

    Args:
        input_data: Dictionary with region, namespace, metric_name, dimensions, optional period/statistic/time range

    Returns:
        Dictionary with success status and metric data or error
    """
    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError
    except ImportError:
        return {
            "success": False,
            "error": {
                "code": "AWS_IMPORT_ERROR",
                "message": "boto3 package not installed",
            },
        }

    region = input_data.get("region")
    namespace = input_data.get("namespace")
    metric_name = input_data.get("metric_name")
    dimensions = input_data.get("dimensions", [])
    period = input_data.get("period", 300)
    statistic = input_data.get("statistic", "Average")
    start_time_str = input_data.get("start_time")
    end_time_str = input_data.get("end_time")

    if not all([region, namespace, metric_name, dimensions]):
        return {
            "success": False,
            "error": {
                "code": "AWS_INVALID_INPUT",
                "message": "region, namespace, metric_name, and dimensions are required",
            },
        }

    try:
        # Parse times
        end_time = _parse_time(end_time_str)
        start_time = _parse_time(start_time_str, default_delta=timedelta(hours=-1))

        session = _get_boto_session(input_data)
        cloudwatch = session.client("cloudwatch")

        # Build dimensions for API
        api_dimensions = [
            {"Name": d["name"], "Value": d["value"]}
            for d in dimensions
        ]

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=api_dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=[statistic],
        )

        # Sort datapoints by timestamp
        datapoints = sorted(
            response.get("Datapoints", []),
            key=lambda x: x["Timestamp"],
        )

        formatted_datapoints = []
        for dp in datapoints:
            formatted_datapoints.append({
                "timestamp": dp["Timestamp"].isoformat(),
                "value": dp.get(statistic, 0),
                "unit": dp.get("Unit", "None"),
            })

        return {
            "success": True,
            "data": {
                "namespace": namespace,
                "metric_name": metric_name,
                "datapoints": formatted_datapoints,
                "period": period,
                "statistic": statistic,
            },
        }

    except NoCredentialsError:
        return {
            "success": False,
            "error": {
                "code": "AWS_AUTH_ERROR",
                "message": "No AWS credentials found",
            },
        }
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        if error_code == "Throttling":
            return {
                "success": False,
                "error": {
                    "code": "AWS_RATE_LIMITED",
                    "message": "Rate limit exceeded. Try again later.",
                },
            }
        return {
            "success": False,
            "error": {
                "code": "AWS_ERROR",
                "message": str(e),
            },
        }
    except Exception as e:
        return {
            "success": False,
            "error": {
                "code": "AWS_ERROR",
                "message": str(e),
            },
        }
