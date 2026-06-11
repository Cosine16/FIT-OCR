package com.cosine.fitocr.domain.model

data class OcrResult(
    val markdown: String,
    val engine: String,
    val elapsedS: Double,
    val imageUrl: String,
    val timestamp: Long = System.currentTimeMillis()
)

enum class OcrEngine(val value: String, val displayName: String) {
    LOCAL("local", "本地"),
    CLOUD("cloud", "云端"),
    FALLBACK("fallback", "自动")
}

sealed class OcrUiState {
    object Idle : OcrUiState()
    object Loading : OcrUiState()
    data class Success(val result: OcrResult) : OcrUiState()
    data class Error(val message: String) : OcrUiState()
}
