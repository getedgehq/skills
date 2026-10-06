// interview-reel-template: an interview short from data. Point these three imports at your reel's folder.
// examples/starter is a complete small reel to copy.
import { Reel } from "./src/engine/Reel";
import reel from "./examples/starter/reel.json";
import beats from "./examples/starter/beats.json";
import captions from "./examples/starter/captions.json";

export default function Project() {
  return <Reel reel={reel as any} beats={beats as any} captions={captions as any} />;
}
