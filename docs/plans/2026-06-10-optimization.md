# 项目优化实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 修复6项审查中发现的逻辑问题和代码清理

**Tech Stack:** Python 3.9+, FastAPI, Uvicorn

---

### Task 1: 修复 `constants.py` 多余的 `""`
**Files:** Modify: `server/config/constants.py:1`

### Task 2: 修复 `heal()` HP恢复公式冗余
**Files:** Modify: `server/models/game_state.py:281`

### Task 3: 使用 `effective_diff` 计算实际成功率
**Files:** Modify: `server/models/game_state.py:200-201`

### Task 4: 任务失败惩罚按风险等级分级
**Files:** Modify: `server/config/data.py` (添加 failure 字段)
**Files:** Modify: `server/models/game_state.py:231-233` (使用新字段)

### Task 5: 添加线程安全的游戏状态管理
**Files:** Modify: `server/api/routes.py`

### Task 6: 添加服务端日志
**Files:** Modify: `server/main.py`
