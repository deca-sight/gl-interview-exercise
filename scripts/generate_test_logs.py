import boto3
import time
import random
import logging
import argparse
from datetime import datetime
from botocore.exceptions import ClientError, ProfileNotFound, NoCredentialsError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_logs(log_group_name: str, log_stream_name: str, num_logs: int, region: str, profile: str = None):
    """Generate test logs with both normal and error messages."""
    try:
        session_args = {"region_name": region}
        if profile:
            session_args["profile_name"] = profile

        session = boto3.Session(**session_args)
        logs_client = session.client('logs')

        # Create log stream if it doesn't exist
        try:
            logs_client.create_log_stream(
                logGroupName=log_group_name,
                logStreamName=log_stream_name
            )
        except logs_client.exceptions.ResourceAlreadyExistsException:
            logger.info(f"Log stream {log_stream_name} already exists")
        except ClientError as ce:
            logger.error(f"Failed to create log stream: {ce.response['Error']['Message']}")
            return

        # Generate sequence token
        try:
            response = logs_client.describe_log_streams(
                logGroupName=log_group_name,
                logStreamNamePrefix=log_stream_name
            )
            sequence_token = response['logStreams'][0].get('uploadSequenceToken')
        except Exception as e:
            logger.error(f"Error getting sequence token: {str(e)}")
            sequence_token = None

        # Generate logs
        log_events = []
        for i in range(num_logs):
            timestamp = int(time.time() * 1000)
            message_type = "ERROR" if random.random() < 0.3 else "INFO"
            message = f"{message_type}: Test {message_type.lower()} message {i} at {datetime.fromtimestamp(timestamp/1000)}"
            log_events.append({'timestamp': timestamp, 'message': message})

        # Put logs
        try:
            kwargs = {
                'logGroupName': log_group_name,
                'logStreamName': log_stream_name,
                'logEvents': log_events
            }
            if sequence_token:
                kwargs['sequenceToken'] = sequence_token

            logs_client.put_log_events(**kwargs)
            logger.info(f"Successfully generated {num_logs} test logs")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"ClientError while putting logs: {e.response['Error']['Message']} ({error_code})")
        except Exception as e:
            logger.error(f"Unexpected error while putting logs: {str(e)}")

    except ProfileNotFound:
        logger.error(f"The specified AWS profile '{profile}' was not found.")
    except NoCredentialsError:
        logger.error("No AWS credentials found. Please configure your credentials.")
    except Exception as e:
        logger.error(f"Failed to initialize session or client: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate test logs for CloudWatch')
    parser.add_argument('--log-group', required=True, help='CloudWatch Log Group name')
    parser.add_argument('--log-stream', required=True, help='CloudWatch Log Stream name')
    parser.add_argument('--num-logs', type=int, default=10, help='Number of logs to generate')
    parser.add_argument('--region', default='us-east-1', help='AWS region (default: us-east-1)')
    parser.add_argument('--profile', help='AWS profile name (optional)')

    args = parser.parse_args()

    generate_test_logs(args.log_group, args.log_stream, args.num_logs, args.region, args.profile)

