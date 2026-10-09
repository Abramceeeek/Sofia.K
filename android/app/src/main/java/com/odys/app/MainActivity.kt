package com.odys.app

import android.content.Intent
import android.graphics.Color as AndroidColor
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.SystemBarStyle
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner

class MainActivity : ComponentActivity() {
    private val model: AppModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge(
            statusBarStyle = SystemBarStyle.dark(AndroidColor.TRANSPARENT),
            navigationBarStyle = SystemBarStyle.dark(AndroidColor.TRANSPARENT),
        )
        super.onCreate(savedInstanceState)
        model.reminders.channel()
        handle(intent)
        lifecycle.addObserver(object : DefaultLifecycleObserver {
            // each time the app comes to the front, start waking the free server (it sleeps after 15 min)
            override fun onResume(owner: LifecycleOwner) {
                model.onResume()
                model.location.refresh()
            }

            override fun onPause(owner: LifecycleOwner) {
                model.location.stop()
            }
        })
        setContent { RootView(model) }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handle(intent)
    }

    /** A share link (daysout://r/<code>), or a tapped rating reminder (opens that stop). */
    private fun handle(intent: Intent?) {
        intent ?: return
        intent.data?.let { model.openLink(it) }
        intent.getStringExtra("momentId")?.let { model.openStop(it) }
    }
}
