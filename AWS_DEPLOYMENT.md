# AWS Deployment Information

## Access Your App

**Domain Name:** http://taskschedule.mebbert.com:5000
**Elastic IP (Static):** http://100.50.222.238:5000

**Login Credentials:**
- Username: De / Password: percy
- Username: Michael / Password: percy
- Plus 13 additional users (see add_new_users.py) with password: claude101

## AWS Resources Created

### EC2 Instance
- Instance ID: i-05582111840d4a971
- Instance Type: t2.micro (free tier eligible)
- Elastic IP (Static): 100.50.222.238
- Allocation ID: eipalloc-08457e0840e101474
- Region: us-east-1 (Virginia)

### Security Group
- Group ID: sg-08148e411586cd1fe
- Name: taskschedule-sg
- Inbound Rules:
  - Port 22 (SSH) - from anywhere
  - Port 80 (HTTP) - from anywhere
  - Port 5000 (Flask) - from anywhere

### SSH Key
- Key Name: taskschedule-key
- Private Key File: `taskschedule-key.pem` (in project directory)
- **IMPORTANT:** Keep this file secure! Anyone with this key can access your server.

### Route 53 DNS
- Hosted Zone: mebbert.com (Z040520630S50ZVHYL1YA)
- DNS Record: taskschedule.mebbert.com → 100.50.222.238 (A record)
- TTL: 300 seconds (5 minutes)

### Elastic IP
- Allocation ID: eipalloc-08457e0840e101474
- Static IP: 100.50.222.238
- **Note:** This IP is permanent and will not change even if the instance is stopped/restarted

## Connecting via SSH

```bash
ssh -i taskschedule-key.pem ec2-user@taskschedule.mebbert.com
# Or using IP:
ssh -i taskschedule-key.pem ec2-user@100.50.222.238
```

## App Management

The app runs as a systemd service and starts automatically on boot.

**Check status:**
```bash
sudo systemctl status taskschedule
```

**View logs:**
```bash
sudo journalctl -u taskschedule -f
```

**Restart app:**
```bash
sudo systemctl restart taskschedule
```

**Stop app:**
```bash
sudo systemctl stop taskschedule
```

## Updating the App

To deploy updates:

1. SSH into the instance
2. Pull latest changes:
   ```bash
   cd /home/ec2-user/taskschedule
   git pull origin main
   ```
3. Restart the service:
   ```bash
   sudo systemctl restart taskschedule
   ```

## AWS IAM User

- Username: claude-deploy
- Permissions: EC2FullAccess, VPCFullAccess, ElasticLoadBalancingFullAccess
- Access Key ID: AKIA3PPSZFE3HK3OJ7HZ (stored in ~/.aws/credentials)

## Costs

- t2.micro instances are free tier eligible (750 hours/month free for 12 months)
- After free tier: ~$0.0116/hour (~$8.50/month)
- Data transfer: First 100 GB/month free, then $0.09/GB

## Terminating Resources (to stop costs)

To completely remove everything:

```bash
# Terminate the instance
python -m awscli ec2 terminate-instances --instance-ids i-05582111840d4a971

# Delete the security group (after instance is terminated)
python -m awscli ec2 delete-security-group --group-id sg-08148e411586cd1fe

# Delete the key pair
python -m awscli ec2 delete-key-pair --key-name taskschedule-key
```

## Security Notes

- The app is accessible from anywhere on the internet
- Password authentication is case-insensitive
- No HTTPS/SSL configured (traffic is unencrypted)
- For production use, consider:
  - Setting up HTTPS with Let's Encrypt
  - Using a proper password hashing library
  - Restricting security group to specific IP addresses
  - Setting up automated backups of the database
