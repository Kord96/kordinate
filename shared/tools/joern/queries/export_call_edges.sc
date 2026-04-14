def encode(value: String): String = {
  Option(value)
    .getOrElse("")
    .replace("\\", "\\\\")
    .replace("\t", "\\t")
    .replace("\n", "\\n")
    .replace("\r", "\\r")
}

@main def exec(cpgFile: String) = {
  importCpg(cpgFile)
  cpg.method.l.foreach { method =>
    method.callOut.l.foreach { call =>
      val callerFile = method.file.name.headOption.getOrElse("")
      val callFile = call.file.name.headOption.getOrElse("")
      val row = Seq(
        encode(method.name),
        encode(method.fullName),
        encode(method.signature),
        encode(callerFile),
        method.lineNumber.getOrElse(-1).toString,
        encode(call.name),
        encode(call.methodFullName),
        encode(call.signature),
        encode(call.code),
        encode(call.dispatchType),
        encode(callFile),
        call.lineNumber.getOrElse(-1).toString,
        call.columnNumber.getOrElse(-1).toString
      ).mkString("\t")
      println(row)
    }
  }
}
