package com.cosine.fitocr.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.cosine.fitocr.data.api.FitOcrApi
import com.cosine.fitocr.data.preferences.SettingsPreferences
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.net.SocketTimeoutException
import javax.inject.Inject

/**
 * 设置页面 ViewModel
 * 管理连接测试状态和自定义 IP 地址
 */
@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val api: FitOcrApi,
    private val settingsPreferences: SettingsPreferences
) : ViewModel() {

    // 连接测试状态
    sealed class ConnectionStatus {
        object Idle : ConnectionStatus()
        object Testing : ConnectionStatus()
        data class Success(
            val torch: String,
            val cuda: Boolean,
            val device: String?
        ) : ConnectionStatus()
        data class Failed(val message: String) : ConnectionStatus()
    }

    private val _connectionStatus = MutableStateFlow<ConnectionStatus>(ConnectionStatus.Idle)
    val connectionStatus: StateFlow<ConnectionStatus> = _connectionStatus.asStateFlow()

    // IP 输入相关
    private val _inputAddress = MutableStateFlow(settingsPreferences.getBaseUrl()?.let { extractAddress(it) } ?: "")
    val inputAddress: StateFlow<String> = _inputAddress.asStateFlow()

    private val _addressError = MutableStateFlow<String?>(null)
    val addressError: StateFlow<String?> = _addressError.asStateFlow()

    private val _saveSuccess = MutableStateFlow(false)
    val saveSuccess: StateFlow<Boolean> = _saveSuccess.asStateFlow()

    /**
     * 测试与后端的连接
     */
    fun testConnection() {
        _connectionStatus.value = ConnectionStatus.Testing
        viewModelScope.launch {
            try {
                val response = api.health()
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null && body.ok) {
                        _connectionStatus.value = ConnectionStatus.Success(
                            torch = body.torch,
                            cuda = body.cuda,
                            device = body.device
                        )
                    } else {
                        _connectionStatus.value = ConnectionStatus.Failed("服务状态异常")
                    }
                } else {
                    _connectionStatus.value = ConnectionStatus.Failed(
                        "HTTP ${response.code()}: ${response.message()}"
                    )
                }
            } catch (e: SocketTimeoutException) {
                _connectionStatus.value = ConnectionStatus.Failed("连接超时，请检查地址和网络")
            } catch (e: Exception) {
                _connectionStatus.value = ConnectionStatus.Failed(
                    e.message?.takeIf { it.isNotEmpty() } ?: "无法连接到服务器"
                )
            }
        }
    }

    /**
     * 更新 IP 输入框内容
     */
    fun updateInputAddress(address: String) {
        _inputAddress.value = address
        _addressError.value = null
        _saveSuccess.value = false
    }

    /**
     * 保存自定义 IP 地址
     * @return true 表示验证通过并已保存
     */
    fun saveAddress(): Boolean {
        val input = _inputAddress.value.trim()

        if (input.isEmpty()) {
            // 空输入表示清除自定义地址，使用默认值
            settingsPreferences.setBaseUrl(null)
            _addressError.value = null
            _saveSuccess.value = true
            return true
        }

        val fullUrl = "http://$input"
        if (!isValidUrl(fullUrl)) {
            _addressError.value = "地址格式无效，示例：192.168.1.100:8001"
            return false
        }

        settingsPreferences.setBaseUrl(fullUrl)
        _addressError.value = null
        _saveSuccess.value = true
        return true
    }

    /**
     * 重置保存成功提示
     */
    fun clearSaveSuccess() {
        _saveSuccess.value = false
    }

    /**
     * 重置连接测试状态
     */
    fun resetConnectionStatus() {
        _connectionStatus.value = ConnectionStatus.Idle
    }

    /**
     * 验证 URL 格式
     */
    private fun isValidUrl(url: String): Boolean {
        return try {
            val uri = java.net.URI(url)
            val host = uri.host ?: return false
            val port = uri.port

            // 验证 IP 格式 (简单检查：xxx.xxx.xxx.xxx)
            val ipPattern = Regex("^\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}$")
            val isIpValid = ipPattern.matches(host) && host.split(".").all { octet ->
                octet.toIntOrNull()?.let { it in 0..255 } ?: false
            }

            // 或者是 localhost / 域名
            val isHostValid = isIpValid || host == "localhost" || host.contains(".")

            // 端口验证
            val isPortValid = port == -1 || port in 1..65535

            isHostValid && isPortValid
        } catch (e: Exception) {
            false
        }
    }

    /**
     * 从完整 URL 中提取 host:port 部分
     */
    private fun extractAddress(fullUrl: String): String {
        return try {
            val uri = java.net.URI(fullUrl)
            val host = uri.host ?: return ""
            val port = uri.port
            if (port > 0) "$host:$port" else host
        } catch (e: Exception) {
            ""
        }
    }
}
