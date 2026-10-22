# realm-jvm-logs

A JVM application's logs and stack traces, read to the code that failed. Nothing is ingested.

- **Logs**: every file under the world's `data/logs` (`*.log`, `*.out`, `*.txt`) is read live, one
  row per event (`LogEvent`): timestamp, level, a `severity` on one scale, thread, logger, message,
  and — for an event that logged an exception — the exception, its causes, its root cause and a
  `fingerprint` shared by every event with the same failure at the same frames. Spring Boot,
  Logback/Log4j, java.util.logging and a program's bare stderr are read as they are.
- **Stack traces**: any Java trace — pasted (`MATCH (t:StackTrace {text: $trace})`) or logged — is
  parsed into its throwables (`JavaThrowable`: thrown, causes, suppressed) and frames
  (`JavaStackFrame`). Each frame finds the jar under `data/jars` that compiled its class.
- **To the code**, through realm-java-code and realm-java-source-code: a frame's type (IN_TYPE), the
  method's whole declaration (DECLARED_AT), the lines it was on (SOURCE_AT) and the method's locals
  (HAS_LOCAL). JDK and unmounted library frames are kept, with no jar.

## Views

| view | question |
|---|---|
| `JvmStackTraceCode` | the offending code for this stack trace |
| `JvmStackTraceSummary` | what this trace says, throwable by throwable, with the code at each one's first frame in your jars |
| `JvmLogFailures` | which failures the logs recorded, how often, first and last seen |
| `JvmLogFailureCode` | the root cause and code behind each logged failure (or one fingerprint) |
| `JvmLogLevels` | events by severity and logger, and how many carried a trace |

## Requires

realm-java-code and realm-java-source-code; the appliance's `stacktrace` producer kind and the
`files` producer's `unit: event`. Put the application's jars under `data/jars` (with their
`-sources.jar` beside them, or a source root realm-java-source-code reads) and its logs under
`data/logs`.

The `stacktrace` producer and `unit: event` arrive with embabel/me#2995 (contract: realm-spec#141).
