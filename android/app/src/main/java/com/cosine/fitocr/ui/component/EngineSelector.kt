package com.cosine.fitocr.ui.component

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.cosine.fitocr.domain.model.OcrEngine

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun EngineSelector(
    selectedEngine: OcrEngine,
    onEngineChanged: (OcrEngine) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }
    val arrowRotation by androidx.compose.animation.core.animateFloatAsState(
        targetValue = if (expanded) 180f else 0f,
        label = "arrowRotation"
    )

    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = "识别引擎",
                style = MaterialTheme.typography.labelLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Spacer(modifier = Modifier.height(8.dp))

            ExposedDropdownMenuBox(
                expanded = expanded,
                onExpandedChange = { expanded = !expanded },
                modifier = Modifier.fillMaxWidth()
            ) {
                OutlinedTextField(
                    value = selectedEngine.displayName,
                    onValueChange = {},
                    readOnly = true,
                    textStyle = MaterialTheme.typography.bodyLarge.copy(
                        fontWeight = FontWeight.Medium
                    ),
                    trailingIcon = {
                        Icon(
                            imageVector = Icons.Filled.KeyboardArrowDown,
                            contentDescription = null,
                            modifier = Modifier.rotate(arrowRotation),
                            tint = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    },
                    colors = ExposedDropdownMenuDefaults.outlinedTextFieldColors(
                        focusedContainerColor = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.3f),
                        unfocusedContainerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                        focusedBorderColor = MaterialTheme.colorScheme.primary,
                        unfocusedBorderColor = MaterialTheme.colorScheme.outlineVariant
                    ),
                    shape = RoundedCornerShape(12.dp),
                    modifier = Modifier
                        .fillMaxWidth()
                        .menuAnchor()
                )

                ExposedDropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    OcrEngine.entries.forEach { engine ->
                        val isSelected = engine == selectedEngine
                        val containerColor by animateColorAsState(
                            targetValue = if (isSelected) {
                                MaterialTheme.colorScheme.primaryContainer
                            } else {
                                MaterialTheme.colorScheme.surface
                            },
                            label = "engineItemColor"
                        )

                        DropdownMenuItem(
                            text = {
                                Row(
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Start
                                ) {
                                    EngineIcon(engine = engine)
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Column {
                                        Text(
                                            text = engine.displayName,
                                            style = MaterialTheme.typography.bodyLarge,
                                            fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                                        )
                                        Text(
                                            text = engineDescription(engine),
                                            style = MaterialTheme.typography.bodySmall,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                            },
                            onClick = {
                                onEngineChanged(engine)
                                expanded = false
                            },
                            modifier = Modifier.fillMaxWidth(),
                            leadingIcon = if (isSelected) {
                                {
                                    Surface(
                                        shape = RoundedCornerShape(8.dp),
                                        color = MaterialTheme.colorScheme.primary,
                                        modifier = Modifier.size(8.dp)
                                    ) {}
                                }
                            } else null
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun EngineIcon(engine: OcrEngine, modifier: Modifier = Modifier) {
    val (emoji, bgColor) = when (engine) {
        OcrEngine.LOCAL -> "\uD83D\uDCDA" to MaterialTheme.colorScheme.tertiaryContainer
        OcrEngine.CLOUD -> "\u2601" to MaterialTheme.colorScheme.secondaryContainer
        OcrEngine.FALLBACK -> "\uD83E\uDD16" to MaterialTheme.colorScheme.primaryContainer
    }

    Surface(
        shape = RoundedCornerShape(10.dp),
        color = bgColor,
        modifier = modifier.size(40.dp)
    ) {
        Box(contentAlignment = Alignment.Center) {
            Text(
                text = emoji,
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}

private fun engineDescription(engine: OcrEngine): String = when (engine) {
    OcrEngine.LOCAL -> "本地模型识别，无需联网"
    OcrEngine.CLOUD -> "云端大模型，精度更高"
    OcrEngine.FALLBACK -> "优先本地，失败时自动切换云端"
}
