# aws-sagemaker-delete-domains
Code to delete all domains inside Amazon SageMaker



# Usage

1. Configure aws command line in your environment (https://aws.amazon.com/cli/)
2. Get programmatic access to AWS, user needs permissions to list and delete resources inside Amazon SageMaker
3. Fill out the `REGION` and `DOMAINS_NOT_DELETE` variables
4. Run `delete_domains.py`. This will delete all the user profiles, apps, spaces, and domains inside Amazon SageMaker in the specified region except for the domains specified in `DOMAINS_NOT_DELETE`.
