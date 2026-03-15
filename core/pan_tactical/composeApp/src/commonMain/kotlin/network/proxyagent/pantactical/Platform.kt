package network.proxyagent.pantactical

interface Platform {
    val name: String
}

expect fun getPlatform(): Platform