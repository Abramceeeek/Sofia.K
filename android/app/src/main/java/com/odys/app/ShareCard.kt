package com.odys.app

import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.ClipData
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.LinearGradient
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.RectF
import android.graphics.Shader
import android.graphics.Typeface
import android.os.Build
import android.text.Layout
import android.text.StaticLayout
import android.text.TextPaint
import android.text.TextUtils
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.core.content.FileProvider
import androidx.core.content.res.ResourcesCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.File
import java.net.URLEncoder

/**
 * D114, D119: the card a person can share after rating a stop, in the ODYS cream (app/Sources/ShareCard.swift): the
 * moment's photo with the word they rated it, "A moment from my day", the title, their reason (D127: optional), and "Planned with
 * ODYS". Never the model's "worth £X". No rewards. The photo is openly licensed, so its credit goes on the card.
 * Drawn at 1080 × 1350, the same as the iPhone's, so the picture is the same wherever it's sent.
 */
object ShareCard {
    private const val W = 1080
    private const val H = 1350
    private const val PHOTO_H = 708          // 236 × 3
    private const val PAD = 60f              // 20 × 3

    fun render(context: Context, stop: Stop, rating: Int, reason: Boolean = true): Bitmap {
        val out = Bitmap.createBitmap(W, H, Bitmap.Config.ARGB_8888)
        val c = Canvas(out)
        val serif = ResourcesCompat.getFont(context, R.font.newsreader) ?: Typeface.SERIF
        val italic = ResourcesCompat.getFont(context, R.font.newsreader_italic) ?: Typeface.create(Typeface.SERIF, Typeface.ITALIC)
        c.drawColor(Theme.cream.toArgb())

        // the picture: the card's photo, cropped to fill, or a warm field
        val found = CardPhotos.photo(context, stop.momentId)
        val photoRect = Rect(0, 0, W, PHOTO_H)
        if (found != null) {
            val bmp = found.second
            val scale = maxOf(W.toFloat() / bmp.width, PHOTO_H.toFloat() / bmp.height)
            val sw = (W / scale).toInt()
            val sh = (PHOTO_H / scale).toInt()
            val sx = (bmp.width - sw) / 2
            val sy = (bmp.height - sh) / 2
            c.drawBitmap(bmp, Rect(sx, sy, sx + sw, sy + sh), photoRect, Paint(Paint.FILTER_BITMAP_FLAG or Paint.ANTI_ALIAS_FLAG))
        } else {
            c.drawRect(photoRect, Paint().apply {
                shader = LinearGradient(0f, 0f, 0f, PHOTO_H.toFloat(), 0xFFE7B77A.toInt(), 0xFF3B2A1E.toInt(), Shader.TileMode.CLAMP)
            })
        }

        // their own rating, as a word
        val word = Labels.feel[(rating - 1).coerceIn(0, 4)]
        val tag = TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            typeface = italic
            textSize = 45f
            color = Theme.accent.toArgb()
        }
        val tagText = "Rated: $word"
        val tw = tag.measureText(tagText)
        val pill = RectF(48f, 48f, 48f + tw + 72f, 48f + 90f)
        c.drawRoundRect(pill, 45f, 45f, Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Theme.creamInk.copy(alpha = 0.62f).toArgb() })
        c.drawText(tagText, pill.left + 36f, pill.centerY() + 15f, tag)

        // the cream half
        var y = PHOTO_H + PAD
        val width = (W - 2 * PAD).toInt()
        y += draw(c, "A moment from my day", TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            textSize = 42f
            color = Theme.creamSoft.toArgb()
        }, width, y, 1) + 24f
        y += draw(c, stop.title, TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            typeface = serif
            textSize = 75f
            color = Theme.creamInk.toArgb()
        }, width, y, 3) + 24f
        stop.reasons?.mapNotNull { it.me }?.firstOrNull()?.takeIf { reason }?.let { why ->
            // D115: the plain-language reason, from the sharer's answers (journey round 2: not a quote)
            draw(c, why, TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
                typeface = italic
                textSize = 51f
                color = Theme.creamQuote.toArgb()
            }, width, y, 3)
        }

        // the foot: the arch and "Planned with ODYS", then the photo's credit
        val credit = found?.first?.let { "Photo: ${it.author}, ${it.licence}, Wikimedia Commons (cropped)" }
        val footY = H - PAD - (if (credit != null) 66f else 0f)
        val glyph = android.graphics.Path().apply {
            val gx = PAD
            val gw = 30f
            val gh = gw * 18f / 14f
            val top = footY - gh + 6f
            moveTo(gx, top + gh)
            lineTo(gx, top + gw / 2)
            arcTo(RectF(gx, top, gx + gw, top + gw), 180f, 180f)
            lineTo(gx + gw, top + gh)
            close()
        }
        c.drawPath(glyph, Paint(Paint.ANTI_ALIAS_FLAG).apply { color = Theme.amberDeep.toArgb() })
        c.drawText("Planned with ODYS", PAD + 54f, footY, TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
            textSize = 39f
            color = Theme.creamSoft.toArgb()
        })
        if (credit != null) {
            draw(c, credit, TextPaint(Paint.ANTI_ALIAS_FLAG).apply {
                textSize = 24f
                color = Theme.creamSoft.toArgb()
            }, width, footY + 24f, 2)
        }
        return out
    }

    /** Draws wrapped text at `y`; returns its height. */
    private fun draw(c: Canvas, text: String, paint: TextPaint, width: Int, y: Float, maxLines: Int): Float {
        val layout = StaticLayout.Builder.obtain(text, 0, text.length, paint, width)
            .setAlignment(Layout.Alignment.ALIGN_NORMAL)
            .setMaxLines(maxLines)
            .setEllipsize(TextUtils.TruncateAt.END)
            .build()
        c.save()
        c.translate(PAD, y)
        layout.draw(c)
        c.restore()
        return layout.height.toFloat()
    }

    /** The card and the person's link through Android's share sheet. Which app they picked is the funnel's "shared". */
    suspend fun share(context: Context, model: AppModel, stop: Stop, reason: Boolean = true) {
        val rating = model.myRatings[stop.momentId] ?: return
        val referral = model.referral() ?: return
        val moment = CardPhotos.cardId(stop.momentId) ?: stop.momentId
        val link = AppConfig.BASE_URL.trimEnd('/') + "/r/" + referral.code + "?m=" + URLEncoder.encode(moment, "UTF-8")
        val file = withContext(Dispatchers.IO) {
            val dir = File(context.cacheDir, "share").apply { mkdirs() }
            File(dir, "odys-moment.png").also { f ->
                f.outputStream().use { render(context, stop, rating, reason).compress(Bitmap.CompressFormat.PNG, 100, it) }
            }
        }
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.files", file)
        val send = Intent(Intent.ACTION_SEND).apply {
            type = "image/png"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_TEXT, "${referral.text}: $link")
            clipData = ClipData.newRawUri(null, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        val picked = PendingIntent.getBroadcast(context, 0,
            Intent(context, ShareReceiver::class.java).putExtra("moment", stop.momentId),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE)
        model.client.event("share_sheet", mapOf("moment" to stop.momentId, "rating" to "$rating", "reason" to if (reason) "1" else "0"))
        context.startActivity(Intent.createChooser(send, "Share this moment", picked.intentSender)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK))
    }
}

/**
 * Android tells the app which app a share went to (not whether it was then sent, as the iPhone does), so "shared"
 * here means a person picked an app to send it with.
 */
class ShareReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val chosen: ComponentName? = if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(Intent.EXTRA_CHOSEN_COMPONENT, ComponentName::class.java)
        } else {
            @Suppress("DEPRECATION") intent.getParcelableExtra(Intent.EXTRA_CHOSEN_COMPONENT)
        }
        val moment = intent.getStringExtra("moment") ?: ""
        val pending = goAsync()
        val app = context.applicationContext
        CoroutineScope(Dispatchers.IO).launch {
            runCatching {
                BrainClient(AppConfig.BASE_URL, TokenStore(app))
                    .event("share_sent", mapOf("moment" to moment, "to" to (chosen?.packageName ?: "")))
            }
            pending.finish()
        }
    }
}

/** D114, D119: the share card before it's sent. Their rating and their reason go with it, never "worth £X". */
@Composable
fun SharePreview(model: AppModel, stop: Stop, rating: Int, onClose: () -> Unit) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var reason by remember { mutableStateOf(true) }
    val hasReason = stop.reasons?.any { it.me != null } == true
    val card = remember(stop.momentId, rating, reason) { ShareCard.render(context, stop, rating, reason) }
    FullSheet(model, onClose) {
        Column(Modifier.fillMaxSize()) {
            SheetBar("Share this moment", onClose = onClose)
            ScrollPage(spacing = 18, top = 8, bottom = 24) {
                Image(card.asImageBitmap(), contentDescription = "The card: ${stop.title}, rated ${Labels.feel[(rating - 1).coerceIn(0, 4)]}",
                    modifier = Modifier.fillMaxWidth().aspectRatio(1080f / 1350f).settle(0)
                        .shadow(24.dp, RoundedCornerShape(26.dp)).clip(RoundedCornerShape(26.dp)))
                if (hasReason) {   // D127: the reason is worded by ODYS from their answers, so it's theirs to leave out
                    FilterSwitch("Include the line about why", "Worded by ODYS from your answers", reason) { reason = it }
                }
                Text(if (reason && hasReason) "Your rating and the line about why go with it, and nothing else about you."
                     else "Your rating goes with it, and nothing else about you.",
                    style = Theme.footnote, textAlign = TextAlign.Center, modifier = Modifier.fillMaxWidth())
                Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    PrimaryButton(if (model.busy) "One moment…" else "Send to a friend", enabled = !model.busy) {
                        scope.launch { ShareCard.share(context, model, stop, reason) }
                    }
                    SecondaryButton("Not now", onClick = onClose)
                }
            }
        }
    }
}
