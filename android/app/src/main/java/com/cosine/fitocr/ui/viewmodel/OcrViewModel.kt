package com.cosine.fitocr.ui.viewmodel

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.cosine.fitocr.data.repository.OcrRepository
import com.cosine.fitocr.domain.model.OcrEngine
import com.cosine.fitocr.domain.model.OcrUiState
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class OcrViewModel @Inject constructor(
    private val repository: OcrRepository
) : ViewModel() {

    val uiState: StateFlow<OcrUiState> = repository.uiState

    private var recognizeJob: Job? = null

    fun recognizeImage(uri: Uri, engine: OcrEngine) {
        if (recognizeJob?.isActive == true) {
            recognizeJob?.cancel()
        }
        recognizeJob = viewModelScope.launch {
            repository.recognizeImage(uri, engine)
        }
    }

    fun resetState() {
        recognizeJob?.cancel()
        repository.resetState()
    }

    override fun onCleared() {
        super.onCleared()
        recognizeJob?.cancel()
    }
}
