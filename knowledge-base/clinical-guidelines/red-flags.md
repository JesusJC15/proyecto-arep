# Red Flags for Escalation

## Purpose

This note lists generic red-flag categories to drive the escalation branch of the MVP. It is intentionally conservative and should not be interpreted as medical advice.

## Red-flag categories

- Breathing difficulty or rapid worsening reported by the user.
- Altered consciousness or severe confusion.
- Intense pain with functional impairment.
- Persistent symptoms that do not improve with time or basic care.
- Incomplete information combined with high uncertainty in the model output.

## Expected system action

- Set severity to `high` when one or more red-flag categories are present.
- Force creation of an escalation case for professional review.
- Preserve the source note as part of the recommendation trace.
