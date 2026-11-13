import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setConcurrency(Number(process.env.REMOTION_CONCURRENCY) || null);
// Optional: point at a specific Chrome/Chromium (CI, sandboxes). Unset = Remotion downloads its own.
if (process.env.REMOTION_BROWSER) Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
