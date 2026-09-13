---
type: Runbook
title: Emergency Cloud Handoff
description: How to move active local agent sessions to the cloud when you need to shut down suddenly, without losing in-progress work.
tags: [operations, agents, continuity]
---

# Emergency Cloud Handoff

Use this when you must stop working locally right now (laptop closing, network
loss, urgent context switch) but one or more agent sessions are still busy on a
PR and you want the work to keep going unattended.

Cloud sessions only see what's on the remote branch. Anything only in the
local worktree is lost the moment the local session stops. The push step
below is therefore the time-critical part -- do it first, before anything
else.

## Steps

1. **Force a push of in-flight work.**
   For each busy session, send an immediate, explicit instruction such as:
   > "Stop and commit/push the current state right now, even if incomplete.
   > Report the branch name and PR number once pushed."

   Wait for confirmation that the push succeeded before continuing.

2. **Open a cloud session per affected PR.**
   Use the PR-aware handoff (e.g. `open_pr_session`) against each PR number
   so the cloud agent starts from the pushed branch, not a stale checkout.

3. **Give the cloud session a resume prompt.**
   Summarize what's done and what's left, for example:
   > "Continue this PR from its current pushed state: resolve any remaining
   > review threads, finish the incomplete change, validate, and merge when
   > green. Report back if blocked."

4. **Confirm the cloud session is running**, then stop or archive the local
   session and shut down.

5. **Check back asynchronously.** The cloud session keeps working
   independently of your machine; you'll be notified on completion or if it
   needs input.

## Notes

* This is an on-demand procedure, not a default. Prefer local sessions for
  normal work; reach for cloud handoff only when you must step away.
* If a session can't push in time (e.g. it's mid destructive operation), the
  safer choice is to let it finish locally rather than force a handoff.
* One cloud session per PR/branch keeps scope focused and avoids one agent
  juggling unrelated work.
