---
name: unit-test
description: This skill should be used when the user asks to "单元测试", "写测试", "测试代码", "跑测试", "测试报告", "给代码加测试", "unit test", "add tests", "write tests", or wants to create/run unit tests for the code and produce a test report. 教 Claude 建立测试框架、为代码编写单元测试、运行测试,并用通俗易懂的方式输出测试报告。
---

# 单元测试(unit-test) —— Python / pytest 版

## 用途

帮项目:①搭好测试框架;②给代码写「输入 → 期望输出」的单元测试;③运行测试;④出一份通俗易懂的测试报告。

## 测试框架

- 本项目后端是 **Python(FastAPI + LangChain)**,默认用 **pytest**(Python 最主流的测试框架)。
- 若项目已用了 unittest,以现有为准,不要重复装。

## 步骤

### 第 1 步:确定测什么

- 先问用户「想测哪个功能 / 模块」。
- 用户说「随便 / 你定」时,优先选**纯逻辑、最容易出错**的代码:
  - 密码哈希/校验、JWT 令牌(如 `app/core/security.py`)。
  - 字符串拼接、编号、格式转换(如 `app/rag/chain.py` 的 `build_context`)。
  - 参数校验(如 `app/schemas.py` 的 Pydantic 模型)。
  - 文本分块逻辑(如 `app/rag/splitter.py`)。
- **尽量测「纯函数」**:不碰数据库、网络、大模型、向量库的部分,最容易写、最稳定。

### 第 2 步:确认 / 安装 pytest

- 看有没有 pytest;没有就装:

```bash
pip install pytest
# 需要覆盖率时:
pip install pytest-cov
```

- 测试文件命名 `test_*.py`,统一放在 `tests/` 目录。

### 第 3 步:写测试

- 每个测试就是一个「输入 → 期望输出」的用例,用 `def test_xxx():` 写用例、`assert` 断言:

```python
from app.core.security import hash_password, verify_password


def test_hash_and_verify():
    hashed = hash_password("abc123456")
    assert hashed != "abc123456"                 # 不存明文
    assert verify_password("abc123456", hashed) is True
    assert verify_password("wrong", hashed) is False
```

### 第 4 步:运行

在 `backend/` 目录下用模块方式跑(保证 `app` 可导入):

```bash
python -m pytest tests/ -v
# 需要覆盖率时:
python -m pytest tests/ --cov=app --cov-report=term-missing
```

### 第 5 步:出报告(重要)

跑完后,给用户一份**详细成绩单**,分三部分:

**① 总体统计表**(两列,表头「项目 | 数值」):

| 项目 | 数值 |
| --- | --- |
| 测试文件 | N 个 |
| 测试用例 | N 个 |
| 通过数 | N |
| 失败数 | N |
| 总耗时 | 0.7s |

**② 各模块明细表**(每个测试文件一行):

| 模块 / 文件 | 类型 | 用例数 | 通过 | 失败 | 状态 |
| --- | --- | --- | --- | --- | --- |
| tests/test_security.py | 密码/JWT | 8 | 8 | 0 | ✅ 通过 |

**③ 失败说明**(如有失败):逐个说清「哪道题、期望什么、实际是什么」,并指出问题可能出在哪段代码、怎么修。

## 针对本项目的坑(FastAPI + LangChain + SQLAlchemy)

- 被测代码如果 import 了 `langchain`、`chromadb`、`sentence_transformers` 或触发模型加载(如 `get_embeddings()`),直接跑会**很慢 / 要下载模型 / 报错**——优先测不依赖这些的纯函数。
- 测 SQLAlchemy 模型/接口时,用内存 SQLite(`sqlite:///:memory:`)或 mock 掉 `get_db` 依赖。
- 测 LLM 相关时用 mock,**不要真调 API**(费钱、慢、有额度限制)。

## 注意

- 只新增测试文件,不改业务代码,别把被测代码改坏。
- 用户是技术小白:报告一定用大白话,不要直接甩一堆英文报错日志。
