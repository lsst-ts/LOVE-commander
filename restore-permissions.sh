#!/bin/bash

# Restoring ownership
chown -R 1000:1000 .

# Restoring 755 permission for folders
find ./ -type d -exec chmod 0755 {} \;

# Restoring 644 permission for files
find ./ -type f -exec chmod 0644 {} \;

# Restoring +x permission for sh files
find ./ -name "*.sh" -exec chmod +x {} \;

# Restoring pre-commit +x permission
chmod +x .git/hooks/pre-commit