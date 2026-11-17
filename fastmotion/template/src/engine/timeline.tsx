import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {s} from './anim';
import {C} from './theme';
import {Transition, Tx} from './transitions';

// Every scene component receives its own mounted duration (sec) so it can time its exit.
export type SceneProps = {dur: number};

// One beat on the timeline. Times are absolute seconds in the video.
//   enter/exit: engine transition (omit to let the scene handle its own edges)
//   shift:      advances the scene's internal clock (+0.3 = animation plays 0.3s earlier)
export type Beat = {id: string; from: number; to: number; enter?: Tx; exit?: Tx; shift?: number};

// Neighbouring beats overlap by this much so exits/entrances can crossfade.
export const OVERLAP = 0.3;

export const totalSec = (beats: Beat[]) => Math.max(...beats.map((b) => b.to));

// Plays a list of beats, looking each scene up by id in `scenes`.
export const Timeline: React.FC<{beats: Beat[]; scenes: Record<string, React.FC<SceneProps>>; overlap?: number; background?: string}> = ({beats, scenes, overlap = OVERLAP, background = C.bg}) => (
  <AbsoluteFill style={{background}}>
    {beats.map((b, i) => {
      const Comp = scenes[b.id];
      const last = i === beats.length - 1;
      const dur = b.to - b.from + (last ? 0 : overlap);
      if (!Comp) return null;
      return (
        <Sequence key={b.id + i} name={b.id} from={s(b.from)} durationInFrames={s(dur)}>
          <Transition dur={dur} enter={b.enter} exit={b.exit}>
            {b.shift ? (
              <Sequence from={-s(b.shift)} layout="none">
                <Comp dur={dur} />
              </Sequence>
            ) : (
              <Comp dur={dur} />
            )}
          </Transition>
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
