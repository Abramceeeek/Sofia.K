package com.odys.app

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import androidx.activity.compose.BackHandler
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawing
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.windowInsetsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import android.app.Activity
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties

@Composable
fun RootView(model: AppModel) {
    // D130 (Daylight): the system's own parts (dialogs, the status bar's icons) follow the day or night colours
    val view = LocalView.current
    val day = Theme.day
    SideEffect {
        (view.context as? Activity)?.window?.let { window ->
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = day
                isAppearanceLightNavigationBars = day
            }
        }
    }
    MaterialTheme(
        colorScheme = if (day) lightColorScheme(
            primary = Theme.accent, onPrimary = Theme.onAccent, background = Theme.background,
            surface = Theme.surface, onSurface = Theme.ink, onBackground = Theme.ink, surfaceVariant = Theme.surfaceHigh,
            secondary = Theme.accent, outline = Theme.outlineStrong,
        ) else darkColorScheme(
            primary = Theme.accent, onPrimary = Theme.onAccent, background = Theme.background,
            surface = Theme.surface, onSurface = Theme.ink, onBackground = Theme.ink, surfaceVariant = Theme.surfaceHigh,
            secondary = Theme.accent, outline = Theme.outlineStrong,
        ),
    ) {
        Box(Modifier.screen()) {
            when (model.route) {
                Route.Welcome -> WelcomeView(model)
                Route.Example -> ExampleDayView(model)
                Route.Consent -> ConsentView(model)
                Route.Onboarding -> OnboardingView(model)
                Route.Home -> LivingHome(model)
            }
            AnimatedVisibility(model.waking, Modifier.align(Alignment.TopCenter).statusBarsPadding(),
                enter = fadeIn(), exit = fadeOut()) { WakingBanner() }
        }
        Feedback(model)
    }
}

/** Errors and notices, as alerts above everything (sheets included). */
@Composable
fun Feedback(model: AppModel) {
    val error = model.errorMessage
    val notice = model.notice
    if (error != null) {
        OdysAlert("Something went wrong", error) { model.errorMessage = null }
    } else if (notice != null) {
        OdysAlert(notice.first, notice.second) { model.notice = null }
    }
}

@Composable
fun OdysAlert(title: String, text: String, onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = { TextButton(onDismiss) { Text("OK", color = Theme.accent) } },
        title = { Text(title, style = Theme.headline) },
        text = { Text(text, style = Theme.body.copy(color = Theme.inkSoft)) },
        containerColor = Theme.surfaceHigh,
    )
}

/** A choice to confirm ("Swap it" / "Keep it"), as iOS's confirmation dialogs. */
@Composable
fun ConfirmDialog(
    title: String,
    text: String?,
    confirm: String,
    cancel: String,
    destructive: Boolean = false,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit,
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            TextButton({ onDismiss(); onConfirm() }) {
                Text(confirm, color = if (destructive) Theme.dangerInk else Theme.accent, fontWeight = FontWeight.SemiBold)
            }
        },
        dismissButton = { TextButton(onDismiss) { Text(cancel, color = Theme.inkSoft) } },
        title = { Text(title, style = Theme.headline) },
        text = text?.let { { Text(it, style = Theme.body.copy(color = Theme.inkSoft)) } },
        containerColor = Theme.surfaceHigh,
    )
}

/** A choice of several (a menu of answers), as iOS's action sheets. */
@Composable
fun ChoiceDialog(title: String, text: String?, options: List<Pair<String, () -> Unit>>, cancel: String = "Cancel",
                 onDismiss: () -> Unit) {
    AlertDialog(
        onDismissRequest = onDismiss,
        confirmButton = {
            Column(horizontalAlignment = Alignment.End) {
                for ((label, action) in options) {
                    TextButton({ onDismiss(); action() }) { Text(label, color = Theme.accent) }
                }
                TextButton(onDismiss) { Text(cancel, color = Theme.inkSoft) }
            }
        },
        title = { Text(title, style = Theme.headline) },
        text = text?.let { { Text(it, style = Theme.body.copy(color = Theme.inkSoft)) } },
        containerColor = Theme.surfaceHigh,
    )
}

/**
 * A full-screen sheet (iOS's page sheets): its own window, so it sits above the tabs; the back gesture closes it.
 * The "waking up" note shows inside it too.
 */
@Composable
fun FullSheet(model: AppModel, onDismiss: () -> Unit, color: androidx.compose.ui.graphics.Color = Theme.background,
              content: @Composable BoxScope.() -> Unit) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false, decorFitsSystemWindows = false),
    ) {
        Box(Modifier.fillMaxSize().background(color).windowInsetsPadding(WindowInsets.safeDrawing)) {
            content()
            AnimatedVisibility(model.waking, Modifier.align(Alignment.TopCenter), enter = fadeIn(), exit = fadeOut()) {
                WakingBanner()
            }
        }
    }
}

/** A sheet's top row: a title on the left (optional), "Close" on the right. */
@Composable
fun SheetBar(title: String? = null, close: String = "Close", leading: (@Composable () -> Unit)? = null,
             onClose: () -> Unit) {
    Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp).heightIn(min = 48.dp),
        verticalAlignment = Alignment.CenterVertically) {
        if (leading != null) leading()
        Box(Modifier.weight(1f), contentAlignment = Alignment.Center) {
            if (title != null) Text(title, style = Theme.serif(19.sp), maxLines = 1)
        }
        CloseLink(close, onClose)
    }
}

/** A scrolling page with the app's side margins, and room for the bottom bar. */
@Composable
fun ScrollPage(modifier: Modifier = Modifier, spacing: Int = 20, top: Int = 8, bottom: Int = 32,
               content: @Composable ColumnScope.() -> Unit) {
    Column(
        modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(horizontal = 24.dp)
            .padding(top = top.dp, bottom = bottom.dp),
        verticalArrangement = Arrangement.spacedBy(spacing.dp),
        content = content,
    )
}

/** A page that fills the screen, with its main action pinned at the bottom (iOS's safeAreaInset). */
@Composable
fun PageWithBottom(
    modifier: Modifier = Modifier,
    spacing: Int = 20,
    bottom: @Composable ColumnScope.() -> Unit,
    content: @Composable ColumnScope.() -> Unit,
) {
    Column(modifier.fillMaxSize().imePadding()) {
        Column(
            Modifier.weight(1f).fillMaxWidth().verticalScroll(rememberScrollState()).padding(horizontal = 24.dp)
                .padding(top = 8.dp, bottom = 16.dp),
            verticalArrangement = Arrangement.spacedBy(spacing.dp),
            content = content,
        )
        Column(Modifier.fillMaxWidth().background(Theme.background).padding(horizontal = 24.dp)
            .padding(top = 8.dp, bottom = 8.dp), content = bottom)
    }
}

/** Opens a link in the browser or the app that handles it (Maps, the dialler). */
fun openUrl(context: Context, url: String) {
    try {
        context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url)).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    } catch (e: ActivityNotFoundException) {
        // nothing on this phone can open it
    }
}

/** Google Maps directions to a point (the Android counterpart of "Directions in Apple Maps"). */
fun directionsUrl(pin: Point, transit: Boolean): String =
    "https://www.google.com/maps/dir/?api=1&destination=${pin.lat},${pin.lon}&travelmode=${if (transit) "transit" else "walking"}"

/** The system back closes the top thing: used where the screen has its own "‹ Back". */
@Composable
fun BackTo(enabled: Boolean = true, onBack: () -> Unit) = BackHandler(enabled, onBack)

@Composable
fun Gap(h: Int) = Spacer(Modifier.heightIn(min = h.dp))
