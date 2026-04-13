package com.pan.tactical.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil3.compose.AsyncImage
import com.pan.tactical.models.MissionData
import com.pan.tactical.managers.SentryExtensionRequest
import com.pan.tactical.ui.theme.PanColors

enum class ContextType { PHOTO, VOICE, TEXT }

data class ContextItem(
    val id: String,
    val type: ContextType,
    val payloadBytes: ByteArray? = null,
    var textContent: String? = null
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnSceneTerminal(
    activeMission: MissionData?,
    contextItems: List<ContextItem>,
    selectedItem: ContextItem?,
    onItemSelected: (ContextItem) -> Unit,
    onUpdateItem: (id: String, updatedText: String) -> Unit,
    isProcessingRedaction: Boolean,
    isResolving: Boolean,
    terminalLogs: List<String>,
    hasCameraPermission: Boolean,
    extensionRequest: SentryExtensionRequest?,
    onRequestCameraPermission: () -> Unit,
    onCapturePhoto: () -> Unit,
    onAddTextNote: (String) -> Unit,
    onAddVoiceNote: (String) -> Unit,
    onRemoveItem: (String) -> Unit,
    onRunDiagnostics: () -> Unit,
    onAcceptExtension: (String, Int, Double) -> Unit,
    onDeclineExtension: () -> Unit,
    onLogEntry: (String) -> Unit
) {
    val isSentry = activeMission?.role.toString().uppercase() == "SENTRY"
    var showTextDialog by remember { mutableStateOf(false) }
    var noteText by remember { mutableStateOf("") }
    var editingItemId: String? by remember { mutableStateOf(null) }

    // 🟢 NEW: State for the "+" slot pop-up menu
    var showAddMenuDialog by remember { mutableStateOf(false) }

    // Pre-calculate limits to use in both the Action Bar and the Pop-up Menu
    val photoCount = contextItems.count { it.type == ContextType.PHOTO }
    val canAddPhoto = photoCount < 3 && contextItems.size < 5
    val canAddNote = contextItems.size < 5

    LaunchedEffect(isProcessingRedaction) {
        if (isProcessingRedaction) {
            onLogEntry("PrivacyFilter: Redacting PII and scaling to 720p...")
        } else if (contextItems.isNotEmpty()) {
            onLogEntry("Compliance pass complete. Evidence sanitized.")
        }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        Column(
            modifier = Modifier.fillMaxWidth().background(Color(0xFF0D1117)).padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            // --- HEADER ---
            val titleText = if (isSentry) "🚧 SENTRY TRAFFIC CONTROL" else "📟 AV DIAGNOSTIC TERMINAL"
            val titleColor = if (isSentry) Color(0xFFFF9800) else Color(0xFF00FF00)

            Text(titleText, color = titleColor, fontSize = 16.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(12.dp))

            // --- DIAGNOSTIC INSTRUCTION BLOCK ---
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1A1A1A), RoundedCornerShape(8.dp))
                    .border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp))
                    .padding(12.dp)
            ) {
                Column {
                    Text(
                        text = "FAULT: ${activeMission?.errorCode ?: "UNKNOWN_ERROR"}",
                        color = Color.White,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = activeMission?.diagnostic ?: "Assess vehicle state and run diagnostics.",
                        color = Color(0xFFCCCCCC),
                        fontSize = 14.sp,
                        lineHeight = 20.sp
                    )
                }
            }
            Spacer(modifier = Modifier.height(12.dp))

            // --- POLYMORPHIC CONTEXT DETAIL PANEL ---
            ContextDetailPanel(
                selectedItem = selectedItem,
                onEditNoteRequested = { item ->
                    editingItemId = item.id
                    noteText = item.textContent ?: ""
                    showTextDialog = true
                },
                onPlaybackAudioRequested = { /* Future actual implementation */ },
                modifier = Modifier.weight(1f)
            )
            Spacer(modifier = Modifier.height(16.dp))

            // --- CONTEXT GRID (5 SLOTS) ---
            Row(
                modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                contextItems.forEach { item ->
                    ContextThumbnail(
                        item = item,
                        onRemove = { onRemoveItem(item.id) },
                        onClick = { onItemSelected(item) },
                        isSelected = item == selectedItem
                    )
                }

                val emptySlots = 5 - contextItems.size
                repeat(emptySlots) {
                    Box(
                        modifier = Modifier
                            .size(72.dp)
                            .background(Color(0xFF1E1E1E), RoundedCornerShape(8.dp))
                            .border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp))
                            .clip(RoundedCornerShape(8.dp))
                            // 🟢 THE FIX: Make the empty slot clickable to open the menu
                            .clickable { showAddMenuDialog = true },
                        contentAlignment = Alignment.Center
                    ) {
                        Text("+", color = Color(0xFF555555), fontSize = 24.sp)
                    }
                }
            }
            Spacer(modifier = Modifier.height(16.dp))

            // --- ACTION BAR ---
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                IconButton(
                    onClick = {
                        if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission()
                    },
                    enabled = canAddPhoto,
                    modifier = Modifier.size(56.dp).background(if (canAddPhoto) PanColors.ButtonSecondary else Color(0xFF1E1E1E), CircleShape)
                ) {
                    Text("📷", fontSize = 24.sp)
                }

                IconButton(
                    onClick = { onAddVoiceNote("") },
                    enabled = canAddNote,
                    modifier = Modifier.size(56.dp).background(if (canAddNote) PanColors.ButtonSecondary else Color(0xFF1E1E1E), CircleShape)
                ) {
                    Text("🎙️", fontSize = 24.sp)
                }

                IconButton(
                    onClick = { showTextDialog = true },
                    enabled = canAddNote,
                    modifier = Modifier.size(56.dp).background(if (canAddNote) PanColors.ButtonSecondary else Color(0xFF1E1E1E), CircleShape)
                ) {
                    Text("⌨️", fontSize = 24.sp)
                }
            }
            Spacer(modifier = Modifier.height(24.dp))

            // --- SUBMIT BUTTON ---
            Button(
                enabled = !isResolving && !isProcessingRedaction && contextItems.isNotEmpty(),
                onClick = onRunDiagnostics,
                colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF00BCD4), disabledContainerColor = Color(0xFF1E3538)),
                modifier = Modifier.fillMaxWidth().height(64.dp),
                shape = RoundedCornerShape(8.dp)
            ) {
                if (isResolving) {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp), color = Color.Black)
                } else {
                    Text("RUN DIAGNOSTICS", color = Color.Black, fontWeight = FontWeight.Black, fontSize = 16.sp)
                }
            }
        }

        // 🟢 NEW: ADD CONTEXT MENU DIALOG
        if (showAddMenuDialog) {
            AlertDialog(
                onDismissRequest = { showAddMenuDialog = false },
                containerColor = PanColors.CardBackground,
                title = { Text("Add Evidence", color = Color.White, fontWeight = FontWeight.Bold) },
                text = {
                    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                        Button(
                            onClick = {
                                showAddMenuDialog = false
                                if (hasCameraPermission) onCapturePhoto() else onRequestCameraPermission()
                            },
                            enabled = canAddPhoto,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = PanColors.ButtonSecondary,
                                disabledContainerColor = Color(0xFF1E1E1E)
                            ),
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("📷 Take Photo", color = if (canAddPhoto) Color.White else Color.Gray, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = {
                                showAddMenuDialog = false
                                onAddVoiceNote("")
                            },
                            enabled = canAddNote,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = PanColors.ButtonSecondary,
                                disabledContainerColor = Color(0xFF1E1E1E)
                            ),
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("🎙️ Voice Memo", color = if (canAddNote) Color.White else Color.Gray, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }

                        Button(
                            onClick = {
                                showAddMenuDialog = false
                                showTextDialog = true
                            },
                            enabled = canAddNote,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = PanColors.ButtonSecondary,
                                disabledContainerColor = Color(0xFF1E1E1E)
                            ),
                            modifier = Modifier.fillMaxWidth().height(56.dp),
                            shape = RoundedCornerShape(8.dp)
                        ) {
                            Text("📝 Take Notes", color = if (canAddNote) Color.White else Color.Gray, fontSize = 16.sp, fontWeight = FontWeight.Bold)
                        }
                    }
                },
                confirmButton = {},
                dismissButton = {
                    TextButton(onClick = { showAddMenuDialog = false }) {
                        Text("CANCEL", color = Color.Gray)
                    }
                }
            )
        }

        // --- TEXT NOTE DIALOG (Modified for Editing) ---
        if (showTextDialog) {
            val dialogTitle = if (editingItemId == null) "Add Field Note" else "Edit Note"
            AlertDialog(
                onDismissRequest = { showTextDialog = false; noteText = ""; editingItemId = null },
                containerColor = PanColors.CardBackground,
                title = { Text(dialogTitle, color = Color.White, fontWeight = FontWeight.Bold) },
                text = {
                    OutlinedTextField(
                        value = noteText,
                        onValueChange = { noteText = it },
                        modifier = Modifier.fillMaxWidth().height(120.dp),
                        placeholder = { Text("Describe the scene...", color = Color.Gray) },
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedTextColor = Color.White,
                            unfocusedTextColor = Color.White,
                            focusedBorderColor = PanColors.QualifiedGreen,
                            unfocusedBorderColor = Color.Gray
                        )
                    )
                },
                confirmButton = {
                    Button(
                        onClick = {
                            if (noteText.isNotBlank()) {
                                if (editingItemId == null) {
                                    // Creation flow
                                    onAddTextNote(noteText)
                                } else {
                                    // Update flow (editing existing note)
                                    onUpdateItem(editingItemId!!, noteText)
                                }
                            }
                            showTextDialog = false
                            noteText = ""
                            editingItemId = null
                        },
                        colors = ButtonDefaults.buttonColors(containerColor = PanColors.QualifiedGreen)
                    ) {
                        Text("SAVE", color = Color.White, fontWeight = FontWeight.Bold)
                    }
                },
                dismissButton = {
                    TextButton(onClick = {
                        showTextDialog = false;
                        noteText = "";
                        editingItemId = null
                    }) {
                        Text("CANCEL", color = Color.Gray)
                    }
                }
            )
        }

        AnimatedVisibility(
            visible = extensionRequest != null,
            enter = fadeIn(),
            exit = fadeOut()
        ) {
            val stableRequest = remember { extensionRequest } ?: return@AnimatedVisibility
            SentryExtensionOverlay(
                request = stableRequest,
                onAccept = { onAcceptExtension(stableRequest.taskId, stableRequest.extensionMinutes, stableRequest.offeredBountyUsd) },
                onDecline = onDeclineExtension
            )
        }
    }
}

@Composable
fun ContextDetailPanel(
    selectedItem: ContextItem?,
    onEditNoteRequested: (ContextItem) -> Unit,
    onPlaybackAudioRequested: (ContextItem) -> Unit,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .height(250.dp)
            .background(Color.Black, RoundedCornerShape(8.dp))
            .border(1.dp, Color(0xFF333333), RoundedCornerShape(8.dp))
            .padding(16.dp),
        contentAlignment = Alignment.Center
    ) {
        if (selectedItem == null) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Text("Select an item to view or edit", color = Color.Gray, style = MaterialTheme.typography.bodyLarge)
            }
        } else {
            when (selectedItem.type) {
                ContextType.PHOTO -> {
                    if (selectedItem.payloadBytes != null) {
                        AsyncImage(
                            model = selectedItem.payloadBytes,
                            contentDescription = "Full Size Evidence",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Fit
                        )
                    }
                }
                ContextType.TEXT, ContextType.VOICE -> {
                    Column(
                        modifier = Modifier.fillMaxSize().clickable {
                            onEditNoteRequested(selectedItem)
                        }
                    ) {
                        Text(
                            text = if (selectedItem.type == ContextType.VOICE) "🎙️ Voice Note Transcription:" else "📝 Field Note:",
                            color = Color.Gray,
                            style = MaterialTheme.typography.labelSmall
                        )
                        Spacer(Modifier.height(8.dp))
                        Text(
                            text = selectedItem.textContent ?: "(No Content)",
                            color = Color.White,
                            style = MaterialTheme.typography.bodyMedium,
                            lineHeight = 22.sp,
                            modifier = Modifier.weight(1f).verticalScroll(rememberScrollState())
                        )
                        Spacer(Modifier.height(8.dp))

                        Text(
                            "Tap note to edit",
                            color = Color(0xFF00BCD4),
                            style = MaterialTheme.typography.labelMedium,
                            modifier = Modifier.align(Alignment.End)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun ContextThumbnail(item: ContextItem, onRemove: () -> Unit, onClick: () -> Unit, isSelected: Boolean) {
    Box(
        modifier = Modifier
            .size(72.dp)
            .border(2.dp, if (isSelected) Color(0xFF00BCD4) else Color.Transparent, RoundedCornerShape(8.dp))
            .clip(RoundedCornerShape(8.dp))
            .background(Color(0xFF1E1E1E))
            .clickable { onClick() }
    ) {
        when (item.type) {
            ContextType.PHOTO -> {
                if (item.payloadBytes != null) {
                    AsyncImage(
                        model = item.payloadBytes,
                        contentDescription = "Evidence",
                        modifier = Modifier.fillMaxSize(),
                        contentScale = ContentScale.Crop
                    )
                }
            }
            ContextType.VOICE -> {
                Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    Text("🎙️", fontSize = 24.sp)
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(item.textContent ?: "Audio", color = Color.White, fontSize = 8.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(horizontal = 4.dp))
                }
            }
            ContextType.TEXT -> {
                Column(modifier = Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    Text("📝", fontSize = 24.sp)
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(item.textContent ?: "Note", color = Color.White, fontSize = 8.sp, maxLines = 1, overflow = TextOverflow.Ellipsis, modifier = Modifier.padding(horizontal = 4.dp))
                }
            }
        }

        Box(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(4.dp)
                .size(20.dp)
                .background(Color(0xAA000000), CircleShape)
                .clickable { onRemove() },
            contentAlignment = Alignment.Center
        ) {
            Text("✕", color = Color.Red, fontSize = 10.sp, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
fun SentryExtensionOverlay(request: SentryExtensionRequest, onAccept: () -> Unit, onDecline: () -> Unit) {
    Box(modifier = Modifier.fillMaxSize().background(Color(0xEE000000)).padding(24.dp), contentAlignment = Alignment.Center) {
        Column(
            modifier = Modifier.background(Color(0xFF1E1E1E), RoundedCornerShape(16.dp)).border(2.dp, Color(0xFF4CAF50), RoundedCornerShape(16.dp)).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("🛡️ SENTRY EXTENSION", color = Color(0xFF4CAF50), fontSize = 20.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(12.dp))
            Text(text = "The fleet requires an additional ${request.extensionMinutes}m of scene securement.", color = Color.White, textAlign = TextAlign.Center)
            Spacer(modifier = Modifier.height(16.dp))
            Text(text = "+$${"%.2f".format(request.offeredBountyUsd)} BOUNTY", color = Color(0xFF4CAF50), fontSize = 28.sp, fontWeight = FontWeight.Black)
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = onAccept, modifier = Modifier.fillMaxWidth().height(56.dp), colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF4CAF50))) {
                Text("ACCEPT & EXTEND", fontWeight = FontWeight.ExtraBold, color = Color.White)
            }
            Spacer(modifier = Modifier.height(8.dp))
            TextButton(onClick = onDecline, modifier = Modifier.fillMaxWidth().height(48.dp)) {
                Text("DECLINE", color = Color.Gray, fontWeight = FontWeight.Bold)
            }
        }
    }
}