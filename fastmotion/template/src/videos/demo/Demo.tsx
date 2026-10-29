// A second, original video built only from engine blocks — proves the engine generalises.
// Fictional brand "Morrow" (coffee subscription), agent "Pilot". Edit freely.
import React from 'react';
import {Stage} from '../../engine/ui';
import {Beat, Timeline, totalSec} from '../../engine/timeline';
import {CardFan, Carousel3D, ChatThread, CounterCard, StatBars, TitleBeat} from '../../engine/blocks';

// Each beat: timing + transitions, and the scene to render.
const beats: (Beat & {el: React.ReactNode})[] = [
  {id: 'Intro', from: 0, to: 4, exit: 'blur', el: (
    <Stage>
      <TitleBeat text="Meet **Pilot**, your growth co-pilot" sub="Built for Morrow Coffee" y={420} size={64} />
    </Stage>
  )},
  {id: 'BestAd', from: 4, to: 8.5, exit: 'whipL', el: (
    <Stage>
      <TitleBeat text="Your best ad is still running." y={120} />
      <CounterCard to={212} label="days running" note="It's carrying the account." x={1080} y={330} />
      <CardFan count={1} at={0} cx={640} cy={600} cardW={300} cardH={520} heroCaption="sunday pour-over" />
    </Stage>
  )},
  {id: 'Chat', from: 8.5, to: 15, enter: 'whipL', exit: 'blur', el: (
    <ChatThread agentName="Pilot" userName="Ana" userInitial="A" dust messages={[
      {from: 'agent', text: 'Your morning-ritual ads are fading.', at: 0.4},
      {from: 'agent', text: "Let's test **12** new hooks this week.", at: 1.8},
      {from: 'user', text: 'Do it', at: 3.6},
      {from: 'agent', text: 'Drafting them now.', at: 4.4},
    ]} x={500} y={330} size={40} camera={[{t: 0, z: 1.3, x: -60, y: -60}, {t: 2.5, z: 1.12, x: 0, y: -20}, {t: 6, z: 1, x: 40, y: 30}]} />
  )},
  {id: 'Formats', from: 15, to: 21, exit: 'whipR', el: (
    <Carousel3D
      items={[{label: 'Barista POV', sub: 'for Home Brewers'}, {label: 'Slow pour ASMR', sub: 'for Night Owls'}, {label: 'Desk ritual', sub: 'for Remote Workers', variant: 'product'}, {label: 'Street interview', sub: 'for Commuters'}, {label: 'Origin story', sub: 'for Coffee Nerds', variant: 'scene'}]}
      steps={[{at: 0, focus: 0}, {at: 1.4, focus: 0}, {at: 1.9, focus: 1}, {at: 3.2, focus: 1}, {at: 3.7, focus: 2}, {at: 5, focus: 2}, {at: 5.5, focus: 3}]}
    />
  )},
  {id: 'Results', from: 21, to: 27, enter: 'whipR', el: (
    <Stage>
      <TitleBeat text="Week one, **done**." sub="Hooks that felt like a friend's tip." y={150} />
      <StatBars x={470} y={300} height={560} metrics={[
        {name: 'Thumbstop', base: '22%', val: '38%', bh: 0.4, vh: 0.72},
        {name: 'CTR', base: '0.9%', val: '1.7%', bh: 0.3, vh: 0.62},
        {name: 'CPA', base: '$41', val: '$24', bh: 0.78, vh: 0.44, note: '41% lower'},
        {name: 'ROAS', base: '1.8x', val: '3.9x', bh: 0.3, vh: 0.8},
      ]} />
    </Stage>
  )},
];

export const DEMO_SEC = totalSec(beats);

const scenes = Object.fromEntries(beats.map((b) => [b.id, () => <>{b.el}</>]));

export const Demo: React.FC = () => <Timeline beats={beats} scenes={scenes} />;
