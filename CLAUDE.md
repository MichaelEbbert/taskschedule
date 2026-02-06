# Deployment Info

## AWS Server
- **Subdomain:** https://taskschedule.mebbert.com
- **Internal Port:** 5000
- **Status:** Active

## SSH Access
```bash
ssh -i "C:\claude_projects\taskschedule\taskschedule-key.pem" ec2-user@100.50.222.238
```

## Server Documentation
Full deployment docs on server: `/home/ec2-user/taskschedule/AWS_DEPLOYMENT.md`

## Service Management
```bash
sudo systemctl status taskschedule
sudo systemctl restart taskschedule
sudo journalctl -u taskschedule -f
```

## Deploy Updates

Use the centralized deployment scripts in `C:\claude_projects\deployment-manager\`:

```bash
cd C:\claude_projects\deployment-manager
python deploy.py taskschedule       # Full deploy (sync + deps + restart)
python status.py taskschedule       # Health check
python restart.py taskschedule      # Quick restart
python logs.py taskschedule -f      # Follow logs
```

## Nginx Authentication
See `C:\claude_projects\recipeshoppinglist\CLAUDE.md` for instructions on nginx-level auth to protect all deployed apps.
