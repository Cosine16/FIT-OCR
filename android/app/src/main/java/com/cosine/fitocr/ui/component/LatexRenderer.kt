package com.cosine.fitocr.ui.component

import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView

@Composable
fun LatexRenderer(
    latex: String,
    modifier: Modifier = Modifier
) {
    val darkTheme = isSystemInDarkTheme()
    val textColor = if (darkTheme) "#e2e8f0" else "#0f172a"
    val bgColor = if (darkTheme) "#1e293b" else "#f8fafc"

    val htmlContent = remember(latex, textColor, bgColor) {
        val escaped = latex
            .replace("\\", "\\\\")
            .replace("'", "\\'")
            .replace("\"", "\\\"")
            .replace("\n", "\\n")
            .replace("\r", "")
            .replace("<", "\\u003C")
            .replace(">", "\\u003E")

        """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
            <style>
                * { box-sizing: border-box; }
                body {
                    margin: 0;
                    padding: 16px;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: $bgColor;
                    color: $textColor;
                    font-size: 15px;
                    line-height: 1.7;
                }
                .katex { font-size: 1.08em; }
                .katex-display { margin: 0.8em 0; overflow-x: auto; overflow-y: hidden; }
                p { margin: 0.4em 0; }
                code {
                    background: rgba(128,128,128,0.15);
                    padding: 2px 6px;
                    border-radius: 4px;
                    font-family: 'SF Mono', Monaco, monospace;
                    font-size: 0.92em;
                }
                pre {
                    background: rgba(128,128,128,0.1);
                    padding: 12px;
                    border-radius: 8px;
                    overflow-x: auto;
                }
            </style>
        </head>
        <body>
            <div id="content"></div>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    var content = document.getElementById('content');
                    var html = '$escaped';
                    html = html.replace(/\\n\\n+/g, '</p><p>');
                    html = html.replace(/\\n/g, '<br>');
                    content.innerHTML = '<p>' + html + '</p>';
                    if (window.renderMathInElement) {
                        renderMathInElement(content, {
                            delimiters: [
                                {left: '$$', right: '$$', display: true},
                                {left: '$', right: '$', display: false},
                                {left: '\\(', right: '\\)', display: false},
                                {left: '\\[', right: '\\]', display: true}
                            ],
                            throwOnError: false
                        });
                    }
                });
            </script>
        </body>
        </html>
        """.trimIndent()
    }

    AndroidView(
        factory = { context ->
            WebView(context).apply {
                settings.javaScriptEnabled = true
                settings.domStorageEnabled = true
                settings.loadsImagesAutomatically = true
                settings.cacheMode = WebSettings.LOAD_CACHE_ELSE_NETWORK
                settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                settings.setSupportZoom(false)
                webViewClient = WebViewClient()
                isVerticalScrollBarEnabled = false
                isHorizontalScrollBarEnabled = false
            }
        },
        update = { webView ->
            webView.loadDataWithBaseURL(
                "https://cdn.jsdelivr.net",
                htmlContent,
                "text/html",
                "UTF-8",
                null
            )
        },
        modifier = modifier
            .fillMaxWidth()
            .height(280.dp)
            .padding(4.dp)
    )
}
