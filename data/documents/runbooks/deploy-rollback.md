# Deploy Rollback Runbook

This runbook describes how to roll back a bad deployment of any Aegis
service.

## When To Use This

Use this runbook when a deploy has caused elevated error rates, failed
health checks, or a regression reported by users within the last hour.

## Steps

1. Identify the last known-good release tag in the deploy history.
2. Confirm the rollback target with the on-call lead before proceeding.
3. Run the rollback command for the affected service:

   ```
   deploy rollback --service <service-name> --to <release-tag>
   ```

4. Watch the service's health dashboard for five minutes to confirm error
   rates have returned to baseline.
5. Post a summary of the rollback in the incidents channel, including the
   bad release tag and the reason for rollback.

## After Rollback

Open a follow-up ticket to investigate the root cause of the bad deploy
before it is retried. Do not re-deploy the same release without a fix.
