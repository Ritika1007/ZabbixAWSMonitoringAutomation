<h1 align="center">Zabbix AWS Service Monitoring Automation</h1>

<p align="center">
  <strong>An automation tool for monitoring AWS services using Python, AWS CloudWatch, Boto3, Zabbix, and Zabbix APIs.</strong>
</p>

## Overview

This project is an automation tool that allows you to monitor various AWS services, including Amazon SQS, Amazon DynamoDB, Amazon RDS, Elastic Load Balancer (ELB), and Application Load Balancer (ALB). By leveraging the power of AWS CloudWatch, Boto3, Zabbix, and Zabbix APIs, you can easily collect metrics, track performance, and receive notifications for any anomalies in your AWS infrastructure.

## Features

- **Service Monitoring**: Monitor the health, performance, and utilization of your AWS services in real-time.
- **Customizable Metrics**: Easily customize the metrics you want to collect based on your specific monitoring needs.
- **Alerts and Notifications**: Set up alerts and receive notifications via Zabbix when predefined thresholds are exceeded.
- **Automatic Data Collection**: Automate the collection of metrics using Boto3 and AWS CloudWatch APIs.
- **Easy Integration**: Seamlessly integrate with your existing Zabbix server and leverage its powerful monitoring capabilities.

## Prerequisites

Before running this automation tool, make sure you have the following prerequisites:

- Python 3.x installed on your system
- AWS credentials set up with appropriate permissions to access the services you want to monitor
- Zabbix server and its APIs configured for communication

## 🚀 Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Ritika1007/ZabbixAWSMonitoringAutomation.git
   
2. Install the required Python packages: Boto3, requests
 
3. Configure AWS credentials:

   - If you have the AWS CLI installed, you can run `aws configure` to set up your access key, secret key, and default region.

   - Alternatively, you can manually edit the `~/.aws/credentials` file to include your AWS access key and secret key:

     ```
     [default]
     aws_access_key_id = YOUR_ACCESS_KEY
     aws_secret_access_key = YOUR_SECRET_KEY
     ```

4. Update the configuration:

   Open the `config.ini` file and provide the necessary information:

   - AWS services: Update the ARNs or names of the services you want to monitor.
   - Zabbix configuration: Update the Zabbix server URL, username, and password.
     
## 🛠️ Customization
Feel free to customize and extend this automation tool based on your specific requirements. You can modify the metrics collected, add new services, or integrate with additional AWS services or monitoring tools.

## 📄 License
This project is licensed under the MIT License.

## 🙏 Acknowledgments
[Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)<br>
[Zabbix Documentation](https://www.zabbix.com/documentation/current/en/manual)


