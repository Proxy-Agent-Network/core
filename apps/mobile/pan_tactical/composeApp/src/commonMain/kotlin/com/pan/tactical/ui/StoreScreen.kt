package com.pan.tactical.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.grid.GridCells
import androidx.compose.foundation.lazy.grid.LazyVerticalGrid
import androidx.compose.foundation.lazy.grid.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pan.tactical.ui.theme.PanColors
import kotlinx.coroutines.launch

// ─── DATA MODELS & BUSINESS LOGIC ────────────────────────────────────────────

enum class ItemAvailability {
    IN_STOCK,
    OUT_OF_STOCK,
    COMING_FUTURE,
    LOCKED_MISSIONS
}

data class StoreItem(
    val id: String,
    val name: String,
    val description: String,
    val priceUsd: Double,
    val icon: String,
    val availability: ItemAvailability,
    val availabilityLabel: String? = null,
    val unlockMissionThreshold: Int? = null
)

// Single Source of Truth for availability and locking logic
fun StoreItem.isMissionLocked(missionsCompleted: Int): Boolean {
    return availability == ItemAvailability.LOCKED_MISSIONS &&
            missionsCompleted < (unlockMissionThreshold ?: Int.MAX_VALUE)
}

fun StoreItem.isPurchasable(missionsCompleted: Int): Boolean {
    return availability == ItemAvailability.IN_STOCK ||
            (availability == ItemAvailability.LOCKED_MISSIONS && !isMissionLocked(missionsCompleted))
}

// ─── MAIN SCREEN ─────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StoreScreen(
    currentBalance: Double,
    missionsCompleted: Int,
    onBack: () -> Unit,
    onJoinWaitlist: suspend (itemId: String, email: String) -> Boolean
) {
    val coroutineScope = rememberCoroutineScope()
    val snackbarHostState = remember { SnackbarHostState() }

    // Bottom Sheet State for Lead Capture
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    // 🛡️ FIXED: Synchronized lifecycle scopes to prevent Zombie State on process death
    var showWaitlistSheet by remember { mutableStateOf(false) }
    var selectedWaitlistItem by remember { mutableStateOf<StoreItem?>(null) }

    // Hardcoded inventory for Vanguard 50 Pilot.
    // TODO (Q3): Migrate this to a fetch call from the backend /v1/catalog endpoint.
    val inventory = remember {
        listOf(
            StoreItem(
                id = "gear_vest_01",
                name = "Vanguard Class-2 Hi-Vis Vest",
                description = "Mandatory for Tier 3 nighttime operations. SB 1417 compliant.",
                priceUsd = 45.00,
                icon = "🦺",
                availability = ItemAvailability.IN_STOCK
            ),
            StoreItem(
                id = "gear_flare_01",
                name = "LED Roadside Flare Kit",
                description = "Required for securing multi-lane incident perimeters.",
                priceUsd = 25.00,
                icon = "🚨",
                availability = ItemAvailability.IN_STOCK
            ),
            StoreItem(
                id = "gear_hat_01",
                name = "Standard Field Hat",
                description = "Non-electronic PAN branded cap.",
                priceUsd = 18.00,
                icon = "🧢",
                availability = ItemAvailability.IN_STOCK
            ),
            StoreItem(
                id = "gear_visor_01",
                name = "PAN Window Visor",
                description = "Vehicle identification visor. Clearly marks your AV response unit.",
                priceUsd = 22.00,
                icon = "🚘",
                availability = ItemAvailability.IN_STOCK
            ),
            StoreItem(
                id = "gear_decal_01",
                name = "PAN Magnetic Vehicle Decals",
                description = "Identifies your personal vehicle as an active Vanguard response unit.",
                priceUsd = 15.00,
                icon = "🛡️",
                availability = ItemAvailability.OUT_OF_STOCK
            ),
            StoreItem(
                id = "hw_gauntlets",
                name = "VFG-1 Gauntlets",
                description = "UWB micro-homing gloves for secure, gesture-based vehicle handshakes.",
                priceUsd = 60.00,
                icon = "🧤",
                availability = ItemAvailability.LOCKED_MISSIONS,
                unlockMissionThreshold = 10
            ),
            StoreItem(
                id = "hw_haphat_v2",
                name = "HapHat v2.3",
                description = "Tactical hardhat with 360° LIDAR and spatial haptic feedback.",
                priceUsd = 120.00,
                icon = "🪖",
                availability = ItemAvailability.COMING_FUTURE,
                availabilityLabel = "Q3 2026"
            ),
            StoreItem(
                id = "hw_panoply_vest",
                name = "PANOPLY Vest v1.2",
                description = "Active composite armor with integrated RATS threat detection.",
                priceUsd = 250.00,
                icon = "🦾",
                availability = ItemAvailability.COMING_FUTURE,
                availabilityLabel = "Q4 2026"
            ),
            StoreItem(
                id = "hw_aegis_polo",
                name = "Aegis Polo VFP-1",
                description = "Biometric telemetry polo. Streams stress-index directly to operations.",
                priceUsd = 85.00,
                icon = "👕",
                availability = ItemAvailability.COMING_FUTURE,
                availabilityLabel = "Q1 2027"
            )
        )
    }

    Scaffold(
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        containerColor = Color(0xFF121212),
        topBar = {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .windowInsetsPadding(WindowInsets.statusBars)
                    .background(Color.Black)
                    .padding(16.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(PanColors.ButtonSecondary, RoundedCornerShape(20.dp))
                        .clip(RoundedCornerShape(20.dp))
                        .clickable { onBack() },
                    contentAlignment = Alignment.Center
                ) { Text("◀", color = Color.White, fontSize = 18.sp) }

                Text(
                    text = "SUPPLY DEPOT",
                    color = Color.White,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 2.sp
                )

                // Miniature Balance Display
                Column(horizontalAlignment = Alignment.End) {
                    Text("BALANCE", color = Color.Gray, fontSize = 9.sp, fontWeight = FontWeight.Bold)
                    Text(
                        text = currentBalance.toCurrency(),
                        color = PanColors.QualifiedGreen,
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Black
                    )
                }
            }
        }
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Header Warning
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(Color(0xFF1A1A1A))
                    .padding(16.dp)
            ) {
                Text(
                    text = "VANGUARD 50 PILOT: Hardware fulfillment is currently restricted to the Mesa, AZ operations center. Shipping is disabled.",
                    color = PanColors.WarningOrange,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                    lineHeight = 18.sp,
                    textAlign = TextAlign.Center,
                    modifier = Modifier.fillMaxWidth()
                )
            }

            LazyVerticalGrid(
                columns = GridCells.Fixed(2),
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(inventory) { item ->
                    StoreItemCard(
                        item = item,
                        currentBalance = currentBalance,
                        missionsCompleted = missionsCompleted,
                        onClick = {
                            val isLocked = item.isMissionLocked(missionsCompleted)
                            val isPurchasable = item.isPurchasable(missionsCompleted)

                            when {
                                isLocked -> {
                                    coroutineScope.launch {
                                        snackbarHostState.showSnackbar("Complete ${item.unlockMissionThreshold} missions to unlock this gear.")
                                    }
                                }
                                item.availability == ItemAvailability.COMING_FUTURE -> {
                                    selectedWaitlistItem = item
                                    showWaitlistSheet = true
                                }
                                item.availability == ItemAvailability.OUT_OF_STOCK -> {
                                    coroutineScope.launch {
                                        snackbarHostState.showSnackbar("Item is currently out of stock.")
                                    }
                                }
                                isPurchasable -> {
                                    if (currentBalance >= item.priceUsd) {
                                        // TODO: Wire to actual purchase API
                                        coroutineScope.launch {
                                            snackbarHostState.showSnackbar("Purchase API not yet wired for Pilot.")
                                        }
                                    } else {
                                        coroutineScope.launch {
                                            snackbarHostState.showSnackbar("Insufficient funds. Complete more missions.", withDismissAction = true)
                                        }
                                    }
                                }
                            }
                        }
                    )
                }
            }
        }

        // --- WAITLIST BOTTOM SHEET ---
        val stableItem = selectedWaitlistItem
        if (showWaitlistSheet && stableItem != null) {
            ModalBottomSheet(
                onDismissRequest = { showWaitlistSheet = false },
                sheetState = sheetState,
                containerColor = Color(0xFF1E1E1E),
                scrimColor = Color.Black.copy(alpha = 0.8f)
            ) {
                WaitlistBottomSheetContent(
                    item = stableItem,
                    onSubmit = { email ->
                        val success = onJoinWaitlist(stableItem.id, email)
                        if (success) {
                            sheetState.hide()
                            showWaitlistSheet = false
                            coroutineScope.launch {
                                snackbarHostState.showSnackbar("Added to priority waitlist for ${stableItem.name}.")
                            }
                        } else {
                            coroutineScope.launch {
                                snackbarHostState.showSnackbar("Failed to join waitlist. Please try again.")
                            }
                        }
                        success
                    }
                )
            }
        }
    }
}

// ─── COMPONENTS ──────────────────────────────────────────────────────────────

@Composable
private fun StoreItemCard(
    item: StoreItem,
    currentBalance: Double,
    missionsCompleted: Int,
    onClick: () -> Unit
) {
    val isLocked = item.isMissionLocked(missionsCompleted)
    val isPurchasable = item.isPurchasable(missionsCompleted)
    val isFuture = item.availability == ItemAvailability.COMING_FUTURE
    val canAfford = currentBalance >= item.priceUsd

    val cardAlpha = if (isPurchasable) 1f else 0.5f
    val borderColor = if (isFuture) PanColors.CyanAccent.copy(alpha = 0.3f) else Color(0xFF2A2A2A)

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp))
            .background(Color(0xFF1E1E1E))
            .border(1.dp, borderColor, RoundedCornerShape(12.dp))
            .clickable { onClick() }
            .padding(12.dp)
            .alpha(cardAlpha)
    ) {
        // Icon & Price Row
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.Top
        ) {
            Text(
                text = item.icon,
                fontSize = 36.sp
            )

            Column(horizontalAlignment = Alignment.End) {
                Text(
                    text = item.priceUsd.toCurrency(),
                    color = if (canAfford || !isPurchasable) Color.White else PanColors.WarningOrange,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Black
                )

                // Status Badge
                val statusText = when {
                    isLocked -> "LOCKED"
                    isPurchasable -> "IN STOCK"
                    item.availability == ItemAvailability.OUT_OF_STOCK -> "SOLD OUT"
                    isFuture -> item.availabilityLabel ?: "COMING SOON"
                    else -> ""
                }

                val statusColor = when {
                    isLocked -> Color.Gray
                    isPurchasable -> PanColors.QualifiedGreen
                    item.availability == ItemAvailability.OUT_OF_STOCK -> Color.Gray
                    isFuture -> PanColors.CyanAccent
                    else -> Color.Gray
                }

                Text(
                    text = statusText,
                    color = statusColor,
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp,
                    modifier = Modifier.padding(top = 4.dp)
                )
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // Text Content
        Text(
            text = item.name,
            color = Color.White,
            fontSize = 14.sp,
            fontWeight = FontWeight.Bold,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = item.description,
            color = Color(0xFF888888),
            fontSize = 11.sp,
            lineHeight = 14.sp,
            maxLines = 3,
            overflow = TextOverflow.Ellipsis
        )

        Spacer(modifier = Modifier.height(12.dp))

        // Call to Action Button
        val buttonText = when {
            isLocked -> "UNLOCKS AT ${item.unlockMissionThreshold} MISSIONS"
            isPurchasable -> if (canAfford) "PURCHASE" else "INSUFFICIENT FUNDS"
            item.availability == ItemAvailability.OUT_OF_STOCK -> "UNAVAILABLE"
            isFuture -> "NOTIFY ME"
            else -> ""
        }

        val buttonColor = when {
            isLocked -> Color(0xFF2A2A2A)
            isPurchasable -> if (canAfford) PanColors.QualifiedGreen else Color(0xFF333333)
            item.availability == ItemAvailability.OUT_OF_STOCK -> Color(0xFF333333)
            isFuture -> PanColors.CyanAccent.copy(alpha = 0.2f)
            else -> Color(0xFF333333)
        }

        val buttonTextColor = if (isFuture) PanColors.CyanAccent else Color.Black

        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(36.dp)
                .background(buttonColor, RoundedCornerShape(6.dp)),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = buttonText,
                color = if (isPurchasable && canAfford || isFuture) buttonTextColor else Color.Gray,
                fontSize = 10.sp,
                fontWeight = FontWeight.Black,
                letterSpacing = if (isLocked) 0.sp else 1.sp,
                textAlign = TextAlign.Center,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                modifier = Modifier.padding(horizontal = 4.dp)
            )
        }
    }
}

@Composable
private fun WaitlistBottomSheetContent(
    item: StoreItem,
    onSubmit: suspend (String) -> Boolean
) {
    var email by rememberSaveable { mutableStateOf("") }
    var isSubmitting by remember { mutableStateOf(false) }

    val emailRegex = remember { Regex("^[^@]+@[^@]+\\.[^@]+$") }
    val isValidEmail = emailRegex.matches(email)
    val coroutineScope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(start = 24.dp, end = 24.dp, bottom = 48.dp, top = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = item.icon,
            fontSize = 48.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "HARDWARE LOCKED",
            color = PanColors.CyanAccent,
            fontSize = 12.sp,
            fontWeight = FontWeight.Black,
            letterSpacing = 2.sp
        )

        Text(
            text = item.name,
            color = Color.White,
            fontSize = 24.sp,
            fontWeight = FontWeight.Bold,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(vertical = 8.dp)
        )

        Text(
            text = "This hardware requires network consensus for mass manufacturing. Enter your dispatch email to vote for immediate production and secure your place in the priority queue.",
            color = Color.LightGray,
            fontSize = 13.sp,
            lineHeight = 20.sp,
            textAlign = TextAlign.Center,
            modifier = Modifier.padding(bottom = 24.dp)
        )

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            enabled = !isSubmitting,
            placeholder = { Text("Agent Dispatch Email", color = Color.Gray, fontSize = 14.sp) },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            colors = OutlinedTextFieldDefaults.colors(
                focusedBorderColor = PanColors.CyanAccent,
                unfocusedBorderColor = Color(0xFF333333),
                focusedTextColor = Color.White,
                unfocusedTextColor = Color.White,
                cursorColor = PanColors.CyanAccent
            ),
            shape = RoundedCornerShape(8.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Button(
            onClick = {
                coroutineScope.launch {
                    isSubmitting = true
                    try {
                        onSubmit(email)
                    } finally {
                        isSubmitting = false
                    }
                }
            },
            enabled = isValidEmail && !isSubmitting,
            colors = ButtonDefaults.buttonColors(
                containerColor = PanColors.CyanAccent,
                disabledContainerColor = Color(0xFF333333)
            ),
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            shape = RoundedCornerShape(12.dp)
        ) {
            if (isSubmitting) {
                CircularProgressIndicator(color = Color.Black, modifier = Modifier.size(24.dp))
            } else {
                Text(
                    text = "SECURE MY PLACE IN QUEUE",
                    color = if (isValidEmail) Color.Black else Color.Gray,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.sp
                )
            }
        }
    }
}