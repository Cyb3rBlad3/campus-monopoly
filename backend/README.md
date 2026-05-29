# CampusMonopoly Backend

FastAPI 后端，首期目标是支撑 `front_end` 的 H5 联调与核心规则闭环。

## 本地启动

```bash
cd backend
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

前端 `.env.development`：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 测试

```bash
cd backend
pytest
```

## 文档

- `docs/frontend_function_analysis.md`：前端逐函数解读。
- `docs/frontend_logic_flow.md`：前端功能和状态流。
- `docs/api_contract.md`：前后端接口契约。
- `docs/backend_design_rationale.md`：后端文件设计依据。
- `docs/development_log.md`：开发过程记录。
