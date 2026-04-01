package com.pan.tactical.ui

import androidx.compose.runtime.Composable

// 🛡️ This tells the shared app: "Trust me, the platform folders will build this screen."
@Composable
expect fun AgentDashboardScreen(apiClient: WalletNetworkClient)