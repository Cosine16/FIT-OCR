package com.cosine.fitocr.data.api

import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.GET
import retrofit2.http.Multipart
import retrofit2.http.POST
import retrofit2.http.Part

interface FitOcrApi {
    @Multipart
    @POST("recognize")
    suspend fun recognize(
        @Part file: MultipartBody.Part,
        @Part("engine") engine: RequestBody
    ): Response<OcrResponse>

    @GET("health")
    suspend fun health(): Response<HealthResponse>
}
