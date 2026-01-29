# AWS Infrastructure for mebbert.com Domain

**READ THIS FIRST:** This document describes the existing AWS infrastructure for the mebbert.com domain. Use this information to safely add new subdomains WITHOUT disrupting existing services.

---

## Current Infrastructure Overview

### Domain & DNS
- **Primary Domain:** mebbert.com
- **Route 53 Hosted Zone ID:** Z040520630S50ZVHYL1YA
- **AWS Region:** us-east-1 (Virginia)
- **IAM User:** claude-deploy

### Existing Subdomain in Use
⚠️ **CRITICAL - DO NOT MODIFY OR DELETE**

**taskschedule.mebbert.com:**
- **Type:** A Record
- **IP Address:** 100.50.222.238 (Elastic IP)
- **TTL:** 300 seconds
- **Purpose:** Task scheduling web application
- **Status:** ACTIVE - In production use
- **EC2 Instance ID:** i-05582111840d4a971
- **Elastic IP Allocation ID:** eipalloc-08457e0840e101474

---

## AWS Resources Currently In Use

### Route 53
- **Hosted Zone:** mebbert.com (Z040520630S50ZVHYL1YA)
- **Nameservers:** (Managed by Route 53, DO NOT CHANGE)
- **Existing DNS Records:**
  - taskschedule.mebbert.com → 100.50.222.238 (A record, TTL 300)

### EC2 Instances
- **Instance ID:** i-05582111840d4a971
- **Type:** t2.micro (free tier eligible)
- **Status:** RUNNING
- **Purpose:** taskschedule application
- **Elastic IP:** 100.50.222.238 (MUST NOT BE RELEASED)
- **Security Group ID:** sg-08148e411586cd1fe
- **Region:** us-east-1

### Elastic IPs
- **Allocation ID:** eipalloc-08457e0840e101474
- **Address:** 100.50.222.238
- **Associated With:** i-05582111840d4a971
- ⚠️ **DO NOT RELEASE THIS IP** - It will break taskschedule.mebbert.com

### Security Groups
- **Group ID:** sg-08148e411586cd1fe
- **Name:** taskschedule-sg
- **VPC:** Default VPC in us-east-1
- **Inbound Rules:**
  - Port 22 (SSH) from 0.0.0.0/0
  - Port 80 (HTTP) from 0.0.0.0/0
  - Port 5000 (Flask) from 0.0.0.0/0

### IAM Users
- **Username:** claude-deploy
- **Access Key ID:** AKIA3PPSZFE3HK3OJ7HZ
- **Permissions:**
  - EC2FullAccess
  - VPCFullAccess
  - ElasticLoadBalancingFullAccess
  - Route53FullAccess

---

## How to Safely Add a New Subdomain

### Step 1: Decide on Subdomain Name
Choose a subdomain that does NOT conflict with existing ones:
- ❌ **DO NOT USE:** taskschedule.mebbert.com (already exists)
- ✅ **Available:** [anything-else].mebbert.com

### Step 2: Create Your Infrastructure
Create your EC2 instance, service, or resource that will host the new subdomain.

**BE SURE TO:**
- Create resources in the **us-east-1** region (for consistency)
- Use a **NEW security group** (don't modify sg-08148e411586cd1fe)
- If you need a static IP, allocate a **NEW Elastic IP** (don't touch eipalloc-08457e0840e101474)
- Use a **NEW EC2 instance** (don't modify i-05582111840d4a971)

**BE SURE NOT TO:**
- ❌ Terminate, stop, or modify instance i-05582111840d4a971
- ❌ Release or disassociate Elastic IP 100.50.222.238
- ❌ Modify security group sg-08148e411586cd1fe
- ❌ Delete or modify the taskschedule.mebbert.com DNS record
- ❌ Delete or modify the Route 53 hosted zone Z040520630S50ZVHYL1YA

### Step 3: Add DNS Record in Route 53

**Using AWS CLI:**
```bash
# Example: Creating an A record for newapp.mebbert.com pointing to 203.0.113.50
aws route53 change-resource-record-sets \
  --hosted-zone-id Z040520630S50ZVHYL1YA \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "newapp.mebbert.com",
        "Type": "A",
        "TTL": 300,
        "ResourceRecords": [{"Value": "203.0.113.50"}]
      }
    }]
  }'
```

**BE SURE TO:**
- Use Action: "**CREATE**" (not UPSERT or DELETE)
- Use the correct hosted zone ID: **Z040520630S50ZVHYL1YA**
- Set a reasonable TTL (300-3600 seconds recommended)
- Verify the IP address is correct before creating

**BE SURE NOT TO:**
- ❌ Use Action: "DELETE" (you could accidentally delete existing records)
- ❌ Use the wrong hosted zone ID
- ❌ Create a record with the same name as an existing subdomain
- ❌ Set TTL too high (>3600) during initial testing

### Step 4: Verify the DNS Record

**After creation, verify:**
```bash
# List all DNS records to confirm
aws route53 list-resource-record-sets \
  --hosted-zone-id Z040520630S50ZVHYL1YA

# Test DNS resolution
nslookup newapp.mebbert.com
dig newapp.mebbert.com
```

**BE SURE TO:**
- Confirm your new record appears in the list
- Confirm the existing taskschedule.mebbert.com record is unchanged
- Wait 5-10 minutes for DNS propagation
- Test from multiple locations/networks if possible

---

## Testing Checklist

Before considering your new subdomain complete:

- [ ] New subdomain resolves to the correct IP address
- [ ] Existing subdomain (taskschedule.mebbert.com) still works: http://taskschedule.mebbert.com:5000
- [ ] Can access the service at the new subdomain
- [ ] DNS propagation complete (test with multiple DNS servers)
- [ ] SSL/HTTPS configured if needed
- [ ] Security groups properly configured for your new service
- [ ] Documented the new subdomain in your project's infrastructure docs

---

## Important Warnings

### ⚠️ CRITICAL - DO NOT DO THESE THINGS:
1. **DO NOT** delete the Route 53 hosted zone Z040520630S50ZVHYL1YA
2. **DO NOT** modify or delete the taskschedule.mebbert.com A record
3. **DO NOT** release Elastic IP 100.50.222.238
4. **DO NOT** stop, terminate, or modify EC2 instance i-05582111840d4a971
5. **DO NOT** modify security group sg-08148e411586cd1fe
6. **DO NOT** change the nameservers for mebbert.com
7. **DO NOT** create DNS records with wildcards that could conflict
8. **DO NOT** set very low TTLs (<60 seconds) in production

### 💡 Best Practices:
- Always use "CREATE" action when adding new DNS records
- Test DNS changes in a staging environment first if possible
- Keep TTL at 300 seconds during initial testing, increase after stable
- Document all new subdomains and their purpose
- Use infrastructure-as-code (save your AWS CLI commands in scripts)
- Tag your AWS resources appropriately for organization
- Monitor costs - new resources will incur charges
- Set up CloudWatch alarms for your new resources

---

## Troubleshooting

### "DNS record already exists"
- Check if the subdomain name conflicts with existing records
- List all records: `aws route53 list-resource-record-sets --hosted-zone-id Z040520630S50ZVHYL1YA`
- Choose a different subdomain name

### "New subdomain not resolving"
- Wait 5-10 minutes for DNS propagation (TTL is 300 seconds)
- Check if the record was created: `aws route53 list-resource-record-sets --hosted-zone-id Z040520630S50ZVHYL1YA`
- Verify the IP address is correct and reachable
- Test with: `dig @8.8.8.8 newapp.mebbert.com`

### "Permission denied when creating DNS record"
- Verify your IAM user has Route53FullAccess permission
- Check that you're using the correct AWS credentials
- Verify the hosted zone ID is correct

---

## Cost Implications

Adding a new subdomain DNS record has **minimal cost** (typically <$0.50/month for Route 53).

**However, additional costs may apply for:**
- New EC2 instances (if you create one)
- New Elastic IPs (if you allocate one)
- Data transfer
- Load balancers
- Other AWS services you add

**Current costs for taskschedule setup:**
- Route 53 hosted zone: ~$0.50/month
- DNS queries: ~$0.40 per million queries
- EC2 t2.micro: Free tier eligible (750 hours/month for 12 months), then ~$8.50/month
- Elastic IP: Free when associated with running instance, $0.005/hour when not associated
- Data transfer: First 100 GB/month free, then $0.09/GB

---

## Contact & Support

**Project:** Task Schedule Application
**Repository:** https://github.com/MichaelEbbert/taskschedule
**Deployment Docs:** See AWS_DEPLOYMENT.md in the taskschedule project

**If you break something:**
1. Do NOT panic-delete resources
2. Check AWS CloudTrail to see what changed
3. Restore from the last known good configuration
4. If taskschedule.mebbert.com is down, check:
   - EC2 instance i-05582111840d4a971 is running
   - Elastic IP 100.50.222.238 is still associated
   - DNS record still points to 100.50.222.238
   - Security group sg-08148e411586cd1fe allows traffic on port 5000

---

## Quick Reference Commands

**List all DNS records:**
```bash
aws route53 list-resource-record-sets --hosted-zone-id Z040520630S50ZVHYL1YA
```

**Check EC2 instance status:**
```bash
aws ec2 describe-instances --instance-ids i-05582111840d4a971 --region us-east-1
```

**Check Elastic IP status:**
```bash
aws ec2 describe-addresses --allocation-ids eipalloc-08457e0840e101474 --region us-east-1
```

**Test DNS resolution:**
```bash
nslookup taskschedule.mebbert.com
dig taskschedule.mebbert.com
```

---

**Last Updated:** 2026-01-28
**Infrastructure Status:** STABLE - taskschedule.mebbert.com in production use
