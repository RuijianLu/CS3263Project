

# 

# 

# 

# 

# 

# CS3263 Project Proposal

## Lu Ruijian, A0287930U, e1297772@u.nus.edu

## Brandon Chong Wee Kiat, A0269806N, e1114718@u.nus.edu

##  Jonathan Graziano Yang, A0300413A, e1354779@u.nus.edu

## 

## 

## 

**Problem Description**

Planning a university degree requires students to satisfy many interacting requirements, such as prerequisites, course availability, graduation requirements, workload limits, and personal preferences.

Degree planning can be formulated as a constraint satisfaction and planning problem. Additionally, frontier AI models can interpret these requirements and propose study plans directly. Therefore, we propose to develop and evaluate an **AI degree-planning assistant** based on a simplified model of university course planning. The main research question is:

When does a frontier AI model reason reliably about degree-planning constraints, and when is it more effective to translate the problem into a formal constraint representation and use a solver?

**Sub-problems**

The problem can be broken down into sub-problems of increasing complexity:

* Selecting courses that satisfy degree requirements  
* Respecting prerequisite relationships  
* Distributing courses across semesters subject to workload limits  
* Incorporating preferences (e.g. preferred semesters, professors)

**Approach and Evaluation**

We will compare two approaches using the same natural-language degree-planning requests: One is a frontier AI model proposes a study plan directly. The other is the model translates the request into a formal constraint specification, which a symbolic solver uses to produce a plan. 

Our evaluation will focus on whether a plan satisfies all required constraints, whether each approach correctly identifies impossible cases, and how performance changes as requirements interact more closely. We will also examine errors in the model’s translation to distinguish misunderstanding of a request from difficulty in solving it. 

**Project milestones**

1. **Collect initial dataset.** Degree requirements, module data from NUSMods, etc…  
2. **Build benchmark.** Construct degree-planning scenarios with valid reference plans.  
3. **Solver-assisted pipeline.** Implement a formal pipeline which uses a solver.  
4. **Evaluation.** Evaluate both approaches against the benchmark.

**Risk Assessment**

The main risk is that realistic degree requirements contain exceptions and ambiguous rules that are difficult to encode, which we will mitigate by using a simplified model and stating our assumptions explicitly. API costs are capped at \$100, so we will limit the number of test cases and may use SoC-hosted open-weight models for larger runs. Finally, the model may fail to translate complex requests into valid specifications, but we will treat such failures as findings rather than blockers.

**Division of work**

One member will work on (1) and (2), while two members work on (3) and (4) together. To manage workload, we can reduce the number of sub-problems tested, which requires less data and solver implementation.