from html import escape

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def render_local_docs(app: FastAPI) -> HTMLResponse:
    schema = app.openapi()
    sections: list[str] = []

    for path, operations in schema.get("paths", {}).items():
        items: list[str] = []
        for method, details in operations.items():
            summary = escape(details.get("summary") or details.get("description") or "")
            tags = ", ".join(details.get("tags") or ["default"])
            responses = ", ".join(sorted((details.get("responses") or {}).keys()))
            items.append(
                (
                    "<li>"
                    f"<span class='method method-{method.lower()}'>{method.upper()}</span>"
                    f"<code>{escape(path)}</code>"
                    f"<span class='tags'>{escape(tags)}</span>"
                    f"<p>{summary or '未提供说明'}</p>"
                    f"<small>响应状态码：{escape(responses or '未声明')}</small>"
                    "</li>"
                )
            )

        sections.append(
            (
                "<section class='card'>"
                f"<h2>{escape(path)}</h2>"
                f"<ul>{''.join(items)}</ul>"
                "</section>"
            )
        )

    html = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>{escape(app.title)} - API Docs</title>
      <style>
        :root {{
          color-scheme: light;
          font-family: Arial, sans-serif;
        }}
        body {{
          margin: 0;
          background: #f5f7fb;
          color: #1f2937;
        }}
        header {{
          background: #111827;
          color: white;
          padding: 24px 32px;
        }}
        main {{
          max-width: 1080px;
          margin: 0 auto;
          padding: 24px 16px 48px;
        }}
        .meta {{
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
          margin-top: 12px;
        }}
        .pill {{
          background: #e5eefc;
          color: #1d4ed8;
          padding: 6px 10px;
          border-radius: 999px;
          text-decoration: none;
        }}
        .card {{
          background: white;
          border-radius: 12px;
          padding: 20px;
          margin-top: 16px;
          box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08);
        }}
        ul {{
          list-style: none;
          padding-left: 0;
          margin: 0;
        }}
        li {{
          padding: 12px 0;
          border-top: 1px solid #e5e7eb;
        }}
        li:first-child {{
          border-top: none;
        }}
        .method {{
          display: inline-block;
          min-width: 64px;
          font-weight: 700;
          margin-right: 12px;
        }}
        .method-get {{ color: #047857; }}
        .method-post {{ color: #1d4ed8; }}
        .method-put {{ color: #b45309; }}
        .method-delete {{ color: #b91c1c; }}
        .tags {{
          margin-left: 12px;
          color: #6b7280;
        }}
        code {{
          background: #f3f4f6;
          padding: 2px 6px;
          border-radius: 6px;
        }}
        p {{
          margin: 8px 0;
        }}
      </style>
    </head>
    <body>
      <header>
        <h1>{escape(app.title)} API 文档</h1>
        <p>{escape(app.description or "")}</p>
        <div class="meta">
          <span class="pill">版本：{escape(app.version)}</span>
          <a class="pill" href="{escape(app.openapi_url or '/openapi.json')}">OpenAPI JSON</a>
          <a class="pill" href="/admin/">管理后台</a>
        </div>
      </header>
      <main>
        {''.join(sections)}
      </main>
    </body>
    </html>
    """
    return HTMLResponse(html)
