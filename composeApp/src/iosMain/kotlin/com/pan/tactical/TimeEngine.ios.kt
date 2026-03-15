package com.pan.tactical

import platform.Foundation.NSDate
import platform.Foundation.timeIntervalSince1970

actual fun getCurrentTimeMs(): Long = (NSDate().timeIntervalSince1970 * 1000).toLong()