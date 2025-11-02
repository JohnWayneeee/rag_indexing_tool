# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please **do not** open a public issue. Instead, please report it via one of the following methods:

### Email
Send a detailed description to: [ghost.wayneee@gmail.com](mailto:ghost.wayneee@gmail.com)

### GitHub Security Advisories
Use GitHub's [Private Vulnerability Reporting](https://github.com/JohnWayneeee/rag-indexing-tool/security/advisories/new) feature.

## What to Include

When reporting a vulnerability, please include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if you have one)
- Your contact information (for follow-up questions)

## Response Time

- We will acknowledge receipt of your report within **48 hours**
- We will provide an initial assessment within **7 days**
- We will provide regular updates on progress (at least once per week)

## Security Best Practices

When using this project, please follow these security best practices:

1. **Keep dependencies updated**: Regularly update all dependencies to their latest secure versions
2. **Use environment variables**: Never commit secrets, API keys, or credentials to the repository
3. **Validate input**: Always validate and sanitize user input before processing
4. **Use HTTPS**: In production, always use HTTPS for API communication
5. **Review permissions**: Ensure file system permissions are properly configured
6. **Monitor logs**: Regularly review application logs for suspicious activity

## Known Security Considerations

- **Password-protected PDFs**: Currently not supported. Handle sensitive documents with care.
- **File uploads**: Always validate file types and sizes before processing
- **Vector database**: The ChromaDB database may contain sensitive document content. Ensure proper access controls.

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities and help make this project more secure.

