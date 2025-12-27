"""Java application monitoring tools via JMX.

Tools:
- java_get_heap_usage: Get JVM heap memory usage
- java_get_thread_dump: Generate thread dump
- java_get_gc_stats: Get garbage collection statistics
- java_list_mbeans: List available MBeans
"""

JAVA_TOOLS = [
    "java_get_heap_usage",
    "java_get_thread_dump",
    "java_get_gc_stats",
    "java_list_mbeans",
]

__all__ = ["JAVA_TOOLS"]
