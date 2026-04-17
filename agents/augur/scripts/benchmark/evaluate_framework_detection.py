#!/usr/bin/env python3
"""Run lightweight framework-detection regression checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DETECT = ROOT / "detect_frameworks.py"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_case(repo: Path, case_id: str) -> set[str]:
    if case_id == "fastapi":
        write(repo / "pyproject.toml", "[project]\ndependencies = [\"fastapi\"]\n")
        write(repo / "app.py", "from fastapi import FastAPI\napp = FastAPI()\n@app.get('/health')\ndef health():\n    return {'ok': True}\n")
        return {"fastapi"}
    if case_id == "nestjs":
        write(repo / "package.json", json.dumps({"dependencies": {"@nestjs/common": "^1.0.0", "@nestjs/core": "^1.0.0"}}))
        write(repo / "app.controller.ts", "@Controller()\nexport class AppController {\n  @Get()\n  hello() { return 'ok' }\n}\n")
        return {"nestjs"}
    if case_id == "react":
        write(repo / "package.json", json.dumps({"dependencies": {"react": "^19.0.0", "react-dom": "^19.0.0"}}))
        write(repo / "src" / "main.tsx", "import { createRoot } from 'react-dom/client';\nimport { useState } from 'react';\nfunction App() { const [count] = useState(0); return <div>{count}</div>; }\ncreateRoot(document.getElementById('root')!).render(<App />);\n")
        return {"react"}
    if case_id == "vue":
        write(repo / "package.json", json.dumps({"dependencies": {"vue": "^3.5.0"}}))
        write(repo / "src" / "App.vue", "<template><div>{{ message }}</div></template>\n<script setup lang=\"ts\">\nimport { ref } from 'vue'\nconst message = ref('ok')\n</script>\n")
        return {"vue"}
    if case_id == "angular":
        write(repo / "package.json", json.dumps({"dependencies": {"@angular/core": "^18.0.0", "@angular/router": "^18.0.0"}}))
        write(repo / "src" / "app" / "app.component.ts", "import { Component } from '@angular/core';\n@Component({ selector: 'app-root', template: '<div>ok</div>' })\nexport class AppComponent {}\n")
        return {"angular"}
    if case_id == "nextjs":
        write(repo / "package.json", json.dumps({"dependencies": {"next": "^1.0.0"}}))
        write(repo / "app" / "api" / "users" / "route.ts", "export async function GET() { return Response.json([]) }\n")
        return {"nextjs"}
    if case_id == "rails":
        write(repo / "Gemfile", "gem 'rails'\n")
        write(repo / "config" / "routes.rb", "Rails.application.routes.draw do\n  resources :users\nend\n")
        return {"rails"}
    if case_id == "spring":
        write(repo / "pom.xml", "<project><artifactId>demo</artifactId><dependencies><dependency><artifactId>spring-boot-starter-web</artifactId></dependency></dependencies></project>\n")
        write(repo / "src" / "main" / "java" / "Demo.java", "@SpringBootApplication\n@RestController\nclass Demo {\n  @GetMapping(\"/health\") String health() { return \"ok\"; }\n}\n")
        return {"spring"}
    if case_id == "axum":
        write(repo / "Cargo.toml", "[dependencies]\naxum = \"0.7\"\n")
        write(repo / "src" / "main.rs", "use axum::{routing::get, Router};\nfn app() -> Router { Router::new().route(\"/health\", get(|| async { \"ok\" })) }\n")
        return {"axum"}
    if case_id == "laravel":
        write(repo / "composer.json", json.dumps({"require": {"laravel/framework": "^1.0.0"}}))
        write(repo / "routes" / "api.php", "Route::get('/health', function () { return ['ok' => true]; });\n")
        return {"laravel"}
    if case_id == "gin":
        write(repo / "go.mod", "module example\nrequire github.com/gin-gonic/gin v1.9.0\n")
        write(repo / "main.go", "package main\nimport \"github.com/gin-gonic/gin\"\nfunc main() { r := gin.Default(); r.GET(\"/health\", nil) }\n")
        return {"gin"}
    if case_id == "net-http":
        write(repo / "main.go", "package main\nimport \"net/http\"\nfunc main() { http.HandleFunc(\"/health\", nil); http.ListenAndServe(\":8080\", nil) }\n")
        return {"net-http"}
    if case_id == "phoenix":
        write(repo / "mix.exs", "{:phoenix, \"~> 1.0\"}\n")
        write(repo / "lib" / "app_web" / "router.ex", "defmodule AppWeb.Router do\n  use AppWeb, :router\n  scope \"/\", AppWeb do\n    pipe_through :browser\n  end\nend\n")
        return {"phoenix"}
    if case_id == "grape":
        write(repo / "Gemfile", "gem 'grape'\n")
        write(repo / "api.rb", "class API < Grape::API\n  resource :health do\n    get do\n      { ok: true }\n    end\n  end\nend\n")
        return {"grape"}
    if case_id == "ktor":
        write(repo / "pom.xml", "<project><dependencies><dependency><groupId>io.ktor</groupId><artifactId>ktor-server-core</artifactId></dependency></dependencies></project>\n")
        write(repo / "src" / "main" / "kotlin" / "App.kt", "fun Application.module() { routing { get(\"/health\") { } } }\n")
        return {"ktor"}
    if case_id == "aspnet-minimal":
        write(repo / "app.csproj", "<Project><ItemGroup><FrameworkReference Include=\"Microsoft.AspNetCore.App\" /></ItemGroup></Project>\n")
        write(repo / "Program.cs", "var builder = WebApplication.CreateBuilder(args);\nvar app = builder.Build();\napp.MapGet(\"/health\", () => \"ok\");\n")
        return {"aspnet-minimal"}
    if case_id == "aspnet-controllers":
        write(repo / "app.csproj", "<Project><ItemGroup><FrameworkReference Include=\"Microsoft.AspNetCore.App\" /></ItemGroup></Project>\n")
        write(repo / "UsersController.cs", "[ApiController]\n[Route(\"api/[controller]\")]\npublic class UsersController : ControllerBase {\n  [HttpGet]\n  public string Get() => \"ok\";\n}\n")
        return {"aspnet-controllers"}
    if case_id == "vapor":
        write(repo / "Package.swift", ".package(url: \"https://github.com/vapor/vapor.git\", from: \"4.0.0\")\n")
        write(repo / "Sources" / "App" / "routes.swift", "import Vapor\nfunc routes(_ app: Application) throws { app.get(\"health\") { _ in \"ok\" } }\n")
        return {"vapor"}
    raise ValueError(f"unsupported case: {case_id}")


def run_case(case_id: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix=f"augur-fw-{case_id}-") as tmp:
        repo = Path(tmp)
        expected = build_case(repo, case_id)
        result = subprocess.run(
            [sys.executable, str(DETECT), str(repo), "--pretty"],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout or "{}") if result.returncode == 0 else {}
        facts = payload.get("facts", []) if isinstance(payload, dict) else []
        detected = {str(f.get("raw_evidence", {}).get("framework") or "") for f in facts if f.get("kind") == "framework"}
        detected.discard("")
        return {
            "case": case_id,
            "expected": sorted(expected),
            "detected": sorted(detected),
            "missing": sorted(expected - detected),
            "unexpected": sorted(detected - expected),
            "returncode": result.returncode,
            "stderr": (result.stderr or "").strip(),
            "passed": result.returncode == 0 and detected == expected,
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate framework detection on synthetic repos.")
    parser.add_argument(
        "--cases",
        nargs="*",
        default=[
            "fastapi",
            "nestjs",
            "react",
            "vue",
            "angular",
            "nextjs",
            "rails",
            "spring",
            "axum",
            "laravel",
            "gin",
            "net-http",
            "phoenix",
            "grape",
            "ktor",
            "aspnet-minimal",
            "aspnet-controllers",
            "vapor",
        ],
        help="Framework cases to run.",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    results = [run_case(case_id) for case_id in args.cases]
    summary = {
        "cases": results,
        "passed": sum(1 for item in results if item["passed"]),
        "failed": sum(1 for item in results if not item["passed"]),
    }
    rendered = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
