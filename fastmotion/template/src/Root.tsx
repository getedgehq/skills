import React from 'react';
import {Composition} from 'remotion';
import {FPS} from './engine/constants';
import {Demo, DEMO_SEC} from './videos/demo/Demo';

// Register one <Composition> per video in src/videos/.
export const Root: React.FC = () => (
  <>
    <Composition id="Demo" component={Demo} durationInFrames={Math.round(DEMO_SEC * FPS)} fps={FPS} width={1920} height={1080} />
  </>
);
