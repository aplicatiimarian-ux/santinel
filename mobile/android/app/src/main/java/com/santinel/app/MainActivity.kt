package com.santinel.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.santinel.app.ui.theme.SANTINELTheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.net.HttpURLConnection
import java.net.URL
import java.net.URLEncoder

/**
 * SANTINEL — mobile client.
 *
 * Sends the negotiation text to the SANTINEL API (`/analyze`) and renders the
 * 10-framework coaching read-out: close probability, top frameworks, and a
 * finding + confidence + suggestion per framework. Bilingual EN / RO.
 *
 * The API base defaults to 10.0.2.2:8000 — the host loopback as seen from the
 * Android emulator. Change [API_BASE] for a device / real deployment.
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            SANTINELTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    SantinelApp()
                }
            }
        }
    }
}

private const val API_BASE = "http://10.0.2.2:8000"

private val FRAMEWORK_LABELS = mapOf(
    "cbt" to ("CBT" to "TCC"),
    "nlp" to ("NLP" to "PNL"),
    "ta" to ("Transactional Analysis" to "Analiză Tranzacțională"),
    "ei" to ("Emotional Intelligence" to "Inteligență Emoțională"),
    "attachment" to ("Attachment" to "Atașament"),
    "behavioral_econ" to ("Behavioral Economics" to "Economie Comportamentală"),
    "game_theory" to ("Game Theory" to "Teoria Jocurilor"),
    "neuroscience" to ("Neuroscience" to "Neuroștiință"),
    "narrative" to ("Narrative" to "Narativ"),
    "somatic" to ("Somatic" to "Somatic"),
)

private data class FrameworkInsight(
    val key: String,
    val finding: String,
    val confidence: Int,
    val suggestion: String,
    val triggered: Boolean,
)

private data class AnalysisResult(
    val closeProbability: Int,
    val topFrameworks: List<String>,
    val coaching: String,
    val frameworks: List<FrameworkInsight>,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SantinelApp() {
    var lang by remember { mutableStateOf("en") }
    var text by remember {
        mutableStateOf(
            "Lead: \"I'm interested but the price is too high\"\n" +
                "You: \"I understand cost is important. Let me show you the ROI...\""
        )
    }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var result by remember { mutableStateOf<AnalysisResult?>(null) }
    val scope = rememberCoroutineScope()

    fun analyze() {
        if (text.isBlank()) {
            error = if (lang == "en") "Please enter text" else "Introdu un text"
            return
        }
        loading = true
        error = null
        scope.launch {
            try {
                result = withContext(Dispatchers.IO) { requestAnalysis(text.trim()) }
            } catch (e: Exception) {
                error = (if (lang == "en") "Error: " else "Eroare: ") + (e.message ?: e.toString())
                result = null
            } finally {
                loading = false
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text("SANTINEL", fontWeight = FontWeight.Black, letterSpacing = 3.sp)
                },
                actions = {
                    TextButton(onClick = { lang = if (lang == "en") "ro" else "en" }) {
                        Text(if (lang == "en") "RO" else "EN")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                )
            )
        }
    ) { inner ->
        Column(
            modifier = Modifier
                .padding(inner)
                .fillMaxSize()
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                if (lang == "en") "Analyze Negotiation" else "Analizează Negocierea",
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.Bold,
            )

            OutlinedTextField(
                value = text,
                onValueChange = { text = it },
                modifier = Modifier.fillMaxWidth(),
                label = {
                    Text(if (lang == "en") "Negotiation text" else "Textul negocierii")
                },
                minLines = 4,
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Default),
            )

            Button(
                onClick = { analyze() },
                enabled = !loading,
                modifier = Modifier.fillMaxWidth()
            ) {
                if (loading) {
                    CircularProgressIndicator(
                        modifier = Modifier.height(18.dp),
                        strokeWidth = 2.dp,
                        color = MaterialTheme.colorScheme.onPrimary,
                    )
                    Spacer(Modifier.height(0.dp))
                    Text("  " + if (lang == "en") "Analyzing…" else "Se analizează…")
                } else {
                    Text(
                        if (lang == "en") "ANALYZE WITH ALL 10 FRAMEWORKS"
                        else "ANALIZEAZĂ CU TOATE CELE 10 FRAMEWORK-URI"
                    )
                }
            }

            error?.let {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Text(it, modifier = Modifier.padding(14.dp), color = MaterialTheme.colorScheme.error)
                }
            }

            result?.let { r -> ResultView(r, lang) }

            if (result == null && error == null && !loading) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            if (lang == "en") "How it works" else "Cum funcționează",
                            fontWeight = FontWeight.Bold,
                        )
                        Text(
                            if (lang == "en")
                                "Paste a negotiation exchange, run the analysis across all ten " +
                                    "psychology frameworks, and review the coaching read-out."
                            else
                                "Lipește un schimb de replici, rulează analiza pe toate cele zece " +
                                    "framework-uri și parcurge recomandările.",
                            fontSize = 13.sp,
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ResultView(r: AnalysisResult, lang: String) {
    val probColor = when {
        r.closeProbability < 5 -> MaterialTheme.colorScheme.error
        r.closeProbability < 8 -> MaterialTheme.colorScheme.tertiary
        else -> MaterialTheme.colorScheme.primary
    }

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    "${r.closeProbability}",
                    fontSize = 44.sp,
                    fontWeight = FontWeight.Black,
                    color = probColor,
                )
                Text(
                    "  / 10  " + (if (lang == "en") "close probability" else "probabilitate de închidere"),
                    fontSize = 13.sp,
                )
            }
            if (r.topFrameworks.isNotEmpty()) {
                Text(
                    (if (lang == "en") "Top frameworks: " else "Framework-uri principale: ") +
                        r.topFrameworks.joinToString(", ") { labelFor(it, lang) },
                    fontSize = 13.sp,
                    fontWeight = FontWeight.SemiBold,
                )
            }
            if (r.coaching.isNotBlank()) {
                Text(r.coaching, fontSize = 14.sp)
            }
        }
    }

    Spacer(Modifier.height(4.dp))

    r.frameworks.forEach { fw ->
        Card(modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                Text(labelFor(fw.key, lang), fontWeight = FontWeight.Bold)
                Text(fw.finding, fontWeight = FontWeight.SemiBold, fontSize = 15.sp)
                @Suppress("DEPRECATION")
                LinearProgressIndicator(
                    progress = fw.confidence / 100f,
                    modifier = Modifier.fillMaxWidth(),
                )
                Text(
                    (if (lang == "en") "Confidence: " else "Încredere: ") + "${fw.confidence}%",
                    fontSize = 12.sp,
                )
                if (fw.suggestion.isNotBlank()) {
                    Text("💡 " + fw.suggestion, fontSize = 13.sp)
                }
            }
        }
    }
}

private fun labelFor(key: String, lang: String): String {
    val pair = FRAMEWORK_LABELS[key] ?: return key
    return if (lang == "en") pair.first else pair.second
}

private fun requestAnalysis(text: String): AnalysisResult {
    val url = URL("$API_BASE/analyze?text=" + URLEncoder.encode(text, "UTF-8"))
    val conn = (url.openConnection() as HttpURLConnection).apply {
        requestMethod = "GET"
        connectTimeout = 10_000
        readTimeout = 15_000
        setRequestProperty("Accept", "application/json")
    }
    try {
        val code = conn.responseCode
        val body = (if (code in 200..299) conn.inputStream else conn.errorStream)
            .bufferedReader().use { it.readText() }
        if (code !in 200..299) throw RuntimeException("HTTP $code")
        return parseAnalysis(body)
    } finally {
        conn.disconnect()
    }
}

/** Handles both the bilingual (`{en,ro}`) and the flat-string API shapes. */
private fun parseAnalysis(json: String): AnalysisResult {
    val root = JSONObject(json)
    root.optString("error").takeIf { it.isNotBlank() }?.let { throw RuntimeException(it) }

    fun localized(value: Any?): String = when (value) {
        null -> ""
        is JSONObject -> value.optString("en", value.optString("ro", ""))
        else -> value.toString()
    }

    val fwObj = root.optJSONObject("frameworks") ?: JSONObject()
    val order = root.optJSONArray("frameworks_order")
    val keys: List<String> = if (order != null) {
        (0 until order.length()).map { order.getString(it) }
    } else {
        fwObj.keys().asSequence().toList()
    }

    val frameworks = keys.mapNotNull { key ->
        val f = fwObj.optJSONObject(key) ?: return@mapNotNull null
        val confRaw = f.opt("confidence")
        val conf = when (confRaw) {
            is Number -> {
                val d = confRaw.toDouble()
                if (d <= 1.0) (d * 100).toInt() else d.toInt()
            }
            else -> 0
        }
        FrameworkInsight(
            key = key,
            finding = localized(f.opt("primary_finding")),
            confidence = conf.coerceIn(0, 100),
            suggestion = localized(f.opt("suggestion")),
            triggered = f.optBoolean("triggered", false),
        )
    }

    val top = root.optJSONArray("top_frameworks")
    val topList = if (top != null) (0 until top.length()).map { top.getString(it) } else emptyList()

    return AnalysisResult(
        closeProbability = root.optInt("close_probability", 0),
        topFrameworks = topList,
        coaching = localized(root.opt("coaching")),
        frameworks = frameworks,
    )
}

@Preview(showBackground = true)
@Composable
private fun SantinelPreview() {
    SANTINELTheme { SantinelApp() }
}
