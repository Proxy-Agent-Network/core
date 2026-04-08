package com.pan.tactical.ui.components

// ============================================================================
// PROXY AGENT NETWORK — POST-MISSION FEEDBACK SCREEN
// Sprint: Reputation, Feedback & Community Systems (April 2026)
//
// SEQUENCE CONTRACT (DO NOT CHANGE):
//   task complete → payout confirmed → THIS SCREEN → map/IDLE
//   Never show before payout. Agent who just saw wallet update is in a
//   better emotional state. This is intentional UX design, not an oversight.
//
// INTEGRATION: Add to AgentDashboardScreen.kt BoxWithConstraints alongside
//   PostMissionOverlays. Trigger via `showFeedbackScreen` state flag after
//   the agent taps "RETURN TO PATROL" on the completion overlay.
//
// THUMBS DOWN UX:
//   800ms hold required. Asymmetric friction is intentional — negative ratings
//   require deliberate action, positive ratings are effortless single tap.
// ============================================================================

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.snap
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.ui.theme.PanColors
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// ─── DATA CONTRACT ────────────────────────────────────────────────────────────

/**
 * A single selectable chip. Populate from `feedback_taxonomy.json`
 * `agent_rating_fleet` pool. The caller owns taxonomy loading — this
 * composable is intentionally decoupled from the JSON file.
 */
data class FeedbackIssueChip(
    val label: String,
    val category: String   // "SAFETY" | "COMPLIANCE" | "CONDUCT" | "LOGISTICS"
)

// Internal state machine — not exposed to callers.
private enum class FeedbackPhase {
    SENTIMENT,        // Thumbs up (instant) / Thumbs down (800ms hold)
    ISSUE_SELECTION,  // Single chip selection + Sub-Rosa vent text
    SUBMITTED         // Warm acknowledgment, return to patrol
}

// ─── MAIN SCREEN ─────────────────────────────────────────────────────────────

/**
 * Post-mission feedback screen.
 *
 * @param taskId        The completed task ID — passed through to onSubmit for
 * the caller to fire POST /v1/agent/missions/{task_id}/feedback.
 * @param fleetId       Fleet partner identifier displayed as settlement source.
 * @param payoutAmount  Net payout already received. Displayed for context.
 * @param issueChips    Chip list from `agent_rating_fleet` in feedback_taxonomy.json.
 * @param onSubmit      (isPositive, category, label, ventText) -> Boolean.
 * Suspend function. UI shows loading while inflight.
 * Only advances to success screen if true is returned.
 * @param onDismiss     Agent is ready to return to the map. Set missionState = "IDLE".
 */
@Composable
fun FeedbackScreen(
    taskId: String,
    fleetId: String,
    payoutAmount: Double,
    issueChips: List<FeedbackIssueChip>,
    onSubmit: suspend (isPositive: Boolean, category: String, label: String, ventText: String) -> Boolean,
    onDismiss: () -> Unit
) {
    var phase by remember { mutableStateOf(FeedbackPhase.SENTIMENT) }
    var selectedLabel by remember { mutableStateOf<String?>(null) }
    var ventText by remember { mutableStateOf("") }
    
    // UI Protection States
    var isSubmitting by remember { mutableStateOf(false) }
    var errorMessage by remember { mutableStateOf<String?>(null) }
    val coroutineScope = rememberCoroutineScope()

    // Pure Kotlin currency formatting — matches MissionAlertOverlay and StickyDispatchCard
    val wholePart = payoutAmount.toInt()
    val cents = ((payoutAmount - wholePart) * 100).toInt()
    val formattedPayout = "$$wholePart.${cents.toString().padStart(2, '0')}"

    // Fullscreen backdrop — matches PostMissionOverlays and MissionAlertOverlay
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(Color(0xEE121212))
            .padding(24.dp),
        contentAlignment = Alignment.Center
    ) {
        when (phase) {

            FeedbackPhase.SENTIMENT -> SentimentPhase(
                formattedPayout = formattedPayout,
                fleetId = fleetId,
                isSubmitting = isSubmitting,
                errorMessage = errorMessage,
                onThumbsUp = {
                    // Launch network request to guarantee backend receipt before showing success
                    coroutineScope.launch {
                        isSubmitting = true
                        errorMessage = null
                        val success = onSubmit(true, "", "", "")
                        isSubmitting = false
                        if (success) {
                            phase = FeedbackPhase.SUBMITTED
                        } else {
                            errorMessage = "Network Error. Please try again."
                        }
                    }
                },
                onThumbsDownConfirmed = {
                    errorMessage = null
                    phase = FeedbackPhase.ISSUE_SELECTION
                }
            )

            FeedbackPhase.ISSUE_SELECTION -> IssueSelectionPhase(
                issueChips = issueChips,
                selectedLabel = selectedLabel,
                ventText = ventText,
                isSubmitting = isSubmitting,
                errorMessage = errorMessage,
                onLabelSelected = { selectedLabel = it },
                onVentTextChanged = { if (it.length <= 280) ventText = it },
                onSubmit = {
                    val label = selectedLabel ?: return@IssueSelectionPhase
                    val chipCategory = issueChips.find { it.label == label }?.category ?: ""
                    
                    coroutineScope.launch {
                        isSubmitting = true
                        errorMessage = null
                        val success = onSubmit(false, chipCategory, label, ventText)
                        isSubmitting = false
                        if (success) {
                            phase = FeedbackPhase.SUBMITTED
                        } else {
                            errorMessage = "Submission failed. Check network connection."
                        }
                    }
                },
                onBack = {
                    // Allow agent to reconsider their thumbs-down
                    selectedLabel = null
                    ventText = ""
                    errorMessage = null
                    phase = FeedbackPhase.SENTIMENT
                }
            )

            FeedbackPhase.SUBMITTED -> SubmittedPhase(onDismiss = onDismiss)
        }
    }
}

// ─── PHASE 1: SENTIMENT ───────────────────────────────────────────────────────

@Composable
private fun SentimentPhase(
    formattedPayout: String,
    fleetId: String,
    isSubmitting: Boolean,
    errorMessage: String?,
    onThumbsUp: () -> Unit,
    onThumbsDownConfirmed: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF1E1E1E), RoundedCornerShape(16.dp))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "MISSION DEBRIEF",
            color = Color.Gray,
            fontSize = 12.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )

        // Payout display — same visual weight as PostMissionOverlays
        Text(
            text = formattedPayout,
            color = PanColors.QualifiedGreen,
            fontSize = 52.sp,
            fontWeight = FontWeight.Black
        )

        Text(
            text = "SETTLED  •  $fleetId",
            color = Color(0xFF555555),
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 1.sp
        )

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(1.dp)
                .background(Color(0xFF2A2A2A))
        )

        Text(
            text = "HOW WAS THIS MISSION?",
            color = Color.White,
            fontSize = 15.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 1.sp,
            textAlign = TextAlign.Center
        )

        // Display network errors gracefully
        if (errorMessage != null) {
            Text(
                text = errorMessage,
                color = PanColors.WarningOrange,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        }

        // ── THUMBS UP — instant single tap ───────────────────────────────────
        Button(
            onClick = onThumbsUp,
            enabled = !isSubmitting,
            colors = ButtonDefaults.buttonColors(containerColor = PanColors.QualifiedGreen),
            modifier = Modifier
                .fillMaxWidth()
                .height(64.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            if (isSubmitting) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            } else {
                Text(
                    text = "👍  SMOOTH OPERATION",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )
            }
        }

        // ── THUMBS DOWN — 800ms hold required ────────────────────────────────
        ThumbsDownButton(
            enabled = !isSubmitting,
            onConfirmed = onThumbsDownConfirmed
        )

        Text(
            text = "Hold the report button for 0.8s to file an issue",
            color = Color(0xFF555555),
            fontSize = 11.sp,
            textAlign = TextAlign.Center
        )
    }
}

// ─── 800ms HOLD BUTTON ────────────────────────────────────────────────────────

/**
 * Thumbs-down button with an 800ms deliberate hold requirement.
 *
 * DESIGN INTENT: Asymmetric friction between positive (instant tap) and
 * negative (800ms hold) is intentional. Bad cell connections and rage-tapping
 * must not accidentally file negative reports. The hold is the friction gate.
 */
@Composable
private fun ThumbsDownButton(
    enabled: Boolean,
    onConfirmed: () -> Unit
) {
    val haptic = LocalHapticFeedback.current
    var isHolding by remember { mutableStateOf(false) }
    var holdProgress by remember { mutableStateOf(0f) }

    // NOTE: enabled is checked at LaunchedEffect start but not re-checked before
    // onConfirmed fires. A simultaneous dual-gesture edge case is theoretically
    // possible but not pilot-relevant. Revisit before 500-agent scale.
    LaunchedEffect(isHolding) {
        if (isHolding && enabled) {
            val startTime = System.currentTimeMillis()
            while (isHolding) {
                val elapsed = System.currentTimeMillis() - startTime
                holdProgress = (elapsed / 800f).coerceIn(0f, 1f)
                if (holdProgress >= 1f) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    isHolding = false
                    onConfirmed()
                    break
                }
                delay(16L)
            }
        } else {
            holdProgress = 0f
        }
    }

    val animatedProgress by animateFloatAsState(
        targetValue = holdProgress,
        animationSpec = if (isHolding) snap() else tween(durationMillis = 200),
        label = "hold_progress"
    )

    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(64.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(Color(0xFF2A1A1A))
            .border(
                width = 1.dp,
                color = if (isHolding) Color(0xFFF44336) else Color(0xFF3A1F1F),
                shape = RoundedCornerShape(12.dp)
            )
            // Safer, more idiomatic Compose pointer logic handling gesture cancellation correctly
            .pointerInput(enabled) {
                if (!enabled) return@pointerInput
                detectTapGestures(
                    onPress = {
                        isHolding = true
                        tryAwaitRelease() // Automatically handles finger slide-off and cancellation
                        isHolding = false
                    }
                )
            },
        contentAlignment = Alignment.CenterStart
    ) {
        // Fill track — grows left-to-right as agent holds
        if (animatedProgress > 0f) {
            Box(
                modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(animatedProgress)
                    .background(
                        color = Color(0xFFF44336).copy(alpha = 0.22f),
                        shape = RoundedCornerShape(
                            topStart = 12.dp,
                            bottomStart = 12.dp,
                            topEnd = if (animatedProgress >= 1f) 12.dp else 0.dp,
                            bottomEnd = if (animatedProgress >= 1f) 12.dp else 0.dp
                        )
                    )
            )
        }

        // Label centered over the fill track
        Text(
            text = "👎  REPORT AN ISSUE",
            color = if (isHolding) Color(0xFFF44336) else Color(0xFF666666),
            fontSize = 16.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 1.sp,
            modifier = Modifier.align(Alignment.Center)
        )
    }
}

// ─── PHASE 2: ISSUE SELECTION ─────────────────────────────────────────────────

@Composable
private fun IssueSelectionPhase(
    issueChips: List<FeedbackIssueChip>,
    selectedLabel: String?,
    ventText: String,
    isSubmitting: Boolean,
    errorMessage: String?,
    onLabelSelected: (String) -> Unit,
    onVentTextChanged: (String) -> Unit,
    onSubmit: () -> Unit,
    onBack: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .verticalScroll(rememberScrollState())
            .background(Color(0xFF1E1E1E), RoundedCornerShape(16.dp))
            .padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(10.dp)
    ) {

        Text(
            text = "WHAT WENT WRONG?",
            color = Color(0xFFF44336),
            fontSize = 16.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )

        Text(
            text = "SELECT ONE ISSUE",
            color = Color.Gray,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 1.sp
        )

        Spacer(modifier = Modifier.height(2.dp))

        // ── ISSUE CHIPS ───────────────────────────────────────────────────────
        issueChips.forEach { chip ->
            val isSelected = chip.label == selectedLabel
            val chipColor = categoryAccentColor(chip.category)

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(8.dp))
                    .background(
                        if (isSelected) chipColor.copy(alpha = 0.12f)
                        else Color(0xFF272727)
                    )
                    .border(
                        width = if (isSelected) 2.dp else 1.dp,
                        color = if (isSelected) chipColor else Color(0xFF383838),
                        shape = RoundedCornerShape(8.dp)
                    )
                    .clickable(enabled = !isSubmitting) {
                        onLabelSelected(if (isSelected) "" else chip.label)
                    }
                    .padding(horizontal = 16.dp, vertical = 14.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = chip.label,
                        color = if (isSelected) chipColor else Color.LightGray,
                        fontSize = 14.sp,
                        fontWeight = if (isSelected) FontWeight.Black else FontWeight.Medium
                    )

                    if (isSelected) {
                        Text(
                            text = "✓",
                            color = chipColor,
                            fontSize = 16.sp,
                            fontWeight = FontWeight.Black
                        )
                    } else {
                        Text(
                            text = chip.category,
                            color = Color(0xFF4A4A4A),
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.sp
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(6.dp))

        // ── SUB-ROSA VENT TEXT ────────────────────────────────────────────────
        Text(
            text = "🔒 PRIVATE: This goes to PAN Ops, not the fleet partner.",
            color = PanColors.WarningOrange,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold
        )

        OutlinedTextField(
            value = ventText,
            onValueChange = { if (it.length <= 280) onVentTextChanged(it) },
            enabled = !isSubmitting,
            modifier = Modifier
                .fillMaxWidth()
                .heightIn(min = 96.dp),
            placeholder = {
                Text(
                    text = "Optional — what else should Ops know?",
                    color = Color(0xFF4A4A4A),
                    fontSize = 13.sp
                )
            },
            supportingText = {
                Text(
                    text = "${280 - ventText.length} characters remaining",
                    color = if (ventText.length > 250) PanColors.WarningOrange else Color(0xFF555555),
                    fontSize = 11.sp
                )
            },
            colors = OutlinedTextFieldDefaults.colors(
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White,
                focusedBorderColor = PanColors.CyanAccent,
                unfocusedBorderColor = Color(0xFF383838),
                cursorColor = PanColors.CyanAccent,
                focusedContainerColor = Color(0xFF1A1A1A),
                unfocusedContainerColor = Color(0xFF1A1A1A)
            ),
            shape = RoundedCornerShape(8.dp),
            maxLines = 6
        )

        // Display network errors gracefully
        if (errorMessage != null) {
            Text(
                text = errorMessage,
                color = PanColors.WarningOrange,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(4.dp))

        // ── SUBMIT ────────────────────────────────────────────────────────────
        Button(
            onClick = onSubmit,
            enabled = !isSubmitting && selectedLabel != null && selectedLabel.isNotBlank(),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color(0xFFF44336),
                disabledContainerColor = Color(0xFF3A1A1A)
            ),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            if (isSubmitting) {
                CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
            } else {
                Text(
                    text = "SUBMIT REPORT",
                    color = if (selectedLabel != null && selectedLabel.isNotBlank()) Color.White else Color(0xFF5A3A3A),
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )
            }
        }

        // ── BACK ─────────────────────────────────────────────────────────────
        TextButton(
            onClick = onBack,
            enabled = !isSubmitting,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                text = "← BACK",
                color = Color(0xFF555555),
                fontWeight = FontWeight.Bold,
                fontSize = 13.sp
            )
        }
    }
}

// ─── PHASE 3: SUBMITTED ───────────────────────────────────────────────────────

@Composable
private fun SubmittedPhase(onDismiss: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFF1E1E1E), RoundedCornerShape(16.dp))
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "✓",
            color = PanColors.QualifiedGreen,
            fontSize = 48.sp,
            fontWeight = FontWeight.Black
        )

        Text(
            text = "NOTED",
            color = PanColors.QualifiedGreen,
            fontSize = 24.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 3.sp
        )

        Text(
            text = "We review all feedback to make the network better.\n\nReady for your next mission?",
            color = Color.LightGray,
            fontSize = 14.sp,
            textAlign = TextAlign.Center,
            lineHeight = 22.sp
        )

        Spacer(modifier = Modifier.height(8.dp))

        Button(
            onClick = onDismiss,
            colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4)),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            Text(
                text = "RETURN TO PATROL",
                color = Color.Black,
                fontWeight = FontWeight.Black,
                letterSpacing = 1.sp
            )
        }
    }
}

// ─── HELPERS ─────────────────────────────────────────────────────────────────

private fun categoryAccentColor(category: String): Color = when (category.uppercase()) {
    "SAFETY"     -> Color(0xFFF44336)
    "COMPLIANCE" -> Color(0xFFFF9800)
    "CONDUCT"    -> Color(0xFFFFEB3B)
    "LOGISTICS"  -> Color(0xFF00BCD4)
    else         -> Color(0xFF888888)
}