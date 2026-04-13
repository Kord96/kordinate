def encode(value: String): String = {
  Option(value)
    .getOrElse("")
    .replace("\\", "\\\\")
    .replace("\t", "\\t")
    .replace("\n", "\\n")
    .replace("\r", "\\r")
}

def touchKind(raw: String): String = {
  val value = Option(raw).getOrElse("").toLowerCase
  if (
    value.contains("insert") || value.contains("create") || value.contains("save") ||
    value.contains("write") || value.contains("update") || value.contains("delete") ||
    value.contains("remove") || value.contains("set")
  ) "write"
  else if (
    value.contains("find") || value.contains("get") || value.contains("list") ||
    value.contains("load") || value.contains("fetch") || value.contains("query") ||
    value.contains("select") || value.contains("read") || value.contains("scan")
  ) "read"
  else if (
    value.contains("publish") || value.contains("emit") || value.contains("send") ||
    value.contains("enqueue") || value.contains("dispatch")
  ) "emit"
  else ""
}

def ignorable(value: String): Boolean = {
  val normalized = Option(value).getOrElse("")
  normalized.isEmpty ||
  normalized.startsWith("<operator>.") ||
  normalized.startsWith("__ecma.") ||
  normalized == ":program"
}

@main def exec() = {
  cpg.method.l.foreach { method =>
    if (!ignorable(method.name)) {
      method.callOut.l.foreach { call =>
        val target = Option(call.methodFullName).getOrElse("")
        val targetName = Option(call.name).getOrElse("")
        if (!ignorable(target) && !ignorable(targetName)) {
      val combined = Seq(call.methodFullName, call.name, call.code).mkString(" ")
      val kind = touchKind(combined)
      if (kind != "") {
        val ownerFile = method.file.name.headOption.getOrElse("")
        val row = Seq(
          encode(method.name),
          encode(method.fullName),
          encode(ownerFile),
          method.lineNumber.getOrElse(-1).toString,
          kind,
          encode(call.name),
          encode(call.methodFullName),
          encode(call.code),
          call.lineNumber.getOrElse(-1).toString,
          call.columnNumber.getOrElse(-1).toString
        ).mkString("\t")
        println(row)
      }
        }
      }
    }
  }
}
