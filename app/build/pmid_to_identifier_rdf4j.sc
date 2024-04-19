// Ammonite 2.5.2, scala 2.13
// JAVA_OPTS="-Xmx16g -Xms16g" amm app/build/pmid_to_identifier.sc pmid_identifiers.tsv data-test/pc_reference_identifier_000001.ttl.gz

import $ivy.`org.eclipse.rdf4j:rdf4j-storage:4.3.11`

import java.io._
import java.nio.file.{Files, Paths}
import java.util.zip.GZIPInputStream
import scala.util.{Try,Success,Failure}

import scala.concurrent._
import scala.concurrent.duration._

import java.io.InputStream
import java.net.URI
import org.eclipse.rdf4j.model.Statement
import org.eclipse.rdf4j.rio.RDFFormat
import org.eclipse.rdf4j.rio.Rio
import org.eclipse.rdf4j.query._;

def uncompressed(infile: String): InputStream = {
  new GZIPInputStream(new FileInputStream(new File(infile)))
}

//https://rdf4j.org/documentation/programming/rio/
@main
def main(outfile : String,pc_reference_identifier_files : String*) : Unit = {


    if (new File(outfile).exists()) {
      System.err.println(s"$outfile exists !")
      new File(outfile).delete()
    }

    /* to avoid error read from reference */
    System.setProperty("org.eclipse.rdf4j.rio.verify_uri_syntax","false")

    val fileWriter = new FileWriter(new File(outfile))

    pc_reference_identifier_files.foreach  {
        case (filePath : String) => {
            println(s"---  $filePath --- ")
           val is : InputStream = if (filePath.endsWith(".gz")) {
              println(" -- gunzip -- ")
              uncompressed(filePath)
            } else {
              new FileInputStream(filePath)
            }
         
        val baseURI: String = new File(filePath).toURI.toString
        val format: RDFFormat = RDFFormat.TURTLE

        try {
          val res: GraphQueryResult = QueryResults.parseGraphBackground(is, baseURI, format,null)
          try {
            while (res.hasNext()) {
              val st: Statement = res.next()
             
              val objUri = st.getObject().toString()
              if (objUri.contains("pubmed.ncbi.nlm.nih.gov") && !objUri.contains("PMC")) {
                val sub = st.getSubject().toString().split("/").last.trim
                val obj = objUri.split("/").last.trim
                fileWriter.write(sub+"\t"+obj+"\n")
              }
             
            }
          } finally {
            res.close()
          }
        } catch {
          case e: Exception =>
            // Gérer l'erreur irrécupérable ici
        } finally {
          is.close()
        }
        }

    }
    fileWriter.close()
}
