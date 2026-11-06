---
name: Agent Workflow Glossary
description: Canonical terminology for interpreting project scope, specifications, approvals, and reusable agent resources in this repository.
---

# Agent Workflow Language

This glossary defines the shared language used by humans and agents to coordinate Spec-Driven Development across independent showcase projects.

## Scope

**Project**:
An independent System Analysis and Design case study with its own specifications, architecture, implementation, and verification artifacts.
_Avoid_: repository, feature

**Active Project**:
The single Project whose artifacts and behavior are in scope for the current task.
_Avoid_: current repository, default project

**Repository-wide Scope**:
A task scope that changes shared resources or coordinates more than one Project rather than operating inside one Active Project.
_Avoid_: global project, root project

## Specifications

**Requirement**:
An approved statement of a stakeholder need, constraint, or outcome that the system must satisfy.
_Avoid_: implementation detail, solution

**Specification (Spec)**:
A testable design artifact that translates Requirements into defined system behavior, contracts, models, or architecture.
_Avoid_: requirement, code

**Approved Spec**:
A Spec explicitly accepted by an authorized user and carrying durable approval evidence.
_Avoid_: final draft, completed document

**Governing Spec**:
The Approved Spec that authorizes and constrains a particular implementation change.
_Avoid_: related document, reference note

## Repository Ownership

**Showcase Repository**:
The outer repository that owns Projects, specifications, diagrams, manifests, and shared agent resources but not Component Repository source code.
_Avoid_: monorepo, parent source repository

**Repository Manifest**:
A Project-owned `REPOS.md` declaration of every Component Repository and its reproducible baseline.
_Avoid_: repository list, clone notes

**Checkout Directory**:
The Project boundary reserved for materialized Component Repositories.
_Avoid_: source root, backend repository

**Component Repository**:
An independently versioned Git repository declared by a Repository Manifest and materialized inside a Checkout Directory.
_Avoid_: folder, submodule

**Migration-Pending Project**:
A legacy Project whose code has not yet been converted to manifest-managed Component Repositories.
_Avoid_: invalid project, partially cloned project

## Agent Resources

**Rule**:
A mandatory constraint that applies whenever its declared scope matches the task.
_Avoid_: suggestion, preference

**Workflow**:
An ordered process with explicit completion criteria for producing a defined outcome.
_Avoid_: checklist, rule

**Agent Role**:
A bounded set of responsibilities and decisions used as an analytical perspective or, when ready, an executable agent definition.
_Avoid_: skill, subagent

**Skill**:
A reusable task method with a trigger, required inputs, ordered instructions, outputs, and completion criteria.
_Avoid_: role, template

**Ready Resource**:
An agent resource with actionable content that may govern work.
_Avoid_: available placeholder

**Placeholder Resource**:
A reserved agent resource that has not been designed and must not govern work.
_Avoid_: ready resource, optional instruction
