package com.cosine.fitocr.data.repository

import android.content.Context
import android.net.Uri
import com.cosine.fitocr.data.api.FitOcrApi
import com.cosine.fitocr.domain.model.OcrEngine
import com.cosine.fitocr.domain.model.OcrResult
import com.cosine.fitocr.domain.model.OcrUiState
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody
import java.net.SocketTimeoutException
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class OcrRepository @Inject constructor(
    private val api: FitOcrApi,
    @ApplicationContext private val context: Context
) {
    private val _uiState = MutableStateFlow<OcrUiState>(OcrUiState.Idle)
    val uiState: StateFlow<OcrUiState> = _uiState.asStateFlow()

    suspend fun recognizeImage(uri: Uri, engine: OcrEngine) {
        _uiState.value = OcrUiState.Loading

        try {
            val bytes = withContext(kotlinx.coroutines.Dispatchers.IO) {
                context.contentResolver.openInputStream(uri)?.use { it.readBytes() }
                    ?: throw IllegalArgumentException("无法打开文件")
            }

            val requestBody = bytes.toRequestBody("image/*".toMediaType())
            val filePart = MultipartBody.Part.createFormData(
                "file", "image.jpg", requestBody
            )
            val engineBody = engine.value.toRequestBody("text/plain".toMediaType())

            val response = api.recognize(filePart, engineBody)

            if (response.isSuccessful) {
                val body = response.body()
                if (body != null) {
                    _uiState.value = OcrUiState.Success(
                        OcrResult(
                            markdown = body.markdown,
                            engine = body.engine,
                            elapsedS = body.elapsedS,
                            imageUrl = body.imageUrl
                        )
                    )
                } else {
                    _uiState.value = OcrUiState.Error("响应体为空")
                }
            } else {
                val errorMsg = response.errorBody()?.string() ?: "未知错误"
                _uiState.value = OcrUiState.Error(errorMsg)
            }
        } catch (e: CancellationException) {
            _uiState.value = OcrUiState.Idle
        } catch (e: SocketTimeoutException) {
            _uiState.value = OcrUiState.Error(
                "请求超时，首次识别需加载模型，请耐心等待后重试"
            )
        } catch (e: Exception) {
            _uiState.value = OcrUiState.Error(e.message ?: "网络错误")
        }
    }

    fun resetState() {
        _uiState.value = OcrUiState.Idle
    }
}
