package com.cosine.fitocr.data.api

import com.google.gson.annotations.SerializedName

data class OcrResponse(
    @SerializedName("image_url") val imageUrl: String,
    @SerializedName("markdown_url") val markdownUrl: String,
    @SerializedName("markdown") val markdown: String,
    @SerializedName("elapsed_s") val elapsedS: Double,
    @SerializedName("engine") val engine: String
)

data class HealthResponse(
    @SerializedName("ok") val ok: Boolean,
    @SerializedName("torch") val torch: String,
    @SerializedName("cuda") val cuda: Boolean,
    @SerializedName("device") val device: String?
)
