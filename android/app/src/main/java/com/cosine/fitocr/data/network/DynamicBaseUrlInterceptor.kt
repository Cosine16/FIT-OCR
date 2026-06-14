package com.cosine.fitocr.data.network

import com.cosine.fitocr.data.preferences.SettingsPreferences
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 动态 BaseUrl 拦截器
 * 在请求发出前，将 URL 的 host/port 替换为用户自定义的地址
 * 这样用户修改 IP 后无需重建 Retrofit 实例，立即生效
 */
@Singleton
class DynamicBaseUrlInterceptor @Inject constructor(
    private val settingsPreferences: SettingsPreferences
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val customBaseUrl = settingsPreferences.getBaseUrl()

        return if (customBaseUrl != null) {
            val customUrl = customBaseUrl.toHttpUrl()
            val originalUrl = originalRequest.url

            val newUrl = originalUrl.newBuilder()
                .scheme(customUrl.scheme)
                .host(customUrl.host)
                .port(customUrl.port)
                .build()

            val newRequest = originalRequest.newBuilder()
                .url(newUrl)
                .build()

            chain.proceed(newRequest)
        } else {
            chain.proceed(originalRequest)
        }
    }
}
