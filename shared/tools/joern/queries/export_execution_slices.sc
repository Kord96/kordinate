def encode(value: String): String = {
  Option(value)
    .getOrElse("")
    .replace("\\", "\\\\")
    .replace("\t", "\\t")
    .replace("\n", "\\n")
    .replace("\r", "\\r")
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
    val ownerFile = method.file.name.headOption.getOrElse("")
    val calls = method.callOut.l
      .filter { call =>
        val target = Option(call.methodFullName).getOrElse("")
        val targetName = Option(call.name).getOrElse("")
        !ignorable(method.name) && !ignorable(target) && !ignorable(targetName)
      }
      .sortBy(_.lineNumber.getOrElse(Int.MaxValue))
    if (calls.nonEmpty) {
      calls.zipWithIndex.foreach { case (call, idx) =>
        val row = Seq(
          encode(method.name),
          encode(method.fullName),
          encode(ownerFile),
          method.lineNumber.getOrElse(-1).toString,
          idx.toString,
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
