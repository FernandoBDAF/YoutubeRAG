# Quick Start - LLM Development Methodology

**Time to First PLAN**: 5 minutes  
**Difficulty**: Beginner-friendly

---

## 🎯 Goal

Create your first PLAN and start working with the structured LLM development methodology.

---

## ⚡ 3-Step Quick Start

### Step 1: Copy Prompt (30 seconds)

Open `LLM/templates/PROMPTS.md` and copy the "Create New PLAN" prompt.

Replace placeholders:

- `[FEATURE_NAME]` → Your feature name (kebab-case, e.g., `USER-AUTHENTICATION`)
- `[GOAL]` → One sentence describing what to achieve
- `[PRIORITY]` → Critical / High / Medium / Low
- `[X-Y hours]` → Time estimate

### Step 2: Execute Prompt (2 minutes)

Give the completed prompt to your LLM:

```
Create a new PLAN for USER-AUTHENTICATION following @LLM/protocols/IMPLEMENTATION_START_POINT.md

Context:
- Goal: Implement secure user authentication with JWT tokens
- Priority: High
- Estimated Effort: 12-16 hours

GrammaPlan Decision:
- Will PLAN exceed 800 lines? No
- Effort > 80 hours? No
- Spans 3+ domains? No
→ Decision: Single PLAN

Create PLAN_USER-AUTHENTICATION.md using @LLM/templates/PLAN-TEMPLATE.md
```

LLM will create your PLAN file!

### Step 3: Start Executing (2 minutes)

Once PLAN is created:

1. Select first achievement to tackle
2. Create SUBPLAN using prompt from PROMPTS.md:

   ```
   Create SUBPLAN for Achievement 1.1 in @PLAN_USER-AUTHENTICATION.md
   ```

3. LLM creates SUBPLAN and starts execution!

---

## 📚 What Just Happened?

You used the methodology to:

- ✅ Create a PLAN (defines WHAT to achieve)
- ✅ Create a SUBPLAN (defines HOW to achieve it)
- ✅ Start execution (LLM is now working!)

---

## 🎓 Learn More

**Next Steps**:

1. **Understand Workflows**: Read `LLM/protocols/IMPLEMENTATION_START_POINT.md` (20 min)
2. **See All Prompts**: Browse `LLM/templates/PROMPTS.md` (10 min)
3. **Learn Patterns**: Read a real PLAN in root directory (10 min)

**Advanced Topics**:

- **Multiple PLANs**: `LLM/guides/MULTIPLE-PLANS-PROTOCOL.md`
- **Large Initiatives**: `LLM/guides/GRAMMAPLAN-GUIDE.md`
- **Team Collaboration**: `LLM/guides/MULTI-LLM-PROTOCOL.md`
- **Quality Checkpoints**: `LLM/guides/IMPLEMENTATION_MID_PLAN_REVIEW.md`

---

## 💡 Pro Tips

1. **Always use prompts**: Faster and more consistent than manual construction
2. **Start small**: First PLAN should be simple (learn the methodology)
3. **Follow protocols**: START_POINT → Work → END_POINT
4. **Test-first**: Write tests before implementation (prevents issues)
5. **Capture learnings**: Document what you learn in EXECUTION_TASKs

---

## 🆘 Troubleshooting

**LLM is confused?**
→ Check you're using @ syntax to reference files: `@LLM/templates/PLAN-TEMPLATE.md`

**Don't know what to do?**
→ Look in PROMPTS.md - there's a prompt for everything!

**Plan getting too large?**
→ Read GRAMMAPLAN-GUIDE.md - might need GrammaPlan

**Working with others?**
→ Read MULTI-LLM-PROTOCOL.md for coordination

---

**You're Ready!** Start creating PLANs and building great software! 🚀

**Entry Point**: `../LLM-METHODOLOGY.md` (comprehensive overview)  
**Prompts**: `templates/PROMPTS.md` (your best friend)
