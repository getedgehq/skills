# Third-party notices

## remocn (MIT)

Several kit components are ports of remocn component designs (camera-stage, device-cluster, stat-payoff,
number-wheel, type-into-input, animated-bar-chart, grid-fill, soft-blur-in), rewritten for the kit's scene
clock. Source: https://github.com/kapishdima/remocn

```
MIT License

Copyright (c) 2026 Remocn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## three.js (MIT)

ParticleText and TypeRing use three.js 0.170.0: the HyperFrames template vendors two unmodified files
(below); the Compound template installs it from npm (`npm i three@0.170.0`). Source: https://github.com/mrdoob/three.js

```
The MIT License

Copyright © 2010-2024 three.js authors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
```

## Inter (SIL Open Font License 1.1)

`template/fonts/InterVariable.woff2` is a Latin subset of Inter 4.0 by The Inter Project Authors
(https://github.com/rsms/inter), redistributed under the SIL Open Font License 1.1; the full license text is in
`template/fonts/OFL-Inter.txt`.

## three.js (MIT), vendored copy

`template/vendor/three.module.min.js` and `template/vendor/RoomEnvironment.js` are unmodified files from three.js
0.170.0; the license is in `template/vendor/three.LICENSE`.

## Not shipped, used at run time

- HyperFrames (Apache-2.0, https://github.com/heygen-com/hyperframes) is fetched by `npx hyperframes`.
- Robust Video Matting (GPL-3.0 code, https://github.com/PeterL1n/RobustVideoMatting) is loaded by
  `scripts/matte_rvm.py` through torch.hub on the user's machine; no part of it is included here.
- MediaPipe (Apache-2.0) is a pip dependency of `scripts/faceboxes.py` and `scripts/facezone.py`.
