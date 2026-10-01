---
name: remotion-lambda-render
description: Deploy a version matched Remotion Lambda function and site, render a composition, and retrieve the output with documented CLI traps.
---

# Remotion Lambda render

Use this for a Remotion project that should render through AWS Lambda. Rendering is CPU and headless browser work; Lambda can fan frames out across workers. Confirm the project version, composition, AWS region, concurrency quota, and expected cost before deployment or render.

## Configuration

Use your own AWS credentials and region from the normal AWS credential chain. Choose a site name, function memory, timeout, frames per Lambda, output bucket, and cost limit for your account. The examples below use placeholders and do not select an account or spend budget for you.

## Procedure

```bash
cd <project>
npm install "@remotion/lambda@$(node -p "require('remotion/package.json').version")"
./node_modules/.bin/remotion lambda functions deploy --timeout=600 --memory=3008 --disk=10240
./node_modules/.bin/remotion lambda sites create src/index.ts --site-name=<site-name> --public-dir=<slim-public-dir>
./node_modules/.bin/remotion lambda render <serve-url> <composition-id> --function-name=<version-matched-function> --gl=swangle --frames-per-lambda=300 --codec=h264 --image-format=jpeg
```

Match `@remotion/lambda` to the project's `remotion` version; use the function name printed by the deployment. Re-upload the site after any code or asset change. Stage only the assets the composition needs when the project public directory is large.

The source workflow observed that local `swiftshader` settings crashed Lambda Chromium; `--gl=swangle` resolved it. Its CLI's `--download` did not fetch the output. Read the render result for the output S3 location and fetch it with `aws s3 cp <output-s3-uri> <local-output>`. Confirm the downloaded file exists and plays. CLI behavior can vary by version, so prefer the current render result over a hardcoded bucket or key pattern.

Keep the number of simultaneous renders within the account's Lambda concurrency quota. On `TooManyRequestsException` or `Rate Exceeded`, wait with backoff and retry the same render request; if throttling persists, use a local render or request a quota increase. A 600 second function helps with heavy compositions that exceed shorter timeouts.

## Example

A 45 second product demo uses a large public asset folder. Copy only its referenced images and audio into a slim staging directory, deploy a function matching the project's Remotion version, upload the updated site, render one composition with `--gl=swangle`, fetch the output URI from the render result, and check the local MP4 before delivery.
