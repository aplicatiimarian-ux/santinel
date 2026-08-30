// SANTINEL Android Audio Recording Service
// Background service for audio recording

package com.santinel.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.media.MediaRecorder
import android.os.Binder
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import java.io.File
import java.text.SimpleDateFormat
import java.util.*

class AudioRecordingService : Service() {
    private var mediaRecorder: MediaRecorder? = null
    private var isRecording = false
    private val binder = LocalBinder()
    private var recordingFile: File? = null

    companion object {
        const val CHANNEL_ID = "AudioRecordingChannel"
        const val NOTIFICATION_ID = 1
    }

    inner class LocalBinder : Binder() {
        fun getService(): AudioRecordingService = this@AudioRecordingService
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val action = intent?.action ?: return START_STICKY

        when (action) {
            "START_RECORDING" -> startAudioRecording()
            "STOP_RECORDING" -> stopAudioRecording()
        }

        return START_STICKY
    }

    override fun onBind(intent: Intent): IBinder {
        return binder
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Audio Recording",
                NotificationManager.IMPORTANCE_LOW
            )
            channel.description = "Notification for background audio recording"
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("SANTINEL Recording")
            .setContentText("Recording negotiation audio...")
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .build()
    }

    private fun startAudioRecording() {
        if (isRecording) return

        try {
            val filename = "call_${System.currentTimeMillis()}.m4a"
            recordingFile = File(getExternalFilesDir(null), filename)

            mediaRecorder = MediaRecorder().apply {
                setAudioSource(MediaRecorder.AudioSource.MIC)
                setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
                setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                setAudioSamplingRate(16000)
                setAudioChannels(1)
                setAudioEncodingBitRate(128000)
                setOutputFile(recordingFile?.absolutePath)
                prepare()
                start()
            }

            isRecording = true
            startForeground(NOTIFICATION_ID, createNotification())
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun stopAudioRecording() {
        if (!isRecording) return

        try {
            mediaRecorder?.apply {
                stop()
                release()
            }
            mediaRecorder = null
            isRecording = false
            stopForeground(STOP_FOREGROUND_REMOVE)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    fun getRecordingFile(): File? = recordingFile

    fun isRecording(): Boolean = isRecording

    override fun onDestroy() {
        super.onDestroy()
        if (isRecording) {
            stopAudioRecording()
        }
    }
}
