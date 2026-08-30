// SANTINEL Android Models

package com.santinel.models

import java.util.UUID

data class User(
    val id: String,
    val email: String,
    val name: String
)

data class CallSession(
    val id: String,
    val startTime: Long,
    val situation: String,
    val personalityDetected: String
)

data class CoachingInsight(
    val id: String,
    val situation: String,
    val personality: String,
    val primaryFinding: String,
    val summary: String,
    val confidence: Double,
    val effectiveness: Double
)
