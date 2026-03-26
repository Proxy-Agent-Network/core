package com.pan.tactical

import android.app.Application

class PanApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        instance = this
    }

    companion object {
        lateinit var instance: PanApplication
            private set
    }
}