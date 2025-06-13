import json
import os
import logging
import boto3
import requests
from typing import Dict, Any
from datetime import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)

logs_client = boto3.client('logs')
ssm_client = boto3.client('ssm')

def get_parameter(parameter_name: str) -> str:
    """Gets a parameter from SSM. Returns the value or raises an error."""
    try:
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True  # needed for the Slack webhook
        )
        return response['Parameter']['Value']
    except Exception as e:
        logger.error(f"Failed to get parameter {parameter_name}: {str(e)}")
        raise

def iso8601_to_epoch_millis(iso_str: str) -> int:
    """Converts an ISO 8601 timestamp string to milliseconds since epoch."""
    try:
        dt = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%f%z")
        return int(dt.timestamp() * 1000)
    except Exception as e:
        logger.error(f"Failed to parse timestamp '{iso_str}': {str(e)}")
        raise

def get_error_logs(log_group_name: str, start_time: int) -> list:
    """Looks for ERROR messages in the logs. Returns a list of matching events."""
    try:
        response = logs_client.filter_log_events(
            logGroupName=log_group_name,
            startTime=start_time,
            filterPattern='"ERROR"'  # simple but effective
        )
        return response.get('events', [])
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise

def send_to_slack(webhook_url: str, message: Dict[str, Any]) -> bool:
    """Sends a message to Slack. Returns True if successful."""
    try:
        response = requests.post(
            webhook_url,
            json=message,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Failed to send to Slack: {str(e)}")
        return False

def format_slack_message(error_logs: list) -> Dict[str, Any]:
    """Makes the error logs look nice in Slack."""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "🚨 Error Logs Detected"
            }
        }
    ]
    
    for log in error_logs:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Timestamp:* {log['timestamp']}\n*Message:* {log['message']}"
            }
        })

    return { "blocks": blocks }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        log_group_name = get_parameter('log-group')
        slack_webhook_url = get_parameter('slack-webhook-url')

        alarm_time_str = event.get('time')
        if not alarm_time_str:
            raise ValueError("Missing 'time' in event payload")

        BUFFER_SECONDS = 120  # 2 minutes
        start_time = iso8601_to_epoch_millis(alarm_time_str) - (BUFFER_SECONDS * 1000)

        error_logs = get_error_logs(log_group_name, start_time)

        if not error_logs:
            logger.info("No errors found - all good!")
            return {
                'statusCode': 200,
                'body': json.dumps('No errors found')
            }

        slack_message = format_slack_message(error_logs)
        if send_to_slack(slack_webhook_url, slack_message):
            logger.info("Successfully sent to Slack")
            return {
                'statusCode': 200,
                'body': json.dumps('Sent to Slack')
            }
        else:
            raise Exception("Failed to send to Slack")

    except Exception as e:
        logger.error(f"Something went wrong: {str(e)}")
        raise

