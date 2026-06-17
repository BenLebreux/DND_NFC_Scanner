# 🧠 D&D Statblock Scanner: Source of Truth

**Project Name:** D&D Statblock Scanner (formerly *NFC Campaign Tool* & *NFC Miniature Scanning Tower*)  
**Primary Goal:** A highly reliable, visually pleasing ("vibes"), split-system physical prop for a D&D campaign. When an NFC-equipped miniature is scanned, the system queries a local Obsidian markdown database and seamlessly displays the corresponding monster statblock on a dedicated screen.

---

## 🚨 Mandatory AI Directives
*Any AI agent interacting with this project MUST adhere strictly to these rules:*

1. **Continuous Documentation:** After *every* conversation, decision, prompt execution, or code modification, you MUST update all relevant documentation files in this `docs/` directory proactively. Do not wait for the user to ask.
2. **Commit Often:** After completing a work session, you MUST commit the codebase to the local Git repository with a descriptive message to maintain the 2-iteration Rollback safety net.
3. **No Silos:**
   - Design choices go to the [Decision Log](Decision_Log.md).
   - Pending items go to the [To-Do List](To_Do.md).
   - Finished tasks go to the [Worklog](Worklog.md).
   - Wiring changes go to the [Hardware Ledger](Hardware_Ledger.md).

---

## 🏗️ Architecture: The Split System (v2)

To avoid hardware pin conflicts and memory issues on a single board, the project uses a two-part split architecture:

| Component | Hardware | Role |
| :--- | :--- | :--- |
| **The Brain** | **Raspberry Pi 3B+** | Handles the heavy lifting: I2C NFC scanning, Obsidian database queries, parsing statblocks, and controlling PWM LED rings. |
| **The Face** | **ESP32 CYD (Cheap Yellow Display)** | Acts as a "dumb terminal" receiving parsed text from the Pi over USB Serial and scrolling it smoothly using LVGL and a rotary encoder. |

---

## 📚 Documentation Index
- **[Hardware Ledger](Hardware_Ledger.md):** Exact wiring, pinouts, component lists, and power delivery specs.
- **[Software Version Control](Software_Version_Control.md):** Software architecture breakdown and Git Rollback guide.
- **[Decision Log](Decision_Log.md):** Chronological log explaining *why* major project decisions were made.
- **[Prototypes & Iterations](Prototypes_and_Iterations.md):** The graveyard of past attempts (Flipper Zero, Standalone CYD).
- **[To-Do List](To_Do.md):** Actionable checklist of bugs, features, and next steps.
- **[Worklog](Worklog.md):** Historical log of completed tasks and squashed bugs.

*(Note: Move older log entries to the `Archive/` folder when files become too long to read comfortably.)*
