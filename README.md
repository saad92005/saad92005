<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/banner-light.svg">
  <img src="assets/banner-dark.svg" width="100%" alt="Muhammad Saad: AI Engineer and Full-Stack Developer in Lahore. A dithered portrait that morphs into the Python, TypeScript and Flutter logos, next to a system-info readout.">
</picture>

<p align="center">
  <a href="https://www.linkedin.com/in/saadshahidpk"><img src="https://img.shields.io/badge/LinkedIn-0f0f11?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyBmaWxsPSIjZmY3YTQ1IiByb2xlPSJpbWciIHZpZXdCb3g9IjAgMCAyNCAyNCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48dGl0bGU%2BTGlua2VkSW48L3RpdGxlPjxwYXRoIGQ9Ik0yMC40NDcgMjAuNDUyaC0zLjU1NHYtNS41NjljMC0xLjMyOC0uMDI3LTMuMDM3LTEuODUyLTMuMDM3LTEuODUzIDAtMi4xMzYgMS40NDUtMi4xMzYgMi45Mzl2NS42NjdIOS4zNTFWOWgzLjQxNHYxLjU2MWguMDQ2Yy40NzctLjkgMS42MzctMS44NSAzLjM3LTEuODUgMy42MDEgMCA0LjI2NyAyLjM3IDQuMjY3IDUuNDU1djYuMjg2ek01LjMzNyA3LjQzM2MtMS4xNDQgMC0yLjA2My0uOTI2LTIuMDYzLTIuMDY1IDAtMS4xMzguOTItMi4wNjMgMi4wNjMtMi4wNjMgMS4xNCAwIDIuMDY0LjkyNSAyLjA2NCAyLjA2MyAwIDEuMTM5LS45MjUgMi4wNjUtMi4wNjQgMi4wNjV6bTEuNzgyIDEzLjAxOUgzLjU1NVY5aDMuNTY0djExLjQ1MnpNMjIuMjI1IDBIMS43NzFDLjc5MiAwIDAgLjc3NCAwIDEuNzI5djIwLjU0MkMwIDIzLjIyNy43OTIgMjQgMS43NzEgMjRoMjAuNDUxQzIzLjIgMjQgMjQgMjMuMjI3IDI0IDIyLjI3MVYxLjcyOUMyNCAuNzc0IDIzLjIgMCAyMi4yMjIgMGguMDAzeiIvPjwvc3ZnPg%3D%3D" alt="LinkedIn"></a>&nbsp;&nbsp;
  <a href="https://saadshahid-portfolio.vercel.app"><img src="https://img.shields.io/badge/Portfolio-0f0f11?style=for-the-badge&logo=vercel&logoColor=ff7a45" alt="Portfolio"></a>&nbsp;&nbsp;
  <a href="mailto:saad39587@gmail.com"><img src="https://img.shields.io/badge/Email-0f0f11?style=for-the-badge&logo=gmail&logoColor=ff7a45" alt="Email"></a>
</p>

I'm a CS student at UMT in Lahore. Most of what I build is an AI feature wrapped in a lot of ordinary, careful engineering: auth, migrations, tests, CI and the parts that make it work for someone who isn't me. I like problems where the model is the easy bit and the hard part is making it trustworthy.


<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/squiggle-light.svg">
  <img src="assets/squiggle-dark.svg" width="100%" alt="">
</picture>

## Selected work

<a href="https://github.com/saad92005/thinkdesk">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/plate-thinkdesk-light.svg">
    <img src="assets/plate-thinkdesk-dark.svg" width="100%" alt="ThinkDesk: a chat answer drawing facts from two uploaded documents, with page citations">
  </picture>
</a>

A multi-tenant knowledge workspace. Retrieval is hybrid: vector and BM25 search fused with Reciprocal Rank Fusion, then reranked by a cross-encoder. Research mode only calls a finding *verified* when two separate documents back it up. Its agents draft Slack posts, but nothing is sent until a person approves it. 105 tests, including tenant isolation.
**[code](https://github.com/saad92005/thinkdesk) · [live](https://thinkdesk-three.vercel.app)**

<br>

<a href="https://github.com/saad92005/omnira">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/plate-omnira-light.svg">
    <img src="assets/plate-omnira-dark.svg" width="100%" alt="Omnira: the assistant sets a timer through a tool call and replies with a checklist">
  </picture>
</a>

A desktop AI agent that can open apps, create files and set timers, but only through capabilities you've granted. It never sees a tool it isn't allowed to use. It has a provider-agnostic LLM layer, OAuth with PKCE, encrypted tokens, 8 ADRs, 131 tests and a real Windows installer.
**[code](https://github.com/saad92005/omnira)**

<br>

<a href="https://github.com/saad92005/aes-app">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/plate-aes-light.svg">
    <img src="assets/plate-aes-dark.svg" width="100%" alt="AES App dashboard: work orders by region">
  </picture>
</a>

Operations software for an engineering services company. Work orders arrive automatically from Gmail, attendance is GPS-verified, and the payroll engine has a five-stage approval flow. It also does double-entry accounting and inventory for 12 roles, all from one Flutter codebase. The AI assistant goes through a server-side proxy, so no key ships in the app.
**[code](https://github.com/saad92005/aes-app)**

<br>

<a href="https://github.com/saad92005/arabic-dialect-mt-nlp">
  <picture>
    <source media="(prefers-color-scheme: light)" srcset="assets/plate-arabic-light.svg">
    <img src="assets/plate-arabic-dark.svg" width="100%" alt="Held-out chrF and BLEU for four Arabic dialect translation systems">
  </picture>
</a>

Dialect Arabic → English translation on 688 held-out sentences across six dialects. Fine-tuning a pretrained MT model on about 1,100 dialect sentences takes BLEU from 13.0 to 29.0. The from-scratch and AraBERT + GRU baselines stay under 1 BLEU, and the write-up explains why.
**[code + write-up](https://github.com/saad92005/arabic-dialect-mt-nlp)**

<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/squiggle-light.svg">
  <img src="assets/squiggle-dark.svg" width="100%" alt="">
</picture>

## Activity

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://streak-stats.demolab.com/?user=saad92005&amp;hide_border=true&amp;background=f7f4ee&amp;stroke=e0dbd1&amp;ring=d9541e&amp;fire=d9541e&amp;currStreakLabel=d9541e&amp;sideLabels=76716a&amp;currStreakNum=1c1b18&amp;sideNums=1c1b18&amp;dates=76716a&amp;card_width=1180">
  <img src="https://streak-stats.demolab.com/?user=saad92005&amp;hide_border=true&amp;background=0f0f11&amp;stroke=2a292e&amp;ring=ff7a45&amp;fire=ff7a45&amp;currStreakLabel=ff7a45&amp;sideLabels=8b867d&amp;currStreakNum=ece7df&amp;sideNums=ece7df&amp;dates=8b867d&amp;card_width=1180" width="100%" alt="Contribution streak">
</picture>

<picture>
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/saad92005/saad92005/output/github-snake.svg">
  <img src="https://raw.githubusercontent.com/saad92005/saad92005/output/github-snake-dark.svg" width="100%" alt="A snake eating my contribution graph">
</picture>

## What I reach for

**Every day:** TypeScript, Python, Dart. React and Next.js on the web, Flutter on mobile, Tauri for desktop.<br>
**Backends:** FastAPI, Fastify, PostgreSQL with Prisma or SQLAlchemy, and Firebase when the client already lives there.<br>
**AI:** tool-calling agents with a human in the loop, hybrid retrieval with reranking and evals, and PyTorch with Hugging Face Transformers for fine-tuning.<br>
**Shipping:** GitHub Actions, Docker, Vercel, Netlify and Render, plus pytest, Vitest and flutter test.

<br>

<picture>
  <source media="(prefers-color-scheme: light)" srcset="assets/signature-light.svg">
  <img src="assets/signature-dark.svg" width="220" alt="— Saad">
</picture>
