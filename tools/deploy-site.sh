#!/usr/bin/env bash
# Rebuild the web page and PDF from THE-HUMAN-CONDITION.md and publish to https://bard.salo.cloud
# AWS resources (account 427077559838, us-east-1):
#   S3 bucket        bard.salo.cloud  (private; read via CloudFront OAC EFJEPZBLURKLA)
#   CloudFront       E3QW02YRJ8NFWW   (d1nib1qapsn9w7.cloudfront.net)
#   ACM certificate  arn:aws:acm:us-east-1:427077559838:certificate/e3af54ea-8381-4f52-a6ec-b282517e61fa
#   Route 53         zone Z02371983EMPX6RTY3MNV, A/AAAA alias bard.salo.cloud -> CloudFront
set -euo pipefail
cd "$(dirname "$0")/.."
tools/build-pdf.sh
python3 -I tools/md2web.py THE-HUMAN-CONDITION.md site/index.html
cp THE-HUMAN-CONDITION.pdf site/
aws s3 cp site/index.html s3://bard.salo.cloud/index.html --content-type "text/html; charset=utf-8" --cache-control "public, max-age=300" --only-show-errors
aws s3 cp site/THE-HUMAN-CONDITION.pdf s3://bard.salo.cloud/THE-HUMAN-CONDITION.pdf --content-type application/pdf --cache-control "public, max-age=3600" --only-show-errors
aws cloudfront create-invalidation --distribution-id E3QW02YRJ8NFWW --paths "/*" --query 'Invalidation.Id' --output text
echo "published: https://bard.salo.cloud"
