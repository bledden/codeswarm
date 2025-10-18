#!/bin/bash
# Generate WorkOS cookie password

echo "Generating WorkOS cookie password..."
echo ""

PASSWORD=$(openssl rand -base64 24)

echo "Generated password:"
echo "$PASSWORD"
echo ""
echo "Add this to your .env file:"
echo "WORKOS_COOKIE_PASSWORD=$PASSWORD"
echo ""
