package com.cosine.fitocr.data.preferences

import android.content.Context
import android.content.SharedPreferences
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 应用设置持久化管理
 * 使用 SharedPreferences 存储自定义后端地址，支持运行时动态修改
 */
@Singleton
class SettingsPreferences @Inject constructor(
    @ApplicationContext context: Context
) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("fit_ocr_settings", Context.MODE_PRIVATE)

    private val _customBaseUrl = MutableStateFlow(
        prefs.getString(KEY_BASE_URL, null)
    )
    val customBaseUrl: StateFlow<String?> = _customBaseUrl.asStateFlow()

    fun getBaseUrl(): String? = prefs.getString(KEY_BASE_URL, null)

    fun setBaseUrl(url: String?) {
        prefs.edit().apply {
            if (url == null) {
                remove(KEY_BASE_URL)
            } else {
                putString(KEY_BASE_URL, url)
            }
            apply()
        }
        _customBaseUrl.value = url
    }

    companion object {
        private const val KEY_BASE_URL = "custom_base_url"
    }
}
