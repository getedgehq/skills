# Worked example: Federico De Ponte, @fedepontehq

The run this skill was built from. It shows the shape of a good answer: every step with its numbers, its n and its strength. These are one account's numbers over a month. They are not targets or benchmarks for anyone else.

## The account

- His old X account was blocked in August 2026. He started again from zero.
- File: all 267 posts on the new account, 2 Sep to 9 Oct 2026 (Pacific time), pulled with the X API v2 on 9 Oct 2026. 531 followers that day.
- 90 original posts, 13 quote posts, 164 replies, no reposts. Metric: impressions. Timezone: America/Los_Angeles.
- Original and quote posts (n = 103): median 124 impressions. Replies (n = 164): median 26.
- Command: `python3 scripts/x_growth_report.py posts.json --tz America/Los_Angeles --topic "Claude/Opus=claude|opus"`

## The 10 steps

1. **Quote more posts.** Quote posts: median 263 impressions (n = 13) vs original posts 114.5 (n = 90), 2.3x. Result, but the smallest group that still counts.
2. **Name the tool your audience already follows.** Posts that mention Claude or Opus: 238 (n = 17) vs 112 (n = 86), 2.1x. Result. Some of these are also quote posts, so steps 1 and 2 partly count the same posts.
3. **Keep links out of the post. Put them in a reply.** With an external link: 108 (n = 18) vs without: 144 (n = 85). Result. A stop-doing step.
4. **Write the whole thought.** Over 280 characters: 161.5 (n = 26) vs under 140: 101 (n = 33); 140 to 280: 116 (n = 44). Result.
5. **Post between noon and 5pm Pacific. Not overnight.** 12:00-16:59: 175 (n = 29) vs 00:00-05:59: 77 (n = 11). Mornings 120.5 (n = 40), evenings 114 (n = 23). Result.
6. **Don't wait for an image or video.** With media: 124 (n = 75) vs text only: 121.5 (n = 28). No difference. Result: something to stop worrying about.
7. **Reply a lot.** 164 of 267 posts were replies, median 26 impressions each. Small one by one, and most of the work.
8. **Sprint when you start.** 146 posts in 8 days, 16 to 23 Sep (Pacific dates). Followers went from 67 (his count at the start) to over 200 (his post on 22 Sep: "just passed 200 followers"). One stretch on one account: a story, not a result. The file holds no follower history.
9. **Ask people what they are building.** His top post, "I'm a solo founder building an AI startup from San Francisco! ... Let's connect! Super curious what you're building", got 9,836 impressions and 312 replies. An earlier quote post in the same spirit ("I'm 25. Solo founder based in SF. Looking to connect with more builders") got 2,958 and 92 replies. Single posts.
10. **Show the experiment, then tell the true story.** "we gave Claude $1 and 2,000+ tools" (a video with a concrete result) got 7,456 impressions. The launch announcement, also a video, got 1,333. The post about the blocked account ("my x account got blocked last month. started again from zero two weeks ago. just passed 200 followers") got 1,779 and 41 replies. Single posts, and they vary: the same blocked-account story posted three days earlier at 18:30 got 41 impressions.

## What the file could not tell him

- Where the views came from, or which posts brought followers.
- Follower history: the 67 and the 200 come from him, not from the file.
- Long posts were cut at about 280 characters in this API pull (no long-post text was requested). They still count as over 280.
