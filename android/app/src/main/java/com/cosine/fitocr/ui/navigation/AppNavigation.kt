package com.cosine.fitocr.ui.navigation

import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.cosine.fitocr.ui.screen.OcrScreen

sealed class Screen(val route: String) {
    object Ocr : Screen("ocr")
}

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = Screen.Ocr.route,
        enterTransition = {
            fadeIn(animationSpec = tween(400)) +
            slideInHorizontally(animationSpec = tween(400)) { it / 4 }
        },
        exitTransition = {
            fadeOut(animationSpec = tween(300))
        },
        popEnterTransition = {
            fadeIn(animationSpec = tween(400)) +
            slideInHorizontally(animationSpec = tween(400)) { it / 4 }
        },
        popExitTransition = {
            fadeOut(animationSpec = tween(300)) +
            slideOutHorizontally(animationSpec = tween(300)) { it / 4 }
        }
    ) {
        composable(
            route = Screen.Ocr.route,
            enterTransition = { fadeIn(animationSpec = tween(500)) },
            exitTransition = { fadeOut(animationSpec = tween(300)) }
        ) {
            OcrScreen()
        }
    }
}
