# server.py — Atlas 7.0 FastAPI Server

import sys
import os
import threading
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import uvicorn

import config

app = FastAPI(title="Atlas 7.0 API", version="7.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Global error handler =====
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ Error on {request.url}: {exc}")
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"error": str(exc)})

# ===== LAZY IMPORTS (error হলেও server চলবে) =====
ai_engine = None
language_detector = None
memory_manager = None
command_parser = None
context_engine = None
pin_auth = None
session_manager = None
auth_logger = None
voice_output = None
VOICE_AVAILABLE = False
FACE_AUTH_AVAILABLE = False

def load_modules():
    global ai_engine, language_detector, memory_manager, command_parser
    global context_engine, pin_auth, session_manager, auth_logger
    global voice_output, VOICE_AVAILABLE, FACE_AUTH_AVAILABLE

    try:
        from backend.core.ai_engine import ai_engine as _ae
        ai_engine = _ae
        print("✅ AI Engine loaded")
    except Exception as e:
        print(f"⚠️ AI Engine: {e}")

    try:
        from backend.core.language import language_detector as _ld
        language_detector = _ld
    except Exception as e:
        print(f"⚠️ Language detector: {e}")

    try:
        from backend.core.memory import memory_manager as _mm
        memory_manager = _mm
    except Exception as e:
        print(f"⚠️ Memory: {e}")

    try:
        from backend.core.command_parser import command_parser as _cp
        command_parser = _cp
    except Exception as e:
        print(f"⚠️ Command parser: {e}")

    try:
        from backend.core.context_engine import context_engine as _ce
        context_engine = _ce
    except Exception as e:
        print(f"⚠️ Context engine: {e}")

    try:
        from backend.auth.pin_auth import pin_auth as _pa
        pin_auth = _pa
        print("✅ PIN Auth loaded")
    except Exception as e:
        print(f"⚠️ PIN Auth: {e}")

    try:
        from backend.auth.session_manager import session_manager as _sm
        session_manager = _sm
    except Exception as e:
        print(f"⚠️ Session manager: {e}")

    try:
        from backend.auth.auth_logger import auth_logger as _al
        auth_logger = _al
    except Exception as e:
        print(f"⚠️ Auth logger: {e}")

    try:
        from backend.core.voice_output import voice_output as _vo
        voice_output = _vo
        VOICE_AVAILABLE = True
        print("✅ Voice loaded")
    except Exception as e:
        print(f"⚠️ Voice: {e}")

    try:
        from backend.auth.face_auth import face_auth_engine
        FACE_AUTH_AVAILABLE = True
        print("✅ Face auth loaded")
    except Exception as e:
        print(f"⚠️ Face auth: {e}")

# ===== MODELS =====
class CommandRequest(BaseModel):
    command: str

class PinRequest(BaseModel):
    pin: str

# ===== AUTH =====
@app.post("/api/auth/pin")
async def verify_pin(req: PinRequest):
    try:
        if pin_auth is None:
            return {"success": False, "reason": "Auth module not loaded"}

        success, msg = pin_auth.verify(req.pin)
        if success:
            token = "atlas_session_token"
            if session_manager:
                try:
                    token = session_manager.create_session("main_user", "pin")
                except:
                    pass
            if auth_logger:
                try:
                    auth_logger.log_success("main_user", "pin")
                except:
                    pass
            return {"success": True, "user_id": "main_user", "session_token": token}

        if auth_logger:
            try:
                auth_logger.log_failure("pin", msg)
            except:
                pass
        return {"success": False, "reason": msg}

    except Exception as e:
        print(f"❌ PIN verify error: {e}")
        traceback.print_exc()
        return {"success": False, "reason": f"Server error: {str(e)}"}

@app.post("/api/auth/logout")
async def logout():
    try:
        if session_manager:
            session_manager.end_all_sessions()
    except:
        pass
    return {"success": True}

# ===== COMMAND =====
@app.post("/api/command")
async def take_command(req: CommandRequest):
    try:
        command = req.command.strip()
        if not command:
            return {"response": None}

        print(f"\n📝 User: {command}")

        if ai_engine is None or language_detector is None:
            load_modules()

        from command_handler import get_command_response

        result = get_command_response(command)
        response = result.get("response")
        lang = result.get("language", "en")

        if response:
            print(f"🤖 Atlas: {str(response)[:100]}")
            if VOICE_AVAILABLE and voice_output:
                threading.Thread(
                    target=voice_output.speak,
                    args=(response, lang),
                    daemon=True
                ).start()

        return {
            "response": response,
            "language": lang,
            "intent": result.get("intent"),
            "confidence": result.get("confidence"),
            "method": result.get("method"),
            "entities": result.get("entities", {}),
        }

    except Exception as e:
        print(f"❌ Command error: {e}")
        traceback.print_exc()
        return {"response": f"❌ Error: {str(e)}", "language": "en"}

# ===== SYSTEM =====
@app.get("/api/system/metrics")
async def get_metrics():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        bat = psutil.sensors_battery()
        return {
            "cpu": round(cpu, 1),
            "mem_used": round(mem.used / (1024**2)),
            "mem_percent": round(mem.percent, 1),
            "disk_percent": round(disk.percent, 1),
            "bat_percent": round(bat.percent, 1) if bat else -1,
            "bat_charging": bat.power_plugged if bat else False,
        }
    except Exception as e:
        return {"cpu": 0, "mem_used": 0, "mem_percent": 0, "disk_percent": 0, "bat_percent": -1, "bat_charging": False}

@app.get("/api/system/weather")
async def get_weather():
    try:
        import requests as req_lib
        api_key = config.WEATHER_API_KEY
        if api_key and "your" not in api_key.lower() and "xxx" not in api_key.lower():
            url = f"https://api.openweathermap.org/data/2.5/weather?q={config.DEFAULT_CITY}&appid={api_key}&units=metric"
            resp = req_lib.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "temp": round(data["main"]["temp"], 1),
                    "desc": data["weather"][0]["description"],
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                    "city": config.DEFAULT_CITY
                }
    except:
        pass
    return {"temp": 30, "desc": "Partly Cloudy", "humidity": 65, "wind": 12, "city": config.DEFAULT_CITY}

@app.get("/api/system/prayer-times")
async def get_prayer_times():
    try:
        import requests as req_lib
        url = f"https://api.aladhan.com/v1/timingsByCity?city={config.PRAYER_CITY}&country={config.PRAYER_COUNTRY}&method=1"
        r = req_lib.get(url, timeout=5)
        if r.status_code == 200:
            t = r.json()["data"]["timings"]
            return {
                "fajr": t["Fajr"], "dhuhr": t["Dhuhr"],
                "asr": t["Asr"], "maghrib": t["Maghrib"], "isha": t["Isha"],
                "city": config.PRAYER_CITY
            }
    except:
        pass
    return {"error": "Could not fetch prayer times"}

@app.get("/api/system/groq-status")
async def groq_status():
    try:
        if ai_engine:
            status = ai_engine.get_key_status()
            return status.get("groq", [])
    except:
        pass
    return []

# ===== AGENTS =====
@app.post("/api/agent/optimize-pc")
async def optimize_pc():
    try:
        from backend.agent.pc_agent import pc_agent
        return pc_agent.optimize()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/agent/clean-temp")
async def clean_temp():
    try:
        from backend.agent.pc_agent import pc_agent
        return {"freed_mb": pc_agent.clean_temp()}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/agent/list-files")
async def list_files(path: str = ""):
    try:
        from backend.agent.file_agent import file_agent
        return file_agent.list_folder(path or str(file_agent.home))
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/agent/search-files")
async def search_files(query: str):
    try:
        from backend.agent.file_agent import file_agent
        return file_agent.search_files(query)
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/agent/organize-downloads")
async def organize_downloads():
    try:
        from backend.agent.file_agent import file_agent
        return file_agent.organize_downloads()
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/agent/execute")
async def execute_command(body: dict):
    try:
        from backend.agent.terminal_agent import terminal_agent
        result = terminal_agent.execute_safe(body.get("cmd", ""))
        return {"output": result['stdout'] if result['success'] else result['stderr']}
    except Exception as e:
        return {"error": str(e)}

# ===== ML AGENT =====
ml_agent_instance = None

def _get_ml_agent():
    global ml_agent_instance
    if ml_agent_instance is None:
        from backend.agent.ml_agent import ml_agent as _ml
        ml_agent_instance = _ml
    return ml_agent_instance

@app.post("/api/ml/upload")
async def ml_upload(file: UploadFile = File(...), file_type: str = Form("auto")):
    try:
        contents = await file.read()
        if not contents:
            return {"success": False, "message": "Empty file"}
        if not file.filename:
            return {"success": False, "message": "No filename"}
        temp_path = Path.home() / "Atlas" / "ml_models" / file.filename
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_bytes(contents)
        agent = _get_ml_agent()
        result = agent.handle("load_dataset", {"filepath": str(temp_path), "file_type": file_type})
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"success": False, "message": f"Upload error: {str(e)}"}

@app.post("/api/ml/analyze")
async def ml_analyze(body: dict):
    try:
        agent = _get_ml_agent()
        data_params = body.get("data", body)
        return agent.handle("analyze_data", data_params)
    except Exception as e:
        return {"success": False, "message": f"Analysis error: {str(e)}"}

@app.post("/api/ml/train")
async def ml_train(body: dict):
    try:
        agent = _get_ml_agent()
        intent = body.get("intent", "train_classifier")
        return agent.handle(intent, {
            "session_id": body.get("session_id", ""),
            "data": body.get("data", {}),
            "target": body.get("target", ""),
            "algorithm": body.get("algorithm", "auto"),
            "texts": body.get("texts", []),
            "labels": body.get("labels", []),
        })
    except Exception as e:
        return {"success": False, "message": f"Training error: {str(e)}"}

@app.post("/api/ml/predict")
async def ml_predict(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("predict", {
            "model_id": body.get("model_id", ""),
            "input": body.get("input", {})
        })
    except Exception as e:
        return {"success": False, "message": f"Prediction error: {str(e)}"}

@app.get("/api/ml/models")
async def ml_models():
    try:
        agent = _get_ml_agent()
        return agent.handle("list_models", {})
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.delete("/api/ml/models/{model_id}")
async def ml_delete_model(model_id: str):
    try:
        agent = _get_ml_agent()
        return agent.handle("delete_model", {"model_id": model_id})
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/ml/models/{model_id}")
async def ml_get_model_info(model_id: str):
    try:
        agent = _get_ml_agent()
        return agent.handle("model_info", {"model_id": model_id})
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/ml/jobs/{job_id}")
async def ml_job_status(job_id: str):
    try:
        agent = _get_ml_agent()
        return agent.handle("job_status", {"job_id": job_id})
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.post("/api/ml/plot")
async def ml_plot(body: dict):
    try:
        agent = _get_ml_agent()
        data_params = body.get("data", {})
        result = agent.handle("plot_data", {
            "session_id": body.get("session_id") or data_params.get("session_id", ""),
            "data": data_params,
            "plot_type": body.get("plot_type", "histogram"),
            "columns": body.get("columns")
        })
        if result.get("success") and result.get("plot_path"):
            p = Path(result["plot_path"])
            if p.exists():
                import base64
                result["plot_base64"] = base64.b64encode(p.read_bytes()).decode()
        return result
    except Exception as e:
        return {"success": False, "message": f"Plot error: {str(e)}"}

# ===== NEW ML ENDPOINTS =====

@app.post("/api/ml/cluster")
async def ml_cluster(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("train_cluster", {
            "session_id": body.get("session_id", ""),
            "algorithm": body.get("algorithm", "kmeans"),
            "n_clusters": body.get("n_clusters", 3),
            "eps": body.get("eps", 0.5),
            "min_samples": body.get("min_samples", 5),
        })
    except Exception as e:
        return {"success": False, "message": f"Cluster error: {str(e)}"}

@app.post("/api/ml/dimreduce")
async def ml_dimreduce(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("reduce_dim", {
            "session_id": body.get("session_id", ""),
            "algorithm": body.get("algorithm", "pca"),
            "n_components": body.get("n_components", 2),
        })
    except Exception as e:
        return {"success": False, "message": f"DimRed error: {str(e)}"}

@app.post("/api/ml/neural")
async def ml_neural(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("train_mlp", {
            "session_id": body.get("session_id", ""),
            "target": body.get("target", ""),
            "task_type": body.get("task_type", "classification"),
            "hidden_layers": body.get("hidden_layers", "100,50"),
            "max_iter": body.get("max_iter", 500),
        })
    except Exception as e:
        return {"success": False, "message": f"MLP error: {str(e)}"}

@app.post("/api/ml/tune")
async def ml_tune(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("tune_hyperparams", {
            "session_id": body.get("session_id", ""),
            "target": body.get("target", ""),
            "task_type": body.get("task_type", "classification"),
            "algorithm": body.get("algorithm", "random_forest"),
            "param_grid": body.get("param_grid"),
            "cv": body.get("cv", 5),
            "scoring": body.get("scoring", "accuracy"),
        })
    except Exception as e:
        return {"success": False, "message": f"Tune error: {str(e)}"}

@app.post("/api/ml/kfold")
async def ml_kfold(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("train_kfold", {
            "session_id": body.get("session_id", ""),
            "target": body.get("target", ""),
            "task_type": body.get("task_type", "classification"),
            "algorithm": body.get("algorithm", "random_forest"),
            "n_splits": body.get("n_splits", 5),
        })
    except Exception as e:
        return {"success": False, "message": f"K-Fold error: {str(e)}"}

@app.post("/api/ml/feature_engineer")
async def ml_feature_engineer(body: dict):
    try:
        agent = _get_ml_agent()
        return agent.handle("feature_engineer", {
            "session_id": body.get("session_id", ""),
            "operations": body.get("operations", []),
        })
    except Exception as e:
        return {"success": False, "message": f"FeatEng error: {str(e)}"}

@app.post("/api/ml/evaluate")
async def ml_evaluate(body: dict):
    try:
        agent = _get_ml_agent()
        metric = body.get("metric", "confusion_matrix")
        if metric == "confusion_matrix":
            return agent.handle("confusion_matrix", {
                "model_id": body.get("model_id", ""),
                "session_id": body.get("session_id", ""),
            })
        elif metric == "roc_curve":
            return agent.handle("roc_curve", {
                "model_id": body.get("model_id", ""),
                "session_id": body.get("session_id", ""),
            })
        elif metric == "elbow":
            return agent.handle("elbow_plot", {
                "session_id": body.get("session_id", ""),
                "max_k": body.get("max_k", 10),
            })
        return {"success": False, "message": f"Unknown metric: {metric}"}
    except Exception as e:
        return {"success": False, "message": f"Evaluate error: {str(e)}"}

# ===== CONFIG =====
@app.get("/api/config")
async def get_config():
    return {
        "app_name": config.APP_NAME,
        "app_version": config.APP_VERSION,
        "user_name": config.USER_NAME,
        "atlas_name": config.ATLAS_NAME,
        "default_city": config.DEFAULT_CITY,
        "theme_color": config.THEME_COLOR,
        "face_available": FACE_AUTH_AVAILABLE,
        "voice_available": VOICE_AVAILABLE,
    }

# ===== WEBSOCKET =====
class ConnectionManager:
    def __init__(self):
        self.active = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# ===== HEALTH =====
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "version": config.APP_VERSION,
        "pin_auth": pin_auth is not None,
        "ai_engine": ai_engine is not None,
        "voice": VOICE_AVAILABLE,
    }

# ===== STARTUP =====
@app.on_event("startup")
async def startup_event():
    print("🔧 Loading modules...")
    load_modules()
    # Start continuous voice listening (if available) and route to command handler
    try:
        from backend.core.voice_input import voice_input as _voice_input
        from command_handler import get_command_response as _get_command_response

        def _voice_callback(cmd: str):
            try:
                if not cmd:
                    return
                # Route recognized text to command processing
                resp = _get_command_response(cmd)
                # Speak response if voice output available
                if voice_output and resp and isinstance(resp, dict):
                    lang = "en"
                    try:
                        lang = language_detector.detect(cmd) if language_detector else "en"
                    except:
                        pass
                    threading.Thread(target=voice_output.speak, args=(resp.get("response", ""), lang), daemon=True).start()
            except Exception as e:
                print(f"⚠️ Voice callback error: {e}")

        # Start background listening
        try:
            _voice_input.start_continuous_listening(callback=_voice_callback)
            print("✅ Voice continuous listening started")
        except Exception as e:
            print(f"⚠️ Could not start voice listening: {e}")
    except Exception as e:
        print(f"⚠️ Voice listening not initialized: {e}")
    print("✅ Atlas 7.0 ready!")

# ===== STATIC FILES (serve built frontend) =====
DIST_DIR = os.path.join(os.path.dirname(__file__), "frontend", "dist")

# Mount static assets (JS, CSS) and root files (favicon, etc.)
if os.path.isdir(DIST_DIR):
    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
        print(f"✅ Frontend assets mounted from {assets_dir}")

    @app.middleware("http")
    async def spa_fallback(request: Request, call_next):
        """Serve index.html for any non-API GET request that would 404."""
        response = await call_next(request)
        if response.status_code == 404 and request.method == "GET":
            path = request.url.path
            # Don't intercept API, WebSocket, or docs routes
            if not any(path.startswith(p) for p in ("/api", "/ws", "/docs", "/openapi", "/assets")):
                index_path = os.path.join(DIST_DIR, "index.html")
                if os.path.exists(index_path):
                    return FileResponse(index_path, media_type="text/html")
        return response
    print("✅ SPA fallback middleware active")
else:
    print(f"⚠️ Frontend dist not found at {DIST_DIR} — serving API only")

# ===== MAIN =====
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Atlas 7.0 — FastAPI Server")
    print("=" * 60)
    print("   App:  http://localhost:8000")
    print("   API:  http://localhost:8000/api/health")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False, log_level="info")